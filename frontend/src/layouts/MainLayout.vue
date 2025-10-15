<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <span class="text-primary text-bold on-right">{{ t('main.brand') }}</span>
        </q-toolbar-title>

        <q-btn-dropdown flat dense :label="locale" class="on-left">
          <q-list>
            <q-item
              clickable
              v-close-popup
              @click="onLocaleSelection(localeOpt)"
              v-for="localeOpt in localeOptions"
              :key="localeOpt.value"
            >
              <q-item-section>
                <q-item-label>{{ localeOpt.label }}</q-item-label>
              </q-item-section>
              <q-item-section avatar v-if="locale === localeOpt.value">
                <q-icon color="primary" name="check" />
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
        <a href="https://www.epfl.ch" target="_blank">
          <img src="EPFL.svg" height="20px" class="on-left" />
        </a>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item clickable :to="'/'">
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('dashboard') }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item-label class="text-h6" header>{{ t('help') }}</q-item-label>
        <q-item clickable :to="'/cookbook'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-bowl-rice" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('cookbook') }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { Cookies } from 'quasar'
import { locales } from 'boot/i18n'

const { locale, t } = useI18n()

const leftDrawerOpen = ref(false)

const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: key.toUpperCase(),
    value: key,
  }))
})

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>
