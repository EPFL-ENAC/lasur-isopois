<template>
  <div>
    <IsochronesMap :mapId="`map-iso`" :height="'95vh'" :zoom="11" />
  </div>
</template>

<script setup lang="ts">
import IsochronesMap from 'src/components/IsochronesMap.vue'
</script>
