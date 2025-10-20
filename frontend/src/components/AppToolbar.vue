<template>
  <q-toolbar class="q-pa-sm">
    <div class="row q-gutter-sm" style="width: 100%">
      <q-input
        v-model="query"
        :label="t('francetravail.query')"
        filled
        dense
        @keyup.enter="onLookupJobs"
        style="max-width: 350px"
      />
      <q-select
        :label="t('region')"
        v-model="isoService.selectedRegion"
        :options="regionOptions"
        filled
        dense
        emit-value
        map-options
        style="min-width: 200px"
      />
      <q-select
        :label="t('transport_mode')"
        v-model="isoService.mode"
        :loading="isoService.loadingIsochrones"
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
  </q-toolbar>
</template>
<script setup lang="ts">
import { REGIONS, type Region } from 'src/stores/isochrones'

const { t } = useI18n()

const isoService = useIsochrones()
const query = ref('')

const modeOptions = computed(() => {
  return ['WALK', 'BIKE', 'EBIKE', 'CAR'].map((m) => {
    return { label: t(`pois.mode.${m.toLowerCase()}`), value: m }
  })
})

const regionOptions = computed(() => {
  return REGIONS.map((region: Region) => {
    return { label: region.name || region.id, value: region.id }
  })
})

async function onLookupJobs() {
  if (query.value.trim().length === 0) {
    return
  }
  isoService.query = query.value.trim()
}
</script>
