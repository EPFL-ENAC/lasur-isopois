<template>
  <div>
    <IsochronesMap v-if="origin" :mapId="`map-iso`" :center="origin" :height="'800px'" :zoom="11" />
  </div>
</template>

<script setup lang="ts">
import IsochronesMap from 'src/components/IsochronesMap.vue'

const origin: [number, number] = [6.57, 46.52] // EPFL
</script>
