import { api } from 'src/boot/api'
import type {
  IsochronesParams,
  IsochronesData,
  IsochronesModes,
  PoisParams,
  RomeCodeResponse,
  JobsResponse,
} from 'src/models'
import type { AxiosResponse } from 'axios'
import { geocoderApi } from 'src/utils/geocoder'

export const CATEGORY_TAGS = {
  food: {
    amenity: ['restaurant', 'cafe', 'fast_food', 'food_court'],
    shop: ['supermarket', 'convenience', 'bakery', 'butcher', 'pastry'],
  },
  education: {
    amenity: [
      'school',
      'library',
      'university',
      'college',
      'public_bookcase',
      'waste_disposal',
      'toy_library',
      'childcare',
      'library_dropoff',
      'prep_school',
    ],
  },
  service: {
    amenity: [
      'post_box',
      'bank',
      'post_office',
      'police',
      'townhall',
      'public_building',
      'public_bath',
    ],
    office: ['coworking', 'administrative'],
    shop: ['dry_cleaning', 'laundry', 'copyshop'],
  },
  health: {
    amenity: ['pharmacy', 'doctors', 'hospital', 'dentist', 'clinic', 'veterinary'],
    healthcare: [
      'pharmacy',
      'doctor',
      'alternative',
      'physiotherapist',
      'hospital',
      'dentist',
      'clinic',
      'laboratory',
      'podiatrist',
      'psychotherapist',
      'centre',
      'audiologist',
      'birthing_centre',
      'blood_donation',
      'optometrist',
      'psychomotricist',
    ],
  },
  leisure: {
    amenity: [
      'bar',
      'community_centre',
      'theatre',
      'social_facility',
      'pub',
      'bbq',
      'nightclub',
      'cinema',
      'music_school',
      'arts_centre',
      'events_venue',
      'social_centre',
      'exhibition_centre',
      'concert_hall',
      'biergarten',
    ],
    shop: ['art'],
    tourism: [
      'artwork',
      'hotel',
      'information',
      'attraction',
      'museum',
      'viewpoint',
      'gallery',
      'zoo',
      'picnic_site',
      'theme_park',
      'camp_site',
      'chalet',
      'motel',
    ],
  },
  transport: {
    amenity: [
      'car_sharing',
      'car_rental',
      'charging_station',
      'ferry_terminal',
      'bicycle_rental',
      'bicycle_repair_station',
      'bus_station',
    ],
    public_transport: ['stop_position', 'platform', 'station'],
  },
  commerce: {
    amenity: ['marketplace'],
    shop: [
      'clothes',
      'kiosk',
      'bicycle',
      'department_store',
      'shoes',
      'books',
      'florist',
      'sports',
      'mall',
      'coffee',
      'second_hand',
      'tea',
      'grocery',
    ],
  },
}

export interface Region {
  id: string
  name: string
  osmid: string
}

export const REGIONS: Region[] = [
  {
    id: '01',
    name: 'Ain',
    osmid: '7387',
  },
  {
    id: '38',
    name: 'Isère',
    osmid: '7437',
  },
  {
    id: '39',
    name: 'Jura',
    osmid: '7460',
  },
  {
    id: '69',
    name: 'Rhône',
    osmid: '7378',
  },
  {
    id: '71',
    name: 'Saône-et-Loire',
    osmid: '7397',
  },
  {
    id: '73',
    name: 'Savoie',
    osmid: '7425',
  },
  {
    id: '74',
    name: 'Haute-Savoie',
    osmid: '7407',
  },

  // {
  //   id: 'GE',
  //   name: 'Genève',
  //   osmid: '1702419',
  // },
]

