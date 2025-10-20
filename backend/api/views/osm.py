import logging
from fastapi import APIRouter, Security
from ..auth import get_api_key
from ..service.lasur import LasurService
from ..models.domain import FeatureCollection, PoisData

router = APIRouter()


@router.post("/_pois", response_model=FeatureCollection, response_model_exclude_none=True)
async def get_pois(
    data: PoisData,
    # api_key: str = Security(get_api_key),
) -> FeatureCollection:
    """Get available OSM features for isochrone calculations."""
    try:
        pois_service = LasurService()
        features = await pois_service.get_osm_pois(
            bbox=data.bbox, categories=data.categories)
        return features
    except Exception as e:
        logging.error(e, exc_info=True)
        return FeatureCollection(type="FeatureCollection", features=[], bbox=data.bbox)
