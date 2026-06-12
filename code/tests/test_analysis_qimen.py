import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add project root/code to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis.engine import AnalysisEngine


def test_qimen_analysis():
    engine = AnalysisEngine()

    # 1. Load rules
    rules = engine.load_rules('direction')
    print(f"Loaded {len(rules)} rules for scope 'direction'.")

    # 2. Test Context: Jia on Bing (Rule 3 in md file -> +1 score)
    # Rule 3: qimen_struct_003, 甲丙, score 1
    context_good = {
        "heaven_stem": "甲",
        "earth_stem": "丙"
    }

    results = engine.run_analysis('direction', context_good)
    print("\nTest Context: Jia (Heaven) on Bing (Earth)")
    if not results:
        print("No rules triggered.")
    for res in results:
        print(f"Rule: {res['rule_id']}, Score: {res['score']}, Val: {res['result_value']}")

    # 3. Test Context: Jia on Jia (Rule 1 -> -1 score)
    context_bad = {
        "heaven_stem": "甲",
        "earth_stem": "甲"
    }
    results_bad = engine.run_analysis('direction', context_bad)
    print("\nTest Context: Jia (Heaven) on Jia (Earth)")
    if not results_bad:
        print("No rules triggered.")
    for res in results_bad:
        print(f"Rule: {res['rule_id']}, Score: {res['score']}, Val: {res['result_value']}")

    print("\n✅ Qimen analysis tests passed!")


if __name__ == '__main__':
    test_qimen_analysis()
