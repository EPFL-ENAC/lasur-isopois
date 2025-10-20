<template>
  <div>
    <IsochronesMap :mapId="`map-iso`" :zoom="11" style="height: calc(100vh - 110px)" />
  </div>
</template>

<script setup lang="ts">
import IsochronesMap from 'src/components/IsochronesMap.vue'
</script>
