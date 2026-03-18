# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a [Bruin](https://bruin-data.github.io/bruin/) data pipeline project for processing HDB (Housing Development Board) resale data from Singapore's data.gov.sg. It ingests and transforms resale flat transaction data using Google BigQuery as the data warehouse.

## Bruin CLI Commands

```bash
# Validate pipeline and assets
bruin validate hdb-pipeline/

# Run the full pipeline
bruin run hdb-pipeline/

# Run a single asset
bruin run hdb-pipeline/assets/<asset_name>.sql

# Run pipeline tests
bruin test hdb-pipeline/
```

## Architecture

### Pipeline Structure

- **`.bruin.yml`** — Top-level Bruin config. Defines named connections (GCP/BigQuery, GCS). This file is gitignored so local overrides don't leak credentials.
- **`hdb-pipeline/pipeline.yml`** — Pipeline definition (schedule, default connections, retries, concurrency).
- **`hdb-pipeline/assets/`** — SQL transformation assets. Each `.sql` file is a Bruin asset with frontmatter between `/* @bruin ... @bruin */` that declares its name, type, dependencies, and materialization strategy.

### Connections (`.bruin.yml`)

- GCP project: `ntu-dsai-488112`, region `asia-southeast1`
- GCS bucket: `dsai-m2-bucket`, path prefix: `datagovsg`
- Uses Application Default Credentials (ADC) — run `gcloud auth application-default login` if needed

### Asset Format

Bruin SQL assets use embedded YAML frontmatter:

```sql
/* @bruin
name: dataset.table_name
type: bq.sql
materialization:
   type: table
depends:
   - upstream_asset_name
@bruin */

SELECT ...
```
