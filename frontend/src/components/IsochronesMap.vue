<template>
  <div>
    <div class="container">
      <div :id="mapId" class="mapview" />
      <div
        v-if="selectedModeCutoffSec.length"
        class="colors q-pa-sm bg-white text-grey-8 text-caption rounded-borders"
      >
        <div class="row q-gutter-sm">
          <div
            v-for="(cutoff, index) in selectedModeCutoffSec"
            :key="`color-${cutoff}`"
            class="row items-center"
          >
            <div
              :style="`width: 15px; height: 15px; background-color: rgba(90, 63, 192, ${cutoffSecTransparency(index)}); border: 1px solid #5a3fc0; margin-right: 5px;`"
            ></div>
            <div>{{ t('pois.minutes', { count: Math.floor(cutoff / 60) }) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MapGeoJSONFeature } from 'maplibre-gl'
import {
  AttributionControl,
  FullscreenControl,
  Map,
  Marker,
  NavigationControl,
  Popup,
  type GeoJSONSource,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from 'src/utils/maps'

const isoService = useIsochrones()

interface Props {
  zoom?: number
  mapId: string
  labelClass?: string
}
const props = defineProps<Props>()

const { t } = useI18n()

const map = ref<Map>()
let marker: Marker | undefined
const isochronesData = ref<GeoJSON.FeatureCollection>()
const selectedModeCutoffSec = ref<number[]>([]) // in seconds

const DEFAULT_CENTER: [number, number] = [6.130943093534228, 46.20157251211427] // Geneva as default

onMounted(onInit)

watch(
  () => [isoService.origin, isoService.mode],
  () => {
    let toUpdate = false
    if (
      isoService.origin &&
      isoService.origin[0] !== undefined &&
      isoService.origin[1] !== undefined
    ) {
      if (map.value) {
        map.value.setCenter(isoService.origin)
        if (marker) {
          marker.setLngLat(isoService.origin)
        } else {
          marker = new Marker().setLngLat(isoService.origin)
          marker.addTo(map.value)
        }
        toUpdate = true
      }
    }
    if (isoService.mode !== undefined) {
      toUpdate = true
    }
    if (toUpdate) {
      loadIsochronesData()
    }
  },
)

watch(
  () => [isoService.updatedPoiSelection, isoService.selectedPois],
  () => {
    if (isoService.updatedPoiSelection && isoService.updatedPoiSelection.length > 0) {
      const category = isoService.updatedPoiSelection.split(':')[0]
      if (category && category.length > 0) {
        onUpdatePoiLayer(category)
      }
    }
  },
)

watch(
  () => isoService.query,
  () => {
    if (isoService.query && isoService.query.length > 0) {
      onUpdateJobsLayer()
    }
  },
)

watch(
  () => isoService.regions,
  () => {
    if (isoService.regions.length) {
      // Update the map with the new region boundaries
      showRegions()
    }
  },
)

watch(
  () => isoService.selectedRegions,
  () => {
    onUpdateJobsLayer()
  },
)

function onInit() {
  map.value = new Map({
    container: props.mapId,
    center: isoService.origin || DEFAULT_CENTER,
    style: style,
    trackResize: true,
    zoom: props.zoom || 14,
    attributionControl: false,
  })
  map.value.addControl(new NavigationControl({}))
  map.value.addControl(new FullscreenControl({}))
  map.value.addControl(
    new AttributionControl({
      compact: true,
      customAttribution:
        '© <a href="https://www.francetravail.fr">France Travail</a>, <a href="https://www.epfl.ch/labs/lasur/">EPFL Lasur</a>, <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    }),
  )
  if (isoService.origin) {
    marker = new Marker().setLngLat([isoService.origin[0], isoService.origin[1]])
    marker.addTo(map.value)
    loadIsochrones()
  }
  map.value.on('click', (e) => {
    isoService.origin = [e.lngLat.lng, e.lngLat.lat]
  })
  isoService.loadRegions()

  // show popup on hovering jobs-layer points
  map.value.on('mouseenter', 'jobs-layer', (e) => {
    if (!e.features || !e.features.length) return
    const feature = e.features[0]
    showFeaturePopup(feature as MapGeoJSONFeature)
  })
}

function showFeaturePopup(feature: MapGeoJSONFeature) {
  if (!map.value) return
  if (feature?.geometry?.type !== 'Point') return
  const coordinates = (feature.geometry as GeoJSON.Point).coordinates.slice()
  const popupContent = document.createElement('div')
  popupContent.innerHTML = `<strong>${t('job_offer')}</strong>`
  Object.entries(feature.properties).forEach(([key, value]) => {
    const propDiv = document.createElement('div')
    if (key === 'URL') {
      const link = document.createElement('a')
      link.href = value as string
      link.textContent = t(`francetravail.offer.${key}`)
      link.target = '_blank'
      link.className = 'epfl'
      propDiv.appendChild(link)
    } else if (key === 'dateCreation') {
      propDiv.textContent =
        t(`francetravail.offer.${key}`) + `: ${new Date(value as string).toLocaleDateString()}`
    } else {
      propDiv.textContent = t(`francetravail.offer.${key}`) + `: ${value}`
    }
    popupContent.appendChild(propDiv)
  })

  new Popup()
    .setLngLat(coordinates as [number, number])
    .setDOMContent(popupContent)
    .addTo(map.value!)
}

function loadIsochrones() {
  if (!map.value) return
  loadIsochronesData()
}

async function loadIsochronesData() {
  removeIsochrones()
  removePois()
  if (!isoService.origin) return
  isoService.loadingIsochrones = true
  const lon = isoService.origin[0]
  const lat = isoService.origin[1]
  let cutoffSec = []
  let mode = 'WALK'
  let bikeSpeed = 13
  switch (isoService.mode) {
    case 'WALK':
      mode = 'WALK'
      cutoffSec = [600, 1200, 1800, 2400]
      break
    case 'BIKE':
      mode = 'BICYCLE'
      cutoffSec = [600, 1200, 1800, 2400]
      break
    case 'EBIKE':
      mode = 'BICYCLE'
      bikeSpeed = 17
      cutoffSec = [600, 1200, 1800, 2400]
      break
    case 'CAR':
      mode = 'CAR'
      cutoffSec = [1200, 2400]
      break
    default:
      cutoffSec = [600, 1200, 1800]
      break
  }
  selectedModeCutoffSec.value = cutoffSec
  return isoService
    .computeIsochrones({
      lon,
      lat,
      mode,
      bikeSpeed,
      cutoffSec,
      datetime: '2025-01-15T06:00:00Z',
    })
    .then((data) => {
      if (data?.isochrones) {
        isochronesData.value = data?.isochrones
        showIsochrones(isochronesData.value)
        if (data?.isochrones.bbox) {
          // load POIs in the current map bbox
          const selected = Object.entries(isoService.selectedPois)
            .filter(([, v]) => v)
            .map(([k]) => k)
          if (selected.length > 0) {
            loadPois(selected)
          }
        }
      }
    })
    .catch((err) => {
      console.error('Error computing isochrones', err)
    })
    .finally(() => {
      isoService.loadingIsochrones = false
    })
}

function removePois() {
  // reset selectedPois
  Object.keys(isoService.selectedPois).forEach((key) => {
    isoService.selectedPois[key] = false
  })

  if (!map.value) return
  isoService.poisOptions.forEach((cat) => {
    const layerId = `pois-layer-${cat.value}`
    if (map.value && map.value.getLayer(layerId)) {
      map.value.removeLayer(layerId)
      map.value.removeSource(layerId)
    }
  })
}

async function loadPois(categories: string[]) {
  if (!map.value) return
  if (!isochronesData.value || !isochronesData.value.bbox) return
  const bbox = isochronesData.value.bbox as [number, number, number, number]
  isoService.loadingIsochrones = true
  const data = await isoService.getOsmPois({
    categories,
    bbox,
  })
  if (data) {
    showPois(data)
  }
  isoService.loadingIsochrones = false
}

function removeIsochrones() {
  if (!map.value) return
  if (map.value.getSource('isochrones')) {
    if (map.value.getLayer('isochrones-layer')) {
      map.value.removeLayer('isochrones-layer')
    }
    map.value.removeSource('isochrones')
  }
}

function showIsochrones(geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  if (map.value.getSource('isochrones')) {
    ;(map.value.getSource('isochrones') as GeoJSONSource).setData(geojson)
  } else {
    map.value.addSource('isochrones', {
      type: 'geojson',
      data: geojson,
    })
    map.value.addLayer({
      id: 'isochrones-layer',
      type: 'fill',
      source: 'isochrones',
      paint: {
        'fill-color': '#5a3fc0',
        'fill-opacity': 0.3,
        'fill-outline-color': '#5a3fc0',
      },
    })
  }
  // remove pois layers if any
  isoService.poisOptions.forEach((cat) => {
    const layerId = `pois-layer-${cat.value}`
    if (map.value?.getLayer(layerId)) {
      map.value.removeLayer(layerId)
      map.value.removeSource(layerId)
    }
  })
}

function showRegions() {
  isoService.regions.forEach((geojson: GeoJSON.Feature) => {
    if (!map.value) return
    // make one layer for each polygon
    const layerId = `region-layer-${geojson.id}`
    const hasLayer = map.value.getLayer(layerId) !== undefined
    const data = {
      type: 'FeatureCollection',
      features: [geojson],
    } as GeoJSON.FeatureCollection
    if (hasLayer) {
      ;(map.value.getSource(layerId) as GeoJSONSource).setData(data)
    } else {
      map.value.addSource(layerId, {
        type: 'geojson',
        data,
      })
      map.value.addLayer({
        id: layerId,
        type: 'line',
        source: layerId,
        paint: {
          'line-color': '#ff0000', // red
          'line-width': 2,
          'line-opacity': 0.5,
        },
      })
    }
  })
}

function showPois(geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  const sources: { [key: string]: GeoJSON.FeatureCollection } = {}
  // set a color property based on category
  geojson.features.forEach((feature) => {
    if (feature.properties && feature.properties.variable && feature.properties.value) {
      const cat = isoService.findCategory(
        feature.properties.variable as string,
        feature.properties.value as string,
      )
      feature.properties.category = cat
      feature.properties.color = isoService.categoryToColor(cat)?.hex || '#000000'
    } else if (feature.properties) {
      feature.properties.color = '#000000'
    }
  })
  // split by category
  geojson.features.forEach((feature) => {
    if (feature.properties && feature.properties.category) {
      const cat = feature.properties.category as string
      if (!(cat in sources)) {
        sources[cat] = { type: 'FeatureCollection', features: [] }
      }
      if (sources[cat]) {
        sources[cat].features.push(feature)
      }
    }
  })
  // add a layer per category
  Object.entries(sources).forEach(([cat, data]) => {
    const layerId = `pois-layer-${cat}`
    if (map.value?.getSource(layerId)) {
      ;(map.value?.getSource(layerId) as GeoJSONSource).setData(data)
    } else {
      map.value?.addSource(layerId, {
        type: 'geojson',
        data,
      })
      map.value?.addLayer({
        id: layerId,
        type: 'circle',
        source: layerId,
        paint: {
          // zoom level 5 -> 2px, level 15 -> 10px
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 1, 18, 5],
          'circle-color': ['get', 'color'],
        },
      })
      // hide if not selected
      if (map.value?.getLayer(layerId) && !isoService.selectedPois[cat]) {
        map.value.setLayoutProperty(layerId, 'visibility', 'none')
      }
    }
  })
}

function onUpdatePoiLayer(name: string) {
  if (!map.value) return
  const layerId = `pois-layer-${name}`
  const hasLayer = map.value.getLayer(layerId) !== undefined
  if (!hasLayer) {
    // load POIs in the current map bbox
    if (map.value) {
      const bbox = isochronesData.value?.bbox as [number, number, number, number]
      if (!bbox) return
      loadPois([name])
    }
    return
  }
  // show/hide layer
  if (isoService.selectedPois[name]) {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'visible')
    }
  } else {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'none')
    }
  }
}

