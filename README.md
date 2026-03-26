# RockLens

A production-grade data analytics and ML pipeline built on a classic rock radio dataset.
Designed as a reference architecture for Python data projects — clean layering, multi-database support, full test coverage.

---

## Features

- **Multi-database pipeline** — SQLite, PostgreSQL, MySQL via a single config change
- **3 ML models** — regression, classification, clustering with GridSearchCV + cross-validation
- **Staged pipeline** — Analysis → ML → Export with per-stage timing and fail-fast support
- **Structured logging** — timestamped logs to console and file, configurable level
- **Config-driven** — all settings in `config.yaml`, no hardcoded values in code
- **68 unit tests** — covering config, adapters, analysis, models, and pipeline

---

## Quick Start

```bash
# 1. Clone and enter
git clone <repo-url>
cd rocklens

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the dataset
python main.py --download

# 5. Run the full pipeline
python main.py
```

---

## Project Structure

```
rocklens/
├── config.yaml                  # All settings — edit this to switch databases
├── main.py                      # CLI entry point (thin — delegates to pipeline)
├── generate_test_db.py          # Generate synthetic DB for offline testing
├── pytest.ini                   # pytest configuration
├── requirements.txt
│
├── src/
│   ├── config.py                # Typed config loader (reads config.yaml)
│   ├── logger.py                # Structured logging setup
│   ├── registry.py              # DB adapter registry — maps dialect → class
│   ├── pipeline.py              # Staged orchestrator (Analysis, ML, Export)
│   ├── analysis.py              # Pure data-transformation functions
│   ├── queries.py               # All SQL in one place
│   ├── models.py                # ML models (regression, classification, clustering)
│   ├── visualize.py             # Chart functions
│   │
│   └── adapters/
│       ├── base.py              # Abstract base class all adapters must implement
│       ├── sqlite.py            # SQLite adapter
│       ├── postgres.py          # PostgreSQL adapter
│       └── mysql.py             # MySQL / MariaDB adapter
│
├── tests/
│   ├── conftest.py              # pytest fixtures (sample_df, tmp_db, tmp_cfg)
│   ├── run_tests.py             # Standalone runner (no pytest install needed)
│   ├── test_config.py
│   ├── test_adapters.py
│   ├── test_analysis.py
│   ├── test_models.py
│   └── test_pipeline.py
│
├── data/                        # SQLite DB lives here (git-ignored)
├── output/                      # Generated charts + CSV exports (git-ignored)
└── logs/                        # Log files (git-ignored)
```

---

## CLI Reference

```bash
python main.py                        # Full pipeline run
python main.py --no-show              # Headless / CI mode (save charts, no popups)
python main.py --download             # Download SQLite dataset (run once)
python main.py --check                # Health-check DB connection and list tables
python main.py --stage analysis       # Run only the Analysis stage
python main.py --stage ml             # Run only the ML stage
python main.py --stage export         # Run only the Export stage
python main.py --list-dbs             # List supported database dialects
python main.py --config prod.yaml     # Use a different config file
```

---

## Switching Databases

Edit one line in `config.yaml`:

```yaml
database:
  dialect: postgres    # sqlite | postgres | mysql
```

Then fill in the credentials for that dialect in the same file.
No Python code changes needed anywhere.

**Install the driver for your database:**
```bash
pip install psycopg2-binary   # PostgreSQL
pip install pymysql            # MySQL / MariaDB
```

**PostgreSQL example:**
```yaml
database:
  dialect: postgres
  postgres:
    host: localhost
    port: 5432
    database: rocklens
    user: myuser
    password: ""              # or set ROCKLENS_DB_PASSWORD env var
```

**Adding a new database** — implement `BaseAdapter`, register it:
```python
from src.registry import register
from myproject.adapters import BigQueryAdapter
register("bigquery", BigQueryAdapter)
```

---

## ML Models

| Model | Task | Algorithm competition | Evaluation |
|---|---|---|---|
| `PlayCountPredictor` | Regression | LinearRegression vs Ridge vs GradientBoosting | KFold CV, MAE, R² |
| `HitClassifier` | Classification | LogisticRegression vs RandomForest vs GradientBoosting | StratifiedKFold CV, F1 |
| `ArtistClusterer` | Clustering | KMeans with elbow method | Inertia, auto-K selection |

All candidates compete via `GridSearchCV`. The winner is selected by CV score and stored as `best_pipeline`.
Results saved to `output/ml_results.json` after every run.

**Tune from config.yaml:**
```yaml
ml:
  cv_folds: 10              # more folds = more reliable evaluation
  hit_percentile: 0.75      # top 25% = hit
  cluster_max_k: 10         # search up to K=10 clusters
  regression:
    candidates:
      - ridge               # run only Ridge (faster)
```

---

## Running Tests

```bash
# Without pytest (works right now)
python tests/run_tests.py

# With pytest (install first)
pip install pytest pytest-cov
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=term-missing

# Single file
pytest tests/test_models.py -v
```

**Test coverage: 68 tests across 9 test classes**

| File | Tests | Covers |
|---|---|---|
| `test_config.py` | 6 | YAML loading, defaults, env var password |
| `test_adapters.py` | 18 | SQLite connect/query/execute, registry, abstract enforcement |
| `test_analysis.py` | 21 | All analysis functions, types, edge cases |
| `test_models.py` | 33 | Feature engineering, all 3 models, error handling |
| `test_pipeline.py` | 10 | Full run, stage skipping, fail-fast, exports |

---

## Output Files

After a full run, `output/` contains:

| File | Description |
|---|---|
| `dashboard.png` | 4-panel analytics overview |
| `top_artists.png` | Bar chart — top 15 artists by song count |
| `by_decade.png` | Songs released + avg plays per decade |
| `most_played.png` | Top 20 most-played songs |
| `play_count_dist.png` | Play count histogram |
| `regression_actual_vs_predicted.png` | Regression model accuracy scatter |
| `confusion_matrix.png` | Hit classifier confusion matrix |
| `elbow_curve.png` | KMeans elbow method — optimal K |
| `artist_clusters.png` | Artist similarity scatter plot |
| `ml_results.json` | All model scores and best hyperparameters |
| `summary_stats.json` | Dataset summary statistics |
| `*.csv` | Exported analysis DataFrames |

---

## Environment Variables

| Variable | Description |
|---|---|
| `ROCKLENS_DB_PASSWORD` | DB password (overrides config.yaml — use in prod) |

---

## Architecture Decisions

**Why the adapter pattern?**
All database-specific code is isolated in `src/adapters/`. The rest of the codebase uses `BaseAdapter` and never imports a specific adapter directly. Adding a new database means writing one new file — zero changes elsewhere.

**Why config.yaml instead of .env?**
`.env` files are flat key-value pairs. A YAML file supports nested structure, comments, and typed values — making it far more readable for a project with this many settings. Secrets (passwords) still use env vars as override.

**Why a Pipeline class instead of a script?**
A script is a list of commands. A Pipeline is a first-class object that can be tested, timed, retried, and reported on. Each stage's success/failure is captured in `PipelineResult` — useful for CI and monitoring.

**Why log instead of print?**
`print()` is fire-and-forget. `logging` gives timestamps, levels, module names, and file output. Set `level: WARNING` in config.yaml to silence info-level noise in production without changing any code.
