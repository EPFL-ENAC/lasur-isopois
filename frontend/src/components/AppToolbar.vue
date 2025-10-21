<template>
  <q-toolbar class="q-pa-sm">
    <div class="row q-col-gutter-sm">
      <q-input
        v-model="query"
        :label="t('francetravail.query')"
        :disable="isoService.loadingJobs"
        filled
        dense
        @keyup.enter="onLookupJobs"
        style="min-width: 200px"
      />
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
      <q-btn v-if="$q.screen.lt.md" flat dense icon="more_vert" class="q-mt-sm">
        <q-menu>
          <q-list style="min-width: 150px">
            <q-item>
              <q-input
                v-model.number="isoService.duration"
                type="number"
                :label="t('max_duration_minutes')"
                :disable="isoService.loadingIsochrones"
                filled
                dense
                :debounce="1000"
                style="min-width: 150px"
              />
            </q-item>
            <q-separator />
            <q-item>
              <address-input
                v-model="location"
                :label="t('address_search')"
                @update:modelValue="onLocationUpdate"
                style="min-width: 150px"
              />
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
      <q-input
        v-if="!$q.screen.lt.md"
        v-model.number="isoService.duration"
        type="number"
        :label="t('max_duration_minutes')"
        :disable="isoService.loadingIsochrones"
        filled
        dense
        :debounce="1000"
        style="min-width: 200px"
      />
      <address-input
        v-if="!$q.screen.lt.md"
        v-model="location"
        :label="t('address_search')"
        @update:modelValue="onLocationUpdate"
        style="min-width: 200px"
      />
    </div>
  </q-toolbar>
</template>
<script setup lang="ts">
import { useQuasar } from 'quasar'
import AddressInput from './AddressInput.vue'
import { REGIONS, type Region } from 'src/stores/isochrones'
import type { AddressLocation } from 'src/components/models'

const $q = useQuasar()
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
