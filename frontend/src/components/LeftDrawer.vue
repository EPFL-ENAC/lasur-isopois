<template>
  <q-list>
    <q-item>
      <q-item-section>
        <q-select
          :label="t('transport_mode')"
          v-model="isoService.mode"
          :loading="isoService.loadingIsochrones"
          :disable="isoService.loadingIsochrones"
          :options="modeOptions"
          option-value="value"
          option-label="label"
          filled
          emit-value
          map-options
          hide-dropdown-icon
        />
      </q-item-section>
    </q-item>

    <q-item>
      <q-item-section>
        <address-input
          v-model="location"
          :label="t('location')"
          :hint="t('address_input_hint')"
          @update:modelValue="onLocationUpdate"
        />
      </q-item-section>
    </q-item>

    <q-item>
      <q-item-section>
        <q-input
          v-model="query"
          :label="t('francetravail.query')"
          :hint="t('francetravail.input_hint')"
          filled
          clearable
          @keyup.enter="onLookupJobs"
        />
      </q-item-section>
    </q-item>

    <q-item>
      <q-item-section>
        <q-item-label class="text-bold q-mt-md">{{ t('pois.title') }}</q-item-label>
        <q-list class="q-mt-sm">
          <template v-for="pois in isoService.poisOptions" :key="pois.value">
            <q-item clickable class="q-pt-none q-pb-none">
              <q-item-section>{{ pois.label }}</q-item-section>
              <q-item-section side>
                <q-toggle
                  v-model="isoService.selectedPois[pois.value]"
                  :color="pois.color"
                  keep-color
                  @update:model-value="onPoiUpdate(pois.value)"
                />
              </q-item-section>
            </q-item>
          </template>
        </q-list>
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup lang="ts">
import type { AddressLocation } from 'src/components/models'
import AddressInput from './AddressInput.vue'

const isoService = useIsochrones()
const { t } = useI18n()

const location = ref<AddressLocation>({ address: '' })
const query = ref('')

const modeOptions = computed(() => {
  return ['WALK', 'BIKE', 'EBIKE', 'CAR'].map((m) => {
    return { label: t(`pois.mode.${m.toLowerCase()}`), value: m }
  })
})

function onLocationUpdate(newLocation: AddressLocation) {
  if (newLocation.lat !== undefined && newLocation.lon !== undefined) {
    if (newLocation.lat === isoService.origin[1] && newLocation.lon === isoService.origin[0]) {
      return
    }
    isoService.origin = [newLocation.lon, newLocation.lat]
  }
}

function onPoiUpdate(category: string) {
  isoService.updatedPoiSelection = `${category}:${isoService.selectedPois[category]}`
}

async function onLookupJobs() {
  if (query.value.trim().length === 0) {
    return
  }
  isoService.query = query.value.trim()
}
</script>
