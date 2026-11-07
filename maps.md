# Geographic animation

Use `kind: "geomap"` for actual geography, `kind: "map"` only for explicitly abstract diagrams. Packaged data: Natural Earth 1:110m modern country boundaries, public domain; lineage in assets/world-source.json. Use externally supplied, attributed GeoJSON for cities, roads or historical borders. A country outline is not a detailed street basemap.

```json
{
 "text":"İstanbul'dan Berlin'e bir rota çiziliyor.","duration":4,"kind":"geomap","zoom":0,
 "map":{
   "bounds":[5,34,40,57],"projection":"mercator",
   "route":[[28.9784,41.0082],[13.4050,52.5200]],
   "great_circle":true,"highlight":["TUR","DEU"],"distance":true,
   "markers":[{"name":"İstanbul","at":[28.9784,41.0082]},{"name":"Berlin","at":[13.4050,52.5200]}]
 }
}
```

`bounds` = west,south,east,north; all coordinates are longitude,latitude. `end_bounds` animates a zoom/pan. `follow: true` follows the moving marker; bounds then specify viewport extent. `route` accepts waypoints, great-circle interpolation by default. Distances use spherical Earth; not a driving distance, airline routing promise or navigation result. `values` maps country ISO/name to numeric data; `vmin/vmax` set a fixed choropleth scale. Explain scale and units in the visual/script. `geojson` overrides bundled boundaries with a local FeatureCollection path.

Dateline routes should use a continuous viewport such as [140,-20,220,60]. Exactly antipodal endpoints require an intermediate waypoint. Inspect dateline borders, small islands, clipped markers and label collisions. The map renderer clips drawing to its viewport and avoids long seam lines. Dataset is low resolution: do not zoom into a city and claim street accuracy. Use actual sourced local GeoJSON or an external map renderer instead.

For higher-detail local browser workflows consider MapLibre + Turf or Remotion's map techniques. These need separate dependencies, may need tile network access and must preserve map-data/style attribution. No API-key bypasses or screenshotting arbitrary maps without required credit.

Sources inspected:
- https://github.com/remotion-dev/skills/tree/main/skills/remotion-maps
- https://www.remotion.dev/docs/maps/
- https://github.com/iart-ai/map-animation-skills
- https://www.naturalearthdata.com/about/terms-of-use/

The packaged Python route/projection/drawing implementation is independent; these sources are reference material, not imported skill files.
