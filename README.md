# 🦊 Kitsune — The Code Knowledge Engine for AI Agents

> **Kitsune reads a whole codebase, or a whole system of services, and builds a map of how
> everything connects. People and AI agents then ask questions and get answers that point
> to the exact code they come from.**

Most "AI over code" tools cut files into 50-line pieces and search the text. Kitsune parses
whole functions, works out who really calls whom, links services across repositories, and
answers from that map, with file and line for every claim.

📘 **New here?** Read the full guide: **[docs/guide.md](docs/guide.md)** (architecture with
diagrams, results, and why it is named Kitsune).

---

## ✨ What it does

| Ordinary approach | What goes wrong | What Kitsune does instead |
|---|---|---|
| Cuts files every N lines | A function is split in half and the AI guesses the rest | Cuts at **real boundaries**: whole functions, methods, classes (tree-sitter, 8 languages) |
| Searches text only | It finds `checkout()` but not the `charge()` it calls | Builds a **graph** of calls and inheritance, resolved through types, imports and dependency injection |
| Looks at one repo | It can't see that the Go gateway calls the Java orders service | **Links services** across repos by their HTTP, gRPC and queue contracts |
| Guesses when unsure | Confident, wrong answers | Marks links **confirmed** or **possible**, and lists its **blind spots** |

**It answers questions like:** "Where is X?", "What calls X?", "What breaks if I change X?",
"How does payment work?", "Which services depend on cart?"

### 🤖 Agents built on top

| Agent | What it does |
|---|---|
| **Investigator** (`agents/investigator.py`) | Takes a bug report, searches the knowledge graph, returns root cause, location, proposed fix and impact |
| **Fix Planner** (`agents/planner.py`) | Turns the root cause into a fix proposal for a pull request. It never writes to source files; a human reviews it |

Kitsune is also the code-context layer for **ArchFox**, a PR reviewer whose review agents
and judge get their context from it.

---

## 📊 Results at a glance

