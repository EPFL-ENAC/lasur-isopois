<template>
  <q-toolbar class="q-pa-sm">
    <div class="row q-col-gutter-sm">
      <div class="col-md-3 col-6">
        <q-input
          v-model="query"
          :label="t('francetravail.query')"
          :disable="isoService.loadingJobs"
          filled
          dense
          @keyup.enter="onLookupJobs"
          style="min-width: 200px"
        />
      </div>
      <div class="col-md-3 col-6">
        <q-select
          :label="t('regions')"
          v-model="isoService.selectedRegions"
          :options="regionOptions"
          :disable="isoService.loadingJobs"
          filled
          dense
          emit-value
          map-options
          multiple
          max-values="5"
          style="min-width: 200px"
        />
      </div>
      <div class="col-md-3 col-6">
        <address-input
          v-model="location"
          :label="t('location')"
          @update:modelValue="onLocationUpdate"
        />
      </div>
      <div class="col-md-3 col-6">
        <q-select
          :label="t('transport_mode')"
          v-model="isoService.mode"
          :disable="isoService.loadingIsochrones"
          :options="modeOptions"
          option-value="value"
          option-label="label"
          filled
          dense
          emit-value
          map-options
          hide-dropdown-icon
          style="min-width: 200px"
        />
      </div>
      <!-- div class="col-md-3 col-6">
        <q-input
          v-model.number="isoService.duration"
          type="number"
          :label="t('max_duration_minutes')"
          :disable="isoService.loadingIsochrones"
          filled
          dense
          @keyup.enter="onLocationUpdate"
          style="min-width: 200px"
        />
      </div -->
    </div>
  </q-toolbar>
</template>
<script setup lang="ts">
import AddressInput from './AddressInput.vue'
import { REGIONS, type Region } from 'src/stores/isochrones'
import type { AddressLocation } from 'src/components/models'

const { t } = useI18n()

const isoService = useIsochrones()
const query = ref('')
const location = ref<AddressLocation>({ address: '' })

const modeOptions = computed(() => {
  return ['WALK', 'BIKE', 'EBIKE', 'CAR', 'TRANSIT', 'RAIL', 'BUS'].map((m) => {
    return { label: t(`pois.mode.${m.toLowerCase()}`), value: m }
  })
})

const regionOptions = computed(() => {
  return REGIONS.map((region: Region) => {
    return { label: region.name || region.id, value: region.id }
  })
})

function onLocationUpdate(newLocation: AddressLocation) {
  if (newLocation.lat !== undefined && newLocation.lon !== undefined) {
    if (!isoService.origin) {
      isoService.origin = [newLocation.lon, newLocation.lat]
      return
    }
    if (newLocation.lat === isoService.origin[1] && newLocation.lon === isoService.origin[0]) {
      return
    }
    isoService.origin = [newLocation.lon, newLocation.lat]
  }
}

async function onLookupJobs() {
  if (query.value.trim().length === 0) {
    return
  }
  isoService.query = query.value.trim()
}
</script>
