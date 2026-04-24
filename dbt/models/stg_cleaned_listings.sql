select *
from {{ source('raw', 'raw_listings') }}