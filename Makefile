.PHONY: setup lock info \
        run profile \
        test lint format typecheck security audit check \
        docs \
        init harness-check backlog \
        agents-list agents-run agents-doctor agents-memory agents-eval \
        prompts-sync prompts-check assistants-sync \
        skills opencode-check \
        index-rag index-rag-rebuild eval-rag \
        clean clean-all help

# ─────────────────────────────────────────────────────────────────────────────
#  Variables
# ─────────────────────────────────────────────────────────────────────────────
MODULE = app
PYTHON = python

# ─────────────────────────────────────────────────────────────────────────────
#  help  →  target por defecto
# ─────────────────────────────────────────────────────────────────────────────
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  MeshHarmes  ·  paquete: $(MODULE)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  Entorno"
	@echo "    make setup           instala dev + hooks de pre-commit"
	@echo "    make lock            actualiza uv.lock"
	@echo "    make info            versiones y paquetes instalados"
	@echo ""
	@echo "  Ejecución"
	@echo "    make run             ejecuta el paquete (python -m $(MODULE))"
	@echo "    make profile         cProfile de la ejecución → profile.prof"
	@echo ""
	@echo "  Calidad"
	@echo "    make check           lint + typecheck + test + arnés"
	@echo "    make test            pytest (proyecto + agentes)"
	@echo "    make lint            ruff check + format --check (no modifica)"
	@echo "    make format          ruff format (aplica cambios)"
	@echo "    make typecheck       mypy"
	@echo "    make security        bandit + pip-audit"
	@echo "    make audit           radon cc + agente audit"
	@echo ""
	@echo "  Documentación"
	@echo "    make docs            sphinx-apidoc + html"
	@echo ""
	@echo "  Arnés (harness)"
	@echo "    make init            puerta de entrada: ¿se puede trabajar? (init.sh)"
	@echo "    make harness-check   valida la estructura del arnés sin correr tests"
	@echo "    make backlog         estado de harness/featureslist.json"
	@echo ""
	@echo "  Agentes"
	@echo "    make agents-list     listar agentes disponibles"
	@echo "    make agents-run      ejecutar un agente"
	@echo "    make agents-doctor   diagnóstico completo con agentes"
	@echo "    make agents-memory   estado de la memoria de agentes"
	@echo "    make agents-eval     harness + routing + contracts + rag"
	@echo "    make prompts-sync    regenera los prompts desde el código y contracts.py"
	@echo "    make prompts-check   falla si un prompt se ha desincronizado"
	@echo "    make assistants-sync espeja los subagentes a .claude/agents/"
	@echo "    make skills          copia los prompts a .opencode/skills/"
	@echo "    make opencode-check  valida la configuración de opencode"
	@echo ""
	@echo "  RAG (extra 'rag')"
	@echo "    make index-rag       indexa código, docs y memoria del arnés"
	@echo "    make index-rag-rebuild  reconstruye el índice desde cero"
	@echo "    make eval-rag        mide la recuperación (hit_rate/recall/MRR)"
	@echo ""
	@echo "  Limpieza"
	@echo "    make clean           cachés y __pycache__"
	@echo "    make clean-all       clean + workspace de agentes + índice RAG"
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
#  Entorno
# ─────────────────────────────────────────────────────────────────────────────
setup:
	uv sync --extra dev
	@uv run pre-commit install 2>/dev/null || echo "  (pre-commit no disponible)"
	@echo ""
	@echo "  Listo. Extras opcionales:  uv sync --extra dev --extra rag --extra docs"
	@echo ""

lock:
	uv lock
	@echo "  uv.lock actualizado."

info:
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Proyecto  : MeshHarmes"
	@echo "  Paquete   : $(MODULE)"
	@echo "  Python    : $(shell uv run python --version 2>/dev/null || python --version)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@uv pip list 2>/dev/null | head -40 || pip list | head -40
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
#  Ejecución
# ─────────────────────────────────────────────────────────────────────────────
run:
	uv run $(PYTHON) -m $(MODULE) hello

profile:
	@echo "▶  Profiling → profile.prof"
	uv run $(PYTHON) -m cProfile -o profile.prof -m $(MODULE) hello
	@echo "   Visualiza con: uv run snakeviz profile.prof"

# ─────────────────────────────────────────────────────────────────────────────
#  Calidad de código
# ─────────────────────────────────────────────────────────────────────────────
test:
	uv run pytest

check: lint typecheck test harness-check
	@echo ""
	@echo "  ✅ check pasado: lint + typecheck + test + arnés OK"

lint:
	uv run ruff check $(MODULE)/ tests/ agents/
	uv run ruff format --check $(MODULE)/ tests/

format:
	uv run ruff format $(MODULE)/ tests/

typecheck:
	uv run mypy $(MODULE)/ tests/
	@echo "  ✅ typecheck OK"

security:
	uv run bandit -r $(MODULE)/ -f txt -x tests
	uv run pip-audit 2>/dev/null || echo "  (pip-audit requiere paquetes instalados — ejecuta make setup primero)"
	@echo "  ✅ security check OK"

