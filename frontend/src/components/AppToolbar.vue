<template>
  <q-toolbar class="q-pa-sm">
    <div class="row q-gutter-sm" style="width: 100%">
      <q-input
        v-model="query"
        :label="t('francetravail.query')"
        :disable="isoService.loadingJobs"
        filled
        dense
        @keyup.enter="onLookupJobs"
        style="width: 200px"
      />
      <q-select
        :label="t('region')"
        v-model="isoService.selectedRegions"
        :options="regionOptions"
        :disable="isoService.loadingJobs"
        filled
        dense
        emit-value
        map-options
        multiple
        style="width: 200px"
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
        style="width: 200px"
      />
      <q-spinner-dots
        v-if="isoService.loadingJobs || isoService.loadingIsochrones"
        size="md"
        color="primary"
        class="q-mt-md"
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
