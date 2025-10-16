import logging
import json
from fastapi import APIRouter, Security
from ..auth import get_api_key
from ..service.osm import OsmService
from ..service.francetravail import FranceTravailService
from ..models.domain import FeatureCollection, PoisData, RomeCodeResponse, JobResponse

router = APIRouter()


@router.post("/_pois", response_model=FeatureCollection, response_model_exclude_none=True)
async def get_pois(
    data: PoisData,
    # api_key: str = Security(get_api_key),
) -> FeatureCollection:
    """Get available OSM features for isochrone calculations."""
    try:
        pois_service = OsmService()
        features = await pois_service.get_pois(
            bbox=data.bbox, categories=data.categories)
        return features
    except Exception as e:
        logging.error(e, exc_info=True)
        return FeatureCollection(type="FeatureCollection", features=[], bbox=data.bbox)


@router.post("/_codes", response_model=RomeCodeResponse, response_model_exclude_none=True)
async def get_codes(
    query: str,
    # api_key: str = Security(get_api_key),
) -> RomeCodeResponse:
    """Get available OSM features for isochrone calculations."""
    try:
        ft_service = FranceTravailService()
        return RomeCodeResponse(codes=ft_service.search_rome_codes(query))
    except Exception as e:
        logging.error(e, exc_info=True)
        return RomeCodeResponse(codes=[])


@router.post("/_jobs", response_model=JobResponse, response_model_exclude_none=True)
async def get_jobs(
    rome_codes: str,
    departments: str = '["01", "74"]',
    # api_key: str = Security(get_api_key),
) -> JobResponse:
    """Get available job offers for isochrone calculations."""
    # Sanity check: verify that rome_codes is a valid JSON array of strings
    codes = []
    deps = []
    try:
        codes = json.loads(rome_codes)
        if not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
            logging.error("rome_codes is not a list of strings")
            return JobResponse(offers=[])
    except json.JSONDecodeError:
        logging.error("Invalid rome_codes JSON")
        return JobResponse(offers=[])
    try:
        deps = json.loads(departments)
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            logging.error("departments is not a list of strings")
            return JobResponse(offers=[])
    except Exception as e:
        logging.error(e, exc_info=True)
        return JobResponse(offers=[])

    try:
        ft_service = FranceTravailService()
        features = ft_service.search_jobs(codes, deps)
        return JobResponse(offers=features.__geo_interface__, codes=codes, departments=deps)
    except Exception as e:
        logging.error(e, exc_info=True)
        return JobResponse(offers=[])
