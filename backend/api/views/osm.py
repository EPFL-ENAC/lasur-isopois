import logging
from typing import Dict
from fastapi import APIRouter, Security
from ..auth import get_api_key
from ..service.osm import OsmService
from ..models.domain import FeatureCollection, PoisData

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


@router.post("/_cache", response_model=Dict, response_model_exclude_none=True)
async def get_pois(
    api_key: str = Security(get_api_key),
) -> Dict:
    """Get available OSM features for isochrone calculations and cache them.
    Use default bounding box and categories from config.
    """
    try:
        pois_service = OsmService()
        count_by_category = await pois_service.make_cache()
        return count_by_category
    except Exception as e:
        logging.error(e, exc_info=True)
        return {'error': str(e)}


@router.delete("/_cache", response_model=None)
async def delete_pois_cache(
    api_key: str = Security(get_api_key),
) -> None:
    """Delete all cached OSM features."""
    try:
        pois_service = OsmService()
        await pois_service.delete_cache()
    except Exception as e:
        logging.error(e, exc_info=True)
        return None
