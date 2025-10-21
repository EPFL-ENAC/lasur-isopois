import { type StyleSpecification } from 'maplibre-gl'

export const style: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      // standard OSM tile server
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 20,
    },
  },
  layers: [
    {
      id: 'light',
      type: 'raster',
      source: 'osm',
      paint: {
        //'raster-saturation': 0.2,
        'raster-brightness-min': 0.2,
      },
    },
  ],
}