Every number was measured, with the correct answers written by hand before Kitsune ran.
Details: [docs/guide.md § Proven results](docs/guide.md#9-proven-results).

| Test | Result |
|---|---|
| Cross-service links on 6 public microservice systems (incl. Train Ticket, 47 services) | **100% precision on all 6**, 100% recall on 5 (PiggyMetrics 60%) |
| Wrong links to services that must not be connected | **0** |
| Right code found, 44 questions on Kitsune's own code | **97.5%** (90% in the top 3) |
| "What calls / what does X call" | **100% / 100%** precision and recall |
| Question type recognised by the router | **100%** (97% on reworded questions) |
| Indexing speed | ~1,200 chunks (Sock Shop, 8 services) in ~110 s on a 4-core laptop CPU |

Reports: [Train Ticket](docs/reports/train-ticket.md) · [Benchmark v2 (Gson, PetClinic)](docs/reports/benchmark-v2.md)

---

## 🚀 Quick start

### 1. Install

The repository root *is* the `kitsune` package, so clone it into a folder named `kitsune`
and run Python from the folder that contains it:

```bash
git clone https://github.com/SayantanBong007/Kitsune.git kitsune
pip install -r kitsune/requirements.txt
```

Or install it as a package, which also gives you the `kitsune` command:

```bash
pip install ./kitsune                 # add [languages] for Kotlin, C# and PHP
```

### 2. Add an LLM key

```bash
cd kitsune
cp .env.example .env
```

Open `.env` and set your Groq key (free at [console.groq.com](https://console.groq.com)).
That's the only required setting:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Index and ask (Python)

```python
from kitsune.engine import RepositoryKnowledgeEngine

engine = RepositoryKnowledgeEngine(namespace="payments")

engine.index_repository("/path/to/your/repo")          # incremental after the first run
print(engine.ask("How does the authentication system work?"))

context = engine.search_semantic("What does the payment flow look like?")   # context for your own agent
impact = engine.get_impact_analysis("process_payment", max_depth=3)
print(f"This change impacts {impact['total_impact']} functions")
```

### 4. Or use the command line

```bash
kitsune index ./payments-api -n payments                 # one repository
kitsune ask "What breaks if I change process_payment?" -n payments
kitsune callers charge -n payments --depth 3

kitsune index-system ./shop -n shop                      # many services: index and link them
kitsune map -n shop                                      # which service calls which
kitsune links --service cart --direction in -n shop      # who depends on cart
kitsune callers OrderServiceImpl.create --cross-service -n shop   # follow HTTP/gRPC/queues too
kitsune endpoint /api/orders --method POST -n shop       # every caller of an endpoint
kitsune blind-spots -n shop                              # what it could not connect
kitsune teach host basket-api cart -n shop               # teach once, remembered for the team
kitsune age -n shop                                      # tails, lessons and habits
```

Every command takes `--namespace/-n`, `--json` and `--data-dir` (default `~/.kitsune/data`).
`python -m kitsune ...` works too. *Windows Git Bash rewrites arguments that start with `/`;
use PowerShell, or set `MSYS_NO_PATHCONV=1`.*

More API examples (graph queries, concepts, service maps, the lore):
[docs/guide.md § Using it](docs/guide.md#11-using-it) and
[docs/architecture.md § Integration API](docs/architecture.md).

---

## ⚙️ Configuration

All settings are environment variables (copy `.env.example` to `.env`). **Only
`GROQ_API_KEY` is required.**

### LLM

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | **Required.** API key for the LLM |
| `LLM_MODEL` | `openai/gpt-oss-20b` | Model to use |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Any OpenAI-compatible endpoint (OpenAI, OpenRouter, Ollama) |
| `LLM_API_KEY` | — | Alternative key; takes precedence over `GROQ_API_KEY` |
| `LLM_REASONING_EFFORT` | `low` for reasoning models | `low` / `medium` / `high` / `none`. Only sent to models that accept it (gpt-oss, o-series, gpt-5) unless set explicitly |
| `KITSUNE_NAMESPACE` | — | Project name; keeps projects apart on shared servers. Same as `RepositoryKnowledgeEngine(namespace=...)` |
| `KITSUNE_CONTEXT_BUDGET` | `10000` | Max characters of code context per question |

```env
# OpenAI
LLM_BASE_URL=https://api.openai.com/v1
GROQ_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini

# OpenRouter
LLM_BASE_URL=https://openrouter.ai/api/v1
GROQ_API_KEY=your-openrouter-key
LLM_MODEL=anthropic/claude-3.5-sonnet

# Ollama (local, fully offline)
LLM_BASE_URL=http://localhost:11434/v1
GROQ_API_KEY=ollama
LLM_MODEL=llama3.1:8b
```

### Storage (all optional)

Without any settings Kitsune runs on a laptop with **ChromaDB** (vectors) and **NetworkX**
(graph, saved to disk). Point it at **Qdrant** and **Neo4j** for a team.

| Variable | Default | Description |
|---|---|---|
| `QDRANT_URL` | — | Qdrant server URL (switches vectors to Qdrant) |
| `QDRANT_API_KEY` | — | API key for Qdrant |
| `QDRANT_LOCAL_PATH` | — | Embedded Qdrant, no server |
| `CHROMA_PATH` | `./data/kitsune/chroma` | ChromaDB path (default backend) |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j URI (switches the graph to Neo4j) |
| `NEO4J_USER` | `neo4j` | Neo4j user |
| `NEO4J_PASSWORD` | `kitsune_password` | Neo4j password |

### Embeddings (optional)

Kitsune embeds code locally with **BAAI/bge-small-en-v1.5** (384-dim, ~120 MB, CPU). No API key.

| Variable | Default | Description |
|---|---|---|
| `HF_HUB_OFFLINE` / `TRANSFORMERS_OFFLINE` | — | Set to `1` to use only the cached model |
| `KITSUNE_EMBED_MAX_TOKENS` | model limit (512) | Embed only the first N tokens of each chunk. `256` indexed 32% faster on CPU with the same eval scores |

### Team setup (shared servers)

Start both servers with the included [docker-compose.yml](docker-compose.yml):

```bash
docker compose up -d
```

It gives both servers **named volumes** and **`restart: unless-stopped`**. Plain
`docker run` without volumes loses every index when Docker Desktop restarts or cleans up
containers; this happened twice while testing Kitsune.

With `QDRANT_URL` and `NEO4J_URI` pointing at shared servers, the whole team works on **one**
knowledge base:

| What | Where it lives on a team setup |
|---|---|
| Code vectors | Qdrant (one collection per namespace) |
| Keyword (BM25) index | Qdrant, collection `<namespace collection>_bm25`. `KITSUNE_KEYWORD_STORE=local` forces a local file |
| Graph + cross-service links | Neo4j (nodes tagged with the namespace) |
| Lore (lessons, habits) | Neo4j node `:KitsuneLore`; concurrent saves are merged. `KITSUNE_LORE=<file>` forces a local file |

**Security checklist**
- **Qdrant:** start the server with `QDRANT__SERVICE__API_KEY=<secret>` and give clients `QDRANT_API_KEY=<secret>`. Use `https://` across machines.
- **Neo4j:** set a strong `NEO4J_AUTH=neo4j/<password>` on the server, matching `NEO4J_PASSWORD` on clients. Use `neo4j+s://` (TLS) across machines.
- **`KITSUNE_REQUIRE_SERVERS=1`:** stop with an error if Qdrant or Neo4j can't be reached, instead of quietly falling back to private local stores and splitting the team.
- **Secrets:** keep keys in `.env` (git-ignored).
- **Privacy:** code is embedded locally. Only the question and the selected code go to the LLM; use Ollama to keep everything on your machines.

---

## 💻 Supported languages

| Language | Extensions | | Language | Extensions |
|---|---|---|---|---|
| Python | `.py` | | C | `.c`, `.h` |
| JavaScript | `.js`, `.jsx` | | C++ | `.cpp`, `.hpp`, `.cc` |
| TypeScript | `.ts`, `.tsx` | | Go | `.go` |
| Java | `.java` | | Rust | `.rs` |

**Optional** (loaded when the grammar is installed: `pip install tree-sitter-kotlin
tree-sitter-c-sharp tree-sitter-php`): Kotlin `.kt`/`.kts`, C# `.cs`, PHP `.php`.

---

## 📁 Project structure

```
kitsune/
├── README.md                  ← you are here
├── docs/                      ← guide, architecture, reports (see below)
├── engine/knowledge_engine.py ← RepositoryKnowledgeEngine: the single entry point
├── indexer.py                 ← parallel, incremental indexing
├── cli.py                     ← the `kitsune` command
├── llm.py                     ← LLM client and model settings
├── parser/                    ← tree-sitter parsing, chunking, call extraction
├── embedder/                  ← embeddings, context notes, cross-encoder reranker
├── store/                     ← vector, graph and keyword stores (server + local versions)
├── graph/                     ← call resolver, library catalog, multi-hop traversal
├── services/                  ← multi-service: discovery, contracts, linker, lore
├── query/                     ← router, cache, hybrid search, context budget, synthesizer
├── concepts/                  ← business concepts (Payment, Auth…) with risk scores
├── agents/                    ← investigator (bug → root cause), planner (root cause → fix)
├── models/                    ← Chunk, Concept, metrics
├── eval/                      ← quality evaluations and benchmarks
├── tests/                     ← unit and integration tests
└── docker-compose.yml         ← Qdrant + Neo4j for a team
```

---

## 📚 Documentation

| Document | Read it for |
|---|---|
| **[Guide](docs/guide.md)** | Start here: the problem, architecture with diagrams, how indexing and answering work, many services, the lore, results, limits |
| [Architecture deep dive](docs/architecture.md) | Pipelines, storage, scalability, security and the integration API in detail |
| [Architect Q&A](docs/architect-qa.md) | Dependency injection, annotations, external libraries and multi-repo, with examples and limits |
| [Multi-service design](docs/design/multi-service.md) | The original design proposal for cross-service linking |
| [Train Ticket report](docs/reports/train-ticket.md) | Blind test on a 47-service system, with graph images |
| [Benchmark v2 report](docs/reports/benchmark-v2.md) | Retrieval benchmark on Gson and Spring PetClinic |

---

## 🧪 Evaluations and tests

Kitsune is built eval-first: every change is scored against hand-written ground truth and a
saved baseline.

```bash
python kitsune/eval/run_eval.py              # one repo, 44 questions (retrieval, call graph, router, concepts)
python kitsune/eval/fetch_external.py        # download the public systems at pinned commits
python kitsune/eval/run_system_eval.py -v    # many services: link precision and recall
python kitsune/eval/eval_v2.py gson --index  # benchmark v2 (add --answers for end-to-end LLM answers)
```

Offline unit tests (a fake embedder replaces the models, so nothing is downloaded):

```bash
pip install pytest
python -m pytest tests -q
```

Integration tests against live Qdrant + Neo4j. They clear the default (no-namespace)
project on those servers, so they're opt-in; other namespaces are left alone:

```bash
docker compose up -d
KITSUNE_INTEGRATION=1 python -m pytest tests/test_integration.py -q
```

---

*Kitsune: in Japanese folklore, a fox spirit that grows a new tail as it grows wiser.
This one grows tails as its lore grows, up to 9.*
