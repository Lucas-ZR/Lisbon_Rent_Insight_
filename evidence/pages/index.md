# Lisbon Rental Insight

A simple project that allow you to explore [idealista](https://www.idealista.pt) rental listing across the *freguesias* (parishes) of Lisbon.

Use the filters below to narrow the listings, leave a filter on **Any** to include everything, or pick **Yes / No** to require or exclude that feature.

<ButtonGroup name=garage title="Garage">
    <ButtonGroupItem valueLabel="Any (no filter)" value="true,false" default/>
    <ButtonGroupItem valueLabel="Yes" value="true"/>
    <ButtonGroupItem valueLabel="No"  value="false"/>
</ButtonGroup>

<ButtonGroup name=lift title="Lift">
    <ButtonGroupItem valueLabel="Any (no filter)" value="true,false" default/>
    <ButtonGroupItem valueLabel="Yes" value="true"/>
    <ButtonGroupItem valueLabel="No"  value="false"/>
</ButtonGroup>

<ButtonGroup name=cave title="Basement (cave)">
    <ButtonGroupItem valueLabel="Any (no filter)" value="true,false" default/>
    <ButtonGroupItem valueLabel="Yes" value="true"/>
    <ButtonGroupItem valueLabel="No"  value="false"/>
</ButtonGroup>

```sql aggregations
select
    avg(price) as avg_price,
    avg(sqm)   as avg_sqm,
    count(*)   as "number of listings",
    geojson_name as freguesia
from mart_listings
where has_garage in (${inputs.garage})
  and has_lift   in (${inputs.lift})
  and is_cave    in (${inputs.cave})
group by geojson_name
```

<ButtonGroup name=map_var title="Map Variable">
    <ButtonGroupItem valueLabel="Average Price (€/moth)" value="avg_price" default/>
    <ButtonGroupItem valueLabel="Average Footage (m²)" value="avg_sqm"/>
    <ButtonGroupItem valueLabel="Total Listings"  value="number of listings"/>
</ButtonGroup>

<AreaMap
    data={aggregations}
    areaCol=freguesia
    geoJsonUrl='/freguesias.geojson'
    geoId=NOME
    value={inputs.map_var}
    valueFmt=num0
    height=400
    basemap={`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png`}
    startingLat=38.7223
    startingLong=-9.1393
    startingZoom=11
/>

<DataTable data={aggregations} rows=all/>