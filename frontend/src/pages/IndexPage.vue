<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div class="q-pa-md">
      <dashboard-panel />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import DashboardPanel from 'src/components/DashboardPanel.vue'
const { t } = useI18n()
</script>
