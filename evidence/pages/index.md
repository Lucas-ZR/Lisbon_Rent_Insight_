---
title: Test
---

```sql first_50
select
    *
from raw_listings
LIMIT 50
```

<DataTable data={first_50} />

```sql listings_by_freguesia
select
    *
from cleaned_listings
```
<AreaMap
    data={listings_by_freguesia}
    areaCol=geoJSON
    geoJsonUrl='/freguesias.geojson'
    geoId=NOME
    value=listings_count
    valueFmt=num0
    height=400
    basemap={`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png`}
    startingLat=38.7223
    startingLong=-9.1393
    startingZoom=12
/>