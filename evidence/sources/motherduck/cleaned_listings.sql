select 
  count(listing_id) AS listings_count,
  freguesia,
  geoJSON
from lisbon_rental.main.stg_cleaned_listings as listings
join lisbon_rental.main.freguesia_map as map
on listings.freguesia=map.slug
group by freguesia, geoJSON