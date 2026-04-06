What is RockLens

A production-grade data analytics and ML pipeline

Built on a classic rock radio dataset (song, artist, year, play count). Designed as a reference architecture — showing how a Python data project should be structured at senior level, from raw SQL to trained ML models to exported charts.

Source files

27

Tests passing

68 / 68

ML model fits

330+

DB dialects

3

Pipeline flow

config.yaml
→
Registry
→
Adapter
→
Analysis
→
ML
→
Export
Each stage is timed, independently skippable, and captured in a PipelineResult. Failures either abort (fail_fast=true) or are recorded and skipped (fail_fast=false).

All files

config.yaml
Single source of truth — all settings, one file
main.py
Thin CLI — parses flags, calls Pipeline, exits
src/config.py
Typed dataclass config loader, reads config.yaml
src/logger.py
Structured logging — timestamps, levels, file + console
src/registry.py
Maps dialect name → adapter class at runtime
src/pipeline.py
Orchestrates all stages, tracks timing and errors
src/adapters/base.py
Abstract base — every adapter must implement this contract
src/adapters/sqlite.py
SQLite — retry logic, WAL mode, schema introspection
src/adapters/postgres.py
PostgreSQL — INFORMATION_SCHEMA, retry backoff
src/adapters/mysql.py
MySQL / MariaDB — SHOW TABLES, ping reconnect
src/analysis.py
Pure data functions — no I/O, no plotting, just DataFrames
src/queries.py
All SQL in one place — never scattered in logic
src/models.py
3 ML models — Pipeline + GridSearchCV + cross-validation
src/visualize.py
9 chart functions — save + optional display
tests/conftest.py
pytest fixtures — sample_df, tmp_db, tmp_cfg
tests/run_tests.py
Standalone runner — no pytest install needed
tests/test_config.py
Config loading, YAML overrides, env var password
tests/test_adapters.py
SQLite connect/query/execute, registry, abstract contract
tests/test_analysis.py
All analysis functions, return types, edge cases
tests/test_models.py
Feature engineering, all 3 models, error paths
tests/test_pipeline.py
Full run, stage skipping, fail-fast, CSV export
generate_test_db.py
Synthetic dataset — run offline without internet
README.md
Full docs — setup, CLI, switching DBs, architecture notes
CHANGELOG.md
Version history — v1, v2, v3 with Added/Changed/Removed
.gitignore
Excludes data/, output/, logs/, .env, .venv, __pycache__
pytest.ini
pytest config — test paths, collection rules, warning filters
requirements.txt
Dependencies — pandas, sklearn, matplotlib, seaborn, pyyaml
Three ML models

Regression
PlayCountPredictor

Predicts how many plays a song gets. LinearRegression vs Ridge vs GradientBoosting compete. Winner picked by 5-fold KFold CV on MAE.

Classification
HitClassifier

Predicts hit or not (top 33% of plays). LogisticReg vs RandomForest vs GradientBoosting. StratifiedKFold, F1 score metric.

Clustering
ArtistClusterer

Groups similar artists using KMeans. Elbow method auto-selects K. Labels clusters: Legends, High Rotation, Prolific, Deep Cuts.

Shared ML patterns in every model

sklearn Pipeline
GridSearchCV
cross-validation
engineer_features()
StandardScaler inside pipeline
LabelEncoder
predict_proba()
ml_results.json tracking
config-driven params
no data leakage
Database support

SQLite default

Built-in, no install needed. WAL mode, retry logic, PRAGMA schema introspection.

PostgreSQL

pip install psycopg2-binary. INFORMATION_SCHEMA, retry backoff, env var password.

MySQL / MariaDB

pip install pymysql. SHOW TABLES, ping reconnect, utf8mb4 charset.

To switch database — edit one line in config.yaml

dialect: sqlite
→ change to →
dialect: postgres
Zero code changes anywhere else.
CLI commands

python main.py
Full pipeline — Analysis + ML + Export
--no-show
Headless / CI mode — save charts, no popup windows
--download
Download the SQLite dataset (run once)
--check
Ping the database and list all tables
--stage ml
Run only one stage: analysis | ml | export
--list-dbs
Print all registered database dialects
--config prod.yaml
Use a different config file (dev / staging / prod)
Test coverage — 68 tests, 5 files

test_config.py — 6 tests
6 pass
test_adapters.py — 18 tests
18 pass
test_analysis.py — 21 tests
21 pass
test_models.py — 33 tests
33 pass
test_pipeline.py — 10 tests
10 pass
Total
68 / 68
python tests/run_tests.py
or with pytest:
pytest tests/ -v --cov=src
Output files generated

dashboard.png
4-panel overview
top_artists.png
Top 15 by song count
by_decade.png
Songs + avg plays per decade
most_played.png
Top 20 most-played songs
play_count_dist.png
Play count histogram
regression_*.png
Actual vs predicted scatter
confusion_matrix.png
Hit classifier results
elbow_curve.png
Optimal K selection
artist_clusters.png
Artist similarity map
ml_results.json
All scores + best hyperparams
Architecture principles

Adapter pattern

All DB-specific code is isolated in adapters/. The rest of the codebase uses BaseAdapter and never imports a concrete class. Adding a new DB = one new file, zero other changes.

Config-driven

No hardcoded values anywhere in src/. Every setting — DB path, ML params, log level, stage toggles — lives in config.yaml. Different environments use different YAML files.

Staged pipeline

Analysis → ML → Export are named stages with timing and error capture. fail_fast in config controls whether one broken stage stops everything or gets skipped.

No data leakage

sklearn Pipelines chain scaler + model together. The scaler never sees test data during training. Manual preprocessing step-by-step is the classic leakage mistake — Pipelines prevent it.

Structured logging

Every log line has a timestamp, level, and module name. Written to console and logs/rocklens.log simultaneously. Set level: WARNING in config to silence noise in production.

Single responsibility

queries.py only holds SQL. analysis.py only transforms data. visualize.py only draws charts. models.py only trains models. No file does another file's job.
