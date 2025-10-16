export interface Link {
  source: string
  target: string
  value: number
}

export interface Links {
  total: number
  data: Link[]
}

export interface IsochronesParams {
  lon: number
  lat: number
  mode: string
  cutoffSec: number[]
  bikeSpeed?: number
  datetime: string
}

export interface IsochronesData {
  isochrones: GeoJSON.FeatureCollection<GeoJSON.Geometry>
  pois: GeoJSON.FeatureCollection<GeoJSON.Geometry>
}

export interface PoisParams {
  categories: string[]
  bbox: [number, number, number, number]
}

export interface IsochronesModes {
  [key: string]: string[]
}
