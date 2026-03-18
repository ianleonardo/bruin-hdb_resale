/* @bruin
name: sggovdata.prices_by_town
type: bq.sql
materialization:
  type: view
depends:
  - sggovdata.resale_flat_price_enriched
@bruin */

SELECT
    town,
    flat_type,
    flat_model,
    AVG(floor_area_sqm)  AS avg_floor_area_sqm,
    AVG(resale_price)    AS avg_resale_price,
    AVG(price_per_sqm)   AS avg_price_per_sqm
FROM sggovdata.resale_flat_price_enriched
GROUP BY town, flat_type, flat_model
