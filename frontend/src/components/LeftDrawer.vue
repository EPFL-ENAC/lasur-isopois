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
  </q-list>
</template>

<script setup lang="ts">
import type { AddressLocation } from 'src/components/models'
import AddressInput from './AddressInput.vue'

const isoService = useIsochrones()
const { t } = useI18n()

const location = ref<AddressLocation>({ address: '' })

const modeOptions = computed(() => {
  return ['WALK', 'BIKE', 'EBIKE'].map((m) => {
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
</script>
