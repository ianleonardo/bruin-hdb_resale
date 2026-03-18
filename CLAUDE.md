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

# Run only quality checks (no ingestion)
bruin run hdb-pipeline/ --only checks

# Run a single asset with full refresh (replaces table)
bruin run hdb-pipeline/assets/<asset_name>.sql --full-refresh
```

## Architecture

### Pipeline Structure

- **`.bruin.yml`** — Top-level Bruin config. Defines named connections (GCP/BigQuery, GCS). Gitignored so credentials don't leak.
- **`hdb-pipeline/pipeline.yml`** — Pipeline definition (name, schedule, start date, default connections).
- **`hdb-pipeline/assets/`** — All pipeline assets:
  - `download_to_gcs.py` — Python asset: downloads CSV from data.gov.sg → uploads to GCS
  - `resale_flat_price.asset.yml` — Ingestr asset: GCS → BigQuery (`sggovdata.resale_flat_price`)
  - `resale_flat_price_enriched.sql` — View: parsed dates, price_per_sqm derived column
  - `prices_by_town.sql` — View: aggregated averages grouped by town, flat_type, flat_model

### Connections (`.bruin.yml`)

- **GCP/BigQuery** — project `ntu-dsai-488112`, region `asia-southeast1`, uses ADC (`gcloud auth application-default login`)
- **GCS** — bucket `dsai-m2-bucket`, service account key at `/Users/ian/Documents/Keys/ntu-dsai-gcs-user.json`
- **data.gov.sg API key** — set `DATAGOVSG_API_KEY` in `.env` at project root

### Data Flow

```
data.gov.sg API
    ↓ download_to_gcs.py
GCS (dsai-m2-bucket/datagovsg/*.csv)
    ↓ resale_flat_price.asset.yml  (ingestr, replace strategy)
sggovdata.resale_flat_price        (raw BigQuery table)
    ↓ resale_flat_price_enriched.sql
sggovdata.resale_flat_price_enriched  (view: parsed dates, price_per_sqm)
    ↓ prices_by_town.sql
sggovdata.prices_by_town              (view: averages by town/flat_type/flat_model)
```

### Key Notes

- `resale_flat_price` uses `incremental_strategy: replace` — each run fully replaces the table to avoid duplicates
- Pattern check on `month` uses SQL `LIKE` syntax (`____-__`), not regex — Bruin uses LIKE for BigQuery pattern checks
- GCS ingestr `source_table` must be the path within the bucket only (no bucket name prefix), since Bruin puts the bucket name in the source URI from the connection config

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
