import json
import pandas as pd
import geopandas as gpd
from francetravail_pipeline import get_rome_access_token, get_rome_codes, get_jobs_access_token, get_department_offers
from ..config import config


class FranceTravailService:

    def __init__(self):
        self.client_id_rome = config.CLIENT_ID_ROME
        self.client_secret_rome = config.CLIENT_SECRET_ROME
        self.client_id_jobs = config.CLIENT_ID_JOBS
        self.client_secret_jobs = config.CLIENT_SECRET_JOBS
        self.rome_token = None
        self.jobs_token = None
        self.regions = json.loads(config.REGIONS)

    def authenticate_rome(self):
        self.rome_token = get_rome_access_token(
            self.client_id_rome, self.client_secret_rome)

    def search_rome_codes(self, query: str):
        self.authenticate_rome()
        return get_rome_codes(self.rome_token, query)

    def authenticate_jobs(self):
        self.jobs_token = get_jobs_access_token(
            self.client_id_jobs, self.client_secret_jobs)

    def search_jobs(self, rome_codes: list[str], regions: list[str]) -> gpd.GeoDataFrame:
        self.authenticate_jobs()
        offers = get_department_offers(
            self.jobs_token, regions if regions else self.regions, ",".join(rome_codes))
        # exclude offers without geometry or with geometry with NaN values
        offers = offers[~offers.geometry.is_empty & offers.geometry.notnull()]
        # exclude offers with invalid geometry (e.g., POINT(NaN NaN))
        offers = offers[offers.geometry.is_valid]
        return gpd.GeoDataFrame(offers, geometry=offers.geometry, crs="EPSG:4326")
