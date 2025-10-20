import logging
from typing import Dict
from fastapi import APIRouter, Security
from ..auth import get_api_key
from ..models.domain import IsochroneData, IsochroneResponse, FeatureCollection
from ..service.lasur import LasurService
from ..config import config
from ..auth import API_KEYS

router = APIRouter()


@router.get("/modes", response_model=Dict[str, str], response_model_exclude_none=True)
async def get_modes(api_key: str = Security(get_api_key)) -> Dict[str, str]:
    """Get available transport modes for isochrone calculations."""
    try:
        lasur_service = LasurService()
        return await lasur_service.get_transport_modes()
    except Exception as e:
        logging.error(e, exc_info=True)
        return {}


@router.post("/_compute", response_model=IsochroneResponse, response_model_exclude_none=True)
async def compute_isochrones(
    data: IsochroneData,
    # api_key: str = Security(get_api_key),
) -> IsochroneResponse:
    """Compute isochrones based on the provided data."""
    try:
        lasur_service = LasurService()
        isochrones = await lasur_service.get_isochrones(
            lon=data.lon,
            lat=data.lat,
            cutoffSec=data.cutoffSec,
            datetime=data.datetime,
            mode=data.mode,
            bikeSpeed=data.bikeSpeed
        )
        return IsochroneResponse(isochrones=isochrones)
    except Exception as e:
        logging.error(e, exc_info=True)
        return IsochroneResponse(isochrones=FeatureCollection(type="FeatureCollection", features=[]))
