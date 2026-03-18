/* @bruin

name: sggovdata.resale_flat_price_enriched
type: bq.sql

materialization:
  type: view

depends:
  - sggovdata.resale_flat_price

@bruin */

SELECT
    PARSE_DATE('%Y-%m', month)                      AS date,
    EXTRACT(YEAR FROM PARSE_DATE('%Y-%m', month))   AS year,
    EXTRACT(MONTH FROM PARSE_DATE('%Y-%m', month))  AS month,
    town,
    flat_type,
    storey_range,
    flat_model,
    floor_area_sqm,
    resale_price,
    SAFE_DIVIDE(resale_price, floor_area_sqm)       AS price_per_sqm
FROM sggovdata.resale_flat_price
