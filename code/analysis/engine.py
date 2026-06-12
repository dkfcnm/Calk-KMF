import json
from .predicates import registry
from code.common.db_manager import db
from code.bazi_calendar.db import get_placeholder

class AnalysisEngine:
    def __init__(self, db_path=None):
        # db_path is ignored as we use central DBManager
        self.rules_cache = {} # scope -> list of rules

    def load_rules(self, scope):
        if scope in self.rules_cache:
            return self.rules_cache[scope]

        ph = get_placeholder()
        
        # Загрузка правил, активных для данной области
        sql = f"""
        SELECT r.rule_id, r.name_ru, r.predicate_code, r.params_json, 
               r.score_base, r.score_formula, s.is_stop
        FROM t_rule_registry r
        JOIN t_rule_scope s ON r.rule_id = s.rule_id
        WHERE s.scope_type = {ph} AND r.is_active = 1
        """
        # db.fetch_all returns list of tuples if using pg8000 (DBManager implementation check needed)
        # DBManager.fetch_all uses cursor.fetchall().
        # pg8000 returns list of lists/tuples. It doesn't return dicts by default unless row_factory set?
        # DBManager in code/common/db_manager.py: 
        # def fetch_all(self, query, params=None) -> List[Tuple]: return cursor.fetchall()
        # So we need to map columns manually or update DBManager to return dicts.
        # Map columns manually since DBManager returns tuples.
        
        rows = db.fetch_all(sql, (scope,))
        
        # Map columns manually since DBManager returns tuples
        # Columns: rule_id, name_ru, predicate_code, params_json, score_base, score_formula, is_stop
        rules = []
        for row in rows:
            rules.append({
                'rule_id': row[0],
                'name_ru': row[1],
                'predicate_code': row[2],
                'params_json': row[3],
                'score_base': row[4],
                'score_formula': row[5],
                'is_stop': row[6]
            })
        
        # Parse JSON params
        for r in rules:
            if r['params_json']:
                try:
                    r['params'] = json.loads(r['params_json'])
                except:
                    r['params'] = {}
            else:
                r['params'] = {}
                
        self.rules_cache[scope] = rules
        return rules

    def evaluate_rule(self, rule, context):
        """
        Выполняет проверку правила.
        Возвращает (is_triggered, result_value, score).
        """
        predicate = registry.get(rule['predicate_code'])
        if not predicate:
            return False, f"Predicate {rule['predicate_code']} not found", 0

        try:
            result = predicate(context, rule['params'])
            # Support both (triggered, msg) and (triggered, msg, score)
            if len(result) == 3:
                is_triggered, result_msg, dynamic_score = result
            else:
                is_triggered, result_msg = result
                dynamic_score = None
        except Exception as e:
            return False, f"Error: {e}", 0

        if is_triggered:
            # Расчет оценки
            # Если предикат вернул динамическую оценку, используем её
            if dynamic_score is not None:
                score = dynamic_score
            else:
                # Иначе используем базовую оценку из правила
                score = rule['score_base']
            return True, result_msg, score
        
        return False, None, 0

    def run_analysis(self, scope, context):
        """
        Запускает анализ для заданного контекста.
        Возвращает список сработавших правил.
        """
        rules = self.load_rules(scope)
        results = []
        
        for rule in rules:
            triggered, val, score = self.evaluate_rule(rule, context)
            if triggered:
                res_item = {
                    'rule_id': rule['rule_id'],
                    'result_value': val,
                    'score': score
                }
                
                if rule['is_stop']:
                    res_item['is_stop'] = True
                    results.append(res_item)
                    break
                
                results.append(res_item)
                    
        return results

class RuleEngine(AnalysisEngine):
    """
    Optimized Engine for Walk Analysis.
    Pre-indexes rules for O(1) lookup.
    """
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.rules_generic = []
        self.rules_by_stem = {} # (heaven, earth) -> list of rules
        self.rules_by_gate = {} # gate -> list of rules
        self.rules_by_star = {} # star -> list of rules
        self._load_and_index_rules()
        
    def _load_and_index_rules(self):
        # Load rules from all relevant scopes
        # Typically 'direction' (structures) and 'date' (officers)
        # We can optimize by loading everything active
        
        sql = """
        SELECT r.rule_id, r.name_ru, r.predicate_code, r.params_json, 
               r.score_base, r.score_formula, r.description,
               s.is_stop, s.scope_type
        FROM t_rule_registry r
        JOIN t_rule_scope s ON r.rule_id = s.rule_id
        WHERE r.is_active = 1
        """
        rows = db.fetch_all(sql)
        
        rules = []
        for row in rows:
            rules.append({
                'rule_id': row[0],
                'name_ru': row[1],
                'predicate_code': row[2],
                'params_json': row[3],
                'score_base': row[4],
                'score_formula': row[5],
                'description': row[6],
                'is_stop': row[7],
                'scope_type': row[8]
            })
        
        for r in rules:
            # Parse params
            if r['params_json']:
                try:
                    r['params'] = json.loads(r['params_json'])
                except:
                    r['params'] = {}
            else:
                r['params'] = {}
                
            # Indexing
            indexed = False
            
            # Index by Stems (Structure)
            if r['predicate_code'] == 'CHECK_QIMEN_STEMS':
                h = r['params'].get('heaven')
                e = r['params'].get('earth')
                if h and e:
                    key = (h, e)
                    if key not in self.rules_by_stem:
                        self.rules_by_stem[key] = []
                    self.rules_by_stem[key].append(r)
                    indexed = True
            
            # Future: Index by Gate
            # if r['predicate_code'] == 'CHECK_QIMEN_GATE': ...
            
            if not indexed:
                self.rules_generic.append(r)
                
    def find_matches(self, context):
        """
        Find all matching rules for the given context (chart + time).
        """
        matches = []
        
        # 1. Stem Lookup (Optimized)
        h = context.get('heaven_stem')
        e = context.get('earth_stem')
        if h and e:
            candidates = self.rules_by_stem.get((h, e), [])
            for rule in candidates:
                triggered, val, score = self.evaluate_rule(rule, context)
                if triggered:
                    matches.append(self._fmt_match(rule, val, score))
                    if rule['is_stop']: return matches # Stop if blocking
        
        # 2. Gate Lookup
        g = context.get('gate')
        if g:
            candidates = self.rules_by_gate.get(g, [])
            for rule in candidates:
                triggered, val, score = self.evaluate_rule(rule, context)
                if triggered:
                    matches.append(self._fmt_match(rule, val, score))
                    if rule['is_stop']: return matches

        # 3. Star Lookup
        s = context.get('star')
        if s:
            candidates = self.rules_by_star.get(s, [])
            for rule in candidates:
                triggered, val, score = self.evaluate_rule(rule, context)
                if triggered:
                    matches.append(self._fmt_match(rule, val, score))
                    if rule['is_stop']: return matches
        
        # 4. Generic Rules (e.g. Day Officer)
        # Performance Critical: Skipped in Python loop. Should be done via SQL.
        # for rule in self.rules_generic:
        #    triggered, val, score = self.evaluate_rule(rule, context)
        #    if triggered:
        #        matches.append(self._fmt_match(rule, val, score))
        #        if rule['is_stop']: return matches
                
        return matches
        
    def _fmt_match(self, rule, val, score):
        return {
            'id': rule['rule_id'],
            'nm': rule['name_ru'],
            'des': rule['description'] or val, # Use description or result msg
            'coef': score,
            'gr': None, # Group ID not in DB currently, maybe add if needed
            'flag_stop': rule['is_stop']
        }

    def calculate_score(self, matches):
        return sum(m['coef'] for m in matches)

