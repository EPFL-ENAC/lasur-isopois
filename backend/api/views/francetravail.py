import logging
import json
from fastapi import APIRouter, Security
from ..auth import get_api_key
from ..service.francetravail import FranceTravailService
from ..models.domain import FeatureCollection, RomeCodeResponse, JobsResponse

router = APIRouter()


@router.get("/_codes", response_model=RomeCodeResponse, response_model_exclude_none=True)
async def get_codes(
    query: str,
    # api_key: str = Security(get_api_key),
) -> RomeCodeResponse:
    """Get available ROME codes matching the query."""
    try:
        ft_service = FranceTravailService()
        return RomeCodeResponse(codes=ft_service.search_rome_codes(query))
    except Exception as e:
        logging.error(e, exc_info=True)
        return RomeCodeResponse(codes=[])


@router.get("/_jobs", response_model=JobsResponse, response_model_exclude_none=True)
async def get_jobs(
    rome_codes: str,
    departments: str = '["01", "74"]',
    # api_key: str = Security(get_api_key),
) -> JobsResponse:
    """Get available job offers to be displayed on the map, optionally filtered by ROME codes and departments."""
    # Sanity check: verify that rome_codes is a valid JSON array of strings
    codes = []
    deps = []
    try:
        codes = json.loads(rome_codes)
        if not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
            logging.error("rome_codes is not a list of strings")
            return JobsResponse(offers=[], codes=[], departments=[])
    except json.JSONDecodeError:
        logging.error("Invalid rome_codes JSON")
        return JobsResponse(offers=FeatureCollection(type="FeatureCollection", features=[], bbox=None), codes=[], departments=[])
    try:
        deps = json.loads(departments)
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            logging.error("departments is not a list of strings")
            return JobsResponse(offers=FeatureCollection(type="FeatureCollection", features=[], bbox=None), codes=[], departments=[])
    except Exception as e:
        logging.error(e, exc_info=True)
        return JobsResponse(offers=FeatureCollection(type="FeatureCollection", features=[], bbox=None), codes=[], departments=[])

    try:
        ft_service = FranceTravailService()
        features = ft_service.search_jobs(codes, deps)
        # if geo dataframe is empty, return empty feature collection
        if features.empty:
            return JobsResponse(offers=FeatureCollection(type="FeatureCollection", features=[], bbox=None), codes=codes, departments=deps)
        return JobsResponse(offers=features.__geo_interface__, codes=codes, departments=deps)
    except Exception as e:
        logging.error(e, exc_info=True)
        return JobsResponse(offers=FeatureCollection(type="FeatureCollection", features=[], bbox=None), codes=[], departments=[])
