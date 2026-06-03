select 
  listings.* exclude(listings.freguesia),
  map.geoJSON as geojson_name
from {{ ref('stg_cleaned_listings') }} as listings
join {{ ref("freguesia_map") }} as map
  on listings.freguesia=map.slug