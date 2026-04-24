WITH base AS (
    SELECT
        *,
        ARRAY_TO_STRING(extra, ' ') AS extra_str
    FROM {{ source('raw', 'raw_listings') }}
)


SELECT
    id                                                           AS listing_id,
    CAST(REGEXP_REPLACE(price, '[^0-9]', '', 'g') AS INTEGER)    AS price,
    CAST(REGEXP_EXTRACT(extra_str, 'T(\d+)', 1) AS INTEGER)   AS rooms,
    CAST(REGEXP_EXTRACT(extra_str, '(\d+) m²', 1) AS INTEGER) AS sqm,
    CONTAINS(extra_str, 'Garagem')                            AS has_garage,
    CONTAINS(extra_str, 'Cave')                               AS is_cave,
    CONTAINS(extra_str, 'com elevador')                       AS has_lift,
    freguesia                                                    AS freguesia,
    EXTRACT(year FROM scraped_at)                                AS listing_year,
    EXTRACT(month FROM scraped_at)                               AS listing_month,

FROM base