audit:
	@echo "▶  Complejidad ciclomática (radon)"
	@uv run radon cc $(MODULE)/ -s --min C 2>/dev/null || echo "  (sin radon)"
	@echo ""
	uv run python -m agents run audit suggest 2>/dev/null || echo "  (agente 'audit' no disponible — ejecuta make setup)"
	@echo "  ✅ audit OK"

# ─────────────────────────────────────────────────────────────────────────────
#  Documentación
# ─────────────────────────────────────────────────────────────────────────────
docs:
	uv run sphinx-apidoc -o docs/source/ $(MODULE)/
	$(MAKE) html -C docs

# ─────────────────────────────────────────────────────────────────────────────
#  Arnés (harness) — el protocolo está en AGENTS.md
# ─────────────────────────────────────────────────────────────────────────────
init:
	@chmod +x init.sh 2>/dev/null || true
	@./init.sh

harness-check:
	@chmod +x init.sh 2>/dev/null || true
	@./init.sh --quick

backlog:
	@uv run $(PYTHON) -c "import json; d=json.load(open('harness/featureslist.json')); \
	print(); print('  Backlog de MeshHarmes'); print(); \
	[print('  [%-11s] %-10s %s' % (f['status'], f['id'], f['title'])) for f in d['features']]; \
	print()"

# ─────────────────────────────────────────────────────────────────────────────
#  Sistema de agentes
# ─────────────────────────────────────────────────────────────────────────────
agents-list:
	uv run python -m agents list

agents-run:
	uv run python -m agents run $(filter-out $@,$(MAKECMDGOALS))

agents-doctor:
	uv run python -m agents doctor

agents-memory:
	@echo "▶  Estado de la memoria de agentes"
	uv run python -m agents run memory status

agents-eval:
	@echo "▶  Evaluación del sistema de agentes (harness + routing + contracts + rag)"
	uv run python -m agents.evals.runner

prompts-sync assistants-sync:
	@echo "▶  Regenerando prompts y subagentes desde el código y los contratos..."
	uv run python -m agents.prompts_sync --write

prompts-check:
	@uv run python -m agents.prompts_sync

# ─────────────────────────────────────────────────────────────────────────────
#  RAG local (extra 'rag')
# ─────────────────────────────────────────────────────────────────────────────
index-rag:
	@echo "▶  Indexando código y documentación del proyecto en ChromaDB..."
	@echo "   (incremental: solo se reindexa lo que cambió)"
	uv run python -m agents run rag index

# Necesario al cambiar HARNESS_RAG_EMBEDDER: los vectores del embedder anterior
# no son comparables con los del nuevo, y mezclarlos no da error — da basura.
index-rag-rebuild:
	@echo "▶  Reconstruyendo el índice RAG desde cero..."
	uv run python -m agents run rag index --rebuild

# Mide si la búsqueda encuentra lo que debería, contra
# agents/evals/rag_golden.json. Sin esto, tocar el troceado o el embedder es
# fe: "parece que ahora busca mejor" no es un dato.
eval-rag:
	@echo "▶  Evaluando la recuperación del RAG (hit_rate / recall@k / MRR)"
	uv run python -m agents run rag evaluate

# ─────────────────────────────────────────────────────────────────────────────
#  Configuración del asistente
# ─────────────────────────────────────────────────────────────────────────────
skills:
	@echo "▶  Instalando skills del proyecto..."
	@mkdir -p .opencode/skills
	@for skill in agents/prompts/*.md; do \
		name=$$(basename "$$skill" .md); \
		cp "$$skill" ".opencode/skills/$$name.md"; \
		echo "   skill: $$name"; \
	done
	@echo "   Skills instaladas en .opencode/skills/."

opencode-check:
	@echo "▶  Verificando configuración opencode..."
	@errors=0; \
	for f in opencode.json .opencode/agents/orquestador.md; do \
		if [ ! -f "$$f" ]; then echo "  ✘ falta $$f"; errors=$$((errors + 1)); \
		else echo "  ✔ $$f"; fi; \
	done; \
	for a in lider implementer reviewer explorer; do \
		if [ ! -f ".opencode/agents/$$a.md" ]; then \
			echo "  ✘ falta .opencode/agents/$$a.md (agente del arnés)"; errors=$$((errors + 1)); \
		else echo "  ✔ .opencode/agents/$$a.md"; fi; \
	done; \
	count=$$(ls agents/prompts/*.md 2>/dev/null | wc -l); \
	echo "  ✔ $$count prompts fuente disponibles."; \
	if [ "$$errors" -eq 0 ]; then echo "  ✔ Todo correcto."; else \
		echo "  ✘ $$errors error(es) encontrados."; exit 1; fi

# ─────────────────────────────────────────────────────────────────────────────
#  Limpieza
# ─────────────────────────────────────────────────────────────────────────────
clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache docs/build profile.prof
	find $(MODULE) tests agents -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "  Cachés y __pycache__ eliminados."

clean-all: clean
	rm -rf agents/workspace/ .rag-index
	@echo "  Limpieza completa (incluye workspace de agentes e índice RAG)."
