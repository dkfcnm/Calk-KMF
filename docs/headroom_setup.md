# Headroom — Настройка и использование в проекте Calk_KMF

**Headroom** — слой оптимизации контекста для LLM-приложений. Сжимает выходные данные инструментов, логи, файлы и RAG-чанки перед отправкой в LLM. Экономия: 60–95% токенов.

---

## Установка

### Python (уже установлено)
```bash
pip install headroom-ai
```

### Node.js / npm (уже установлено)
```bash
npm install -g headroom-ai
```

**Версия:** 0.23.0 (Python + npm)

---

## Автозапуск с PostgreSQL

### Git Bash (рекомендуется)

```bash
# Запуск всей инфраструктуры
bash bat/DB_Start.sh

# Остановка всей инфраструктуры
bash bat/DB_Stop.sh
```

### Windows Explorer (double-click)

```
bat\DB_Start.bat   # Запуск PostgreSQL + Headroom Proxy
bat\DB_Stop.bat    # Остановка PostgreSQL + Headroom Proxy
```

**Проверено:**
- ✅ PostgreSQL запускается/останавливается
- ✅ Headroom proxy запускается/останавливается
- ✅ Proxy стартует с Memory: ENABLED
- ✅ DB создаётся автоматически
- ✅ Данные сохраняются после остановки proxy
- ✅ При перезапуске подхватывается существующая БД

---

## MCP Интеграция (Kimi Code CLI)

Headroom MCP сервер добавлен в `.roo/mcp.json`:

```json
{
  "mcpServers": {
    "headroom": {
      "command": "headroom",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Доступные MCP инструменты

| Инструмент | Описание |
|-----------|----------|
| `headroom_compress` | Сжать контент (текст, JSON, логи). Возвращает hash для retrieval |
| `headroom_retrieve` | Извлечь оригинальный контент по hash |
| `headroom_stats` | Статистика сжатия за сессию |

---

## Режимы использования

### 1. Proxy с памятью (рекомендуется)

```bash
# Запуск proxy с памятью и AST-оптимизацией
headroom proxy \
  --port 8788 \
  --memory \
  --memory-storage=project \
  --code-aware \
  --memory-db-path .headroom/memory.db \
  --log-file .headroom/logs/proxy.log
```

**Windows batch:** `bat/Headroom_Proxy_Start.bat`

**Проверено:**
- ✅ Proxy запускается с `Memory: ENABLED`
- ✅ Memory DB создаётся в `.headroom/memory.db`
- ✅ Данные сохраняются после остановки proxy
- ✅ При перезапуске proxy подхватывает существующую БД

```bash
# Использование с Claude Code
ANTHROPIC_BASE_URL=http://127.0.0.1:8788 claude

# Использование с OpenAI
OPENAI_BASE_URL=http://127.0.0.1:8788/v1 your-app
```

### 2. Python Library

```python
from headroom import compress

messages = [
    {'role': 'assistant', 'content': large_json_output}
]

result = compress(messages, model='gpt-4o-mini')
print(f'Saved {result.tokens_saved} tokens ({result.compression_ratio:.1%})')
```

**Ограничение:** `compress()` может зависать без полной установки `[all]`. Рекомендуется использовать proxy или MCP.

### 3. CLI Tools

```bash
# Структурный diff (понимает синтаксис)
headroom diff old.py new.py

# Анализ строк кода
headroom loc --exclude-dir node_modules,.git

# Поиск по AST
headroom sg -p 'def $FUNC():' -l python

# Статистика proxy
headroom perf --hours 24

# Управление памятью
headroom memory list --db-path .headroom/memory.db
headroom memory stats --db-path .headroom/memory.db
headroom memory export --output memories.json
```

---

## Компрессоры

| Компрессор | Тип контента | Экономия |
|-----------|-------------|----------|
| SmartCrusher | JSON | ~70-90% |
| CodeCompressor | Исходный код (AST) | ~50-70% |
| Kompress-base | Текст/проза | ~40-60% |

---

## Memory (кросс-агентная память)

### Работа с памятью

Headroom memory хранит извлечённые паттерны, ошибки и предпочтения в SQLite.

```bash
# Просмотр воспоминаний
headroom memory list --db-path .headroom/memory.db

# Поиск по содержимому
headroom memory search "optimization" --db-path .headroom/memory.db

# Экспорт
headroom memory export --output .headroom/memories_backup.json

# Импорт
headroom memory import .headroom/memories_backup.json
```

**Формат БД:** SQLite (`memories` таблица + FTS5 для полнотекстового поиска)

**Важно:** Memories создаются автоматически при прохождении LLM-запросов через proxy. Ручная вставка в SQLite возможна, но требует соблюдения формата и синхронизации FTS-индекса.

---

## Learn (извлечение уроков)

```bash
# Анализ прошлых сессий (требует API key)
export ANTHROPIC_API_KEY=sk-ant-...
headroom learn --project /e/Project/Calk_KMF --apply
```

Результат: автоматическое обогащение `AGENTS.md`, `.cursor/rules`, `MEMORY.md`.

---

## Полезные команды для проекта Calk_KMF

```bash
# Статистика проекта
headroom loc --exclude-dir node_modules,.git,__pycache__,build

# Сравнение файлов
headroom diff api/app/routers/refs.py api/app/routers/refs.py.bak

# Поиск паттернов в коде
headroom sg -p 'class $NAME:' -l python

# Запуск proxy с проектными настройками
headroom proxy --port 8788 --memory --code-aware \
  --memory-db-path .headroom/memory.db \
  --log-file .headroom/logs/proxy.log
```

---

## Структура .headroom/

```
.headroom/
├── memory.db              # SQLite: кросс-агентная память
├── memory_graph.db        # Neo4j-style graph (опционально)
├── memory_vectors.db      # Векторное хранилище
├── logs/
│   └── proxy.log          # Логи proxy
└── memories/              # Дополнительные хранилища
```

---

## Ограничения

- **Python 3.14:** headroom-ai установлен из готового wheel (`cp314`), но некоторые опциональные Rust-зависимости могут требовать Python ≤3.13
- **API key для learn:** `headroom learn` требует ANTHROPIC_API_KEY, OPENAI_API_KEY или GEMINI_API_KEY
- **Compress в Python:** может зависать без `[all]` extras; используйте proxy или MCP
- **Memory CLI:** `headroom memory list` по умолчанию ищет в `~/.headroom/memory.db`. Для project-mode используйте `--db-path .headroom/memory.db`

---

## Тестирование

### Proxy + Memory

```bash
# 1. Запуск
headroom proxy --port 8788 --memory --memory-storage=project \
  --memory-db-path .headroom/memory.db

# 2. Проверка health
curl http://127.0.0.1:8788/livez

# 3. Проверка stats
curl http://127.0.0.1:8788/stats

# 4. Остановка (Ctrl+C или kill)

# 5. Проверка сохранения данных
headroom memory stats --db-path .headroom/memory.db
```

---

## Ссылки

- [GitHub](https://github.com/chopratejas/headroom)
- [Документация](https://headroom-docs.vercel.app/docs)
- [llms.txt](https://headroom-docs.vercel.app/llms.txt)
