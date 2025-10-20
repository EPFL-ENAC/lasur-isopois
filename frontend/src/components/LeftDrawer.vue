<template>
  <q-list>
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
const isoService = useIsochrones()
const { t } = useI18n()

function onPoiUpdate(category: string) {
  isoService.updatedPoiSelection = `${category}:${isoService.selectedPois[category]}`
}
</script>
