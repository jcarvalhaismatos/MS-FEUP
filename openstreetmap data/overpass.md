Query usada em `https://overpass-turbo.eu/`.
Apanha municípios (7) e freguesias (8) dentro de uma área retangular.

```sql
[out:json];

(
  way[admin_level=7]({{bbox}});
  way[admin_level=8]({{bbox}});

);

out body;
>;
out skel qt;
```