function cutoffSecTransparency(index: number): number {
  const total = selectedModeCutoffSec.value.length
  return 0.1 + (0.7 * (total - index + 1)) / total
}

async function onUpdateJobsLayer() {
  if (!map.value) return
  showJobs((await loadJobs())?.offers || { type: 'FeatureCollection', features: [] })
  // show/hide layer
  const layerId = 'jobs-layer'
  if (isoService.query && isoService.query.length > 0) {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'visible')
    }
  } else {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'none')
    }
  }
}

async function loadJobs() {
  try {
    const res = await isoService.getJobs(isoService.query.trim())
    return res
  } catch (error) {
    console.error('Error fetching Jobs:', error)
    return undefined
  }
}

function showJobs(geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  const layerId = 'jobs-layer'
  if (map.value.getSource(layerId)) {
    ;(map.value.getSource(layerId) as GeoJSONSource).setData(geojson)
  } else {
    map.value.addSource(layerId, {
      type: 'geojson',
      data: geojson,
    })
    map.value.addLayer({
      id: layerId,
      type: 'circle',
      source: layerId,
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 10, 18, 5],
        'circle-color': '#FF5722',
        'circle-opacity': 0.8,
      },
    })
  }
}
</script>

<style scoped>
.container {
  position: relative; /* Needed for absolute children */
  height: 100%; /* Full height of parent container */
}
.mapview {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
}
.colors {
  position: absolute;
  z-index: 10;
  top: 10px;
  left: 10px;
}
</style>