export const useIsochrones = defineStore('isochrones', () => {
  const { t } = useI18n()

  const mode = ref<string>('WALK')
  const origin = ref<[number, number] | undefined>()
  const loadingIsochrones = ref(false)
  const selectedPois = ref<{ [key: string]: boolean }>({
    food: false,
    education: false,
    service: false,
    health: false,
    leisure: false,
    transport: false,
    commerce: false,
  })
  const updatedPoiSelection = ref<string>('')
  const query = ref('')
  const duration = ref<number | undefined>()
  const regions = ref<GeoJSON.Feature[]>([])
  const selectedRegions = ref<string[]>(['01', '74'])
  const loadingJobs = ref(false)

  const poisOptions = computed(() =>
    ['food', 'education', 'service', 'health', 'leisure', 'transport', 'commerce'].map((cat) => ({
      label: t(`pois.categories.${cat}`),
      value: cat,
      color: categoryToColor(cat)?.name || 'grey-8',
    })),
  )

  async function loadRegions() {
    regions.value = await Promise.all(
      REGIONS.map((entry) => {
        // fetch region details from assets
        return fetch(`/osm/${entry.osmid}.json`)
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Failed to fetch region ${entry.name} from assets`)
            }
            return response.json()
          })
          .then((data) => {
            return {
              id: data.osm_id,
              properties: data.names,
              geometry: data.geometry,
            } as GeoJSON.Feature
          })
          .catch((e) => {
            console.error(`Error fetching region ${entry.name} from assets:`, e)
            // fetch region details from OSM
            return geocoderApi.getDetails('R', entry.osmid)
          })
      }),
    )
  }

  function getModes() {
    return api
      .get('/isochrones/modes')
      .then((res) => {
        const data = res.data as { [key: string]: string }
        // split values
        return Object.fromEntries(
          Object.entries(data).map(([k, v]) => [k, v.split(',')]),
        ) as IsochronesModes
      })
      .catch(() => {
        return undefined
      })
  }

  function computeIsochrones(payload: IsochronesParams) {
    return api
      .post('/isochrones/_compute', payload)
      .then((res) => {
        return res.data as IsochronesData
      })
      .catch(() => {
        return undefined
      })
  }

  async function getOsmPois(payload: PoisParams) {
    return api
      .post('/osm/_pois', payload)
      .then((res) => {
        return res.data as GeoJSON.FeatureCollection
      })
      .catch(() => {
        return undefined
      })
  }

  async function getRomeCodes(query: string): Promise<RomeCodeResponse | undefined> {
    return api
      .get<RomeCodeResponse>('/francetravail/_codes', { params: { query } })
      .then((res: AxiosResponse<RomeCodeResponse>) => {
        return res.data
      })
      .catch(() => {
        return undefined
      })
  }

  async function getJobs(query: string): Promise<JobsResponse | undefined> {
    if (!query || query.trim().length === 0) {
      return undefined
    }
    loadingJobs.value = true
    const regionsParams =
      selectedRegions.value.length > 0 ? selectedRegions.value : REGIONS.map((r) => r.id)
    // check if it is a ROME code
    if (/^[A-Z]\d{4}$/.test(query.trim().toUpperCase())) {
      return api
        .get<JobsResponse>('/francetravail/_jobs', {
          params: {
            rome_codes: JSON.stringify([query.trim().toUpperCase()]),
            regions: JSON.stringify(regionsParams),
          },
        })
        .then((res: AxiosResponse<JobsResponse>) => {
          return res.data
        })
        .catch(() => {
          return undefined
        })
        .finally(() => {
          loadingJobs.value = false
        })
    }
    // else search ROME codes from query
    const rome_codes = await getRomeCodes(query)
    if (!rome_codes || !rome_codes.codes || rome_codes.codes.length === 0) {
      loadingJobs.value = false
      return undefined
    }
    return api
      .get<JobsResponse>('/francetravail/_jobs', {
        params: {
          rome_codes: JSON.stringify(rome_codes?.codes),
          regions: JSON.stringify(regionsParams),
        },
      })
      .then((res: AxiosResponse<JobsResponse>) => {
        return res.data
      })
      .catch(() => {
        return undefined
      })
      .finally(() => {
        loadingJobs.value = false
      })
  }

  function findCategory(tag: string, value: string) {
    for (const [category, tags] of Object.entries(CATEGORY_TAGS)) {
      if (tags[tag as keyof typeof tags]?.includes(value)) {
        return category
      }
    }
    return 'other'
  }

  function categoryToColor(str: string): { name: string; hex: string } | undefined {
    const mapColors: { [key: string]: { name: string; hex: string } } = {
      food: { name: 'red-9', hex: '#c62828' },
      education: { name: 'purple-9', hex: '#6a1b9a' },
      service: { name: 'blue-8', hex: '#1976d2' },
      health: { name: 'green-13', hex: '#00e676' },
      leisure: { name: 'light-green-9', hex: '#558b2f' },
      transport: { name: 'yellow-8', hex: '#fbc02d' },
      commerce: { name: 'pink-4', hex: '#f06292' },
    }
    if (str in mapColors && mapColors[str]) {
      return mapColors[str]
    }
  }

  return {
    mode,
    origin,
    loadingIsochrones,
    selectedPois,
    updatedPoiSelection,
    poisOptions,
    query,
    duration,
    regions,
    selectedRegions,
    loadingJobs,
    loadRegions,
    computeIsochrones,
    findCategory,
    getModes,
    getOsmPois,
    getRomeCodes,
    getJobs,
    categoryToColor,
  }
})
