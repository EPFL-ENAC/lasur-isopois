import logging
from typing import Dict
from fastapi import APIRouter, Security
from ..auth import get_api_key
from isochrones import calculate_isochrones, get_available_modes, intersect_isochrones
from ..models.domain import IsochroneData, IsochroneResponse, FeatureCollection
from ..config import config
from ..auth import API_KEYS
from datetime import datetime
import geopandas as gpd

router = APIRouter()


@router.get("/modes", response_model=Dict[str, str], response_model_exclude_none=True)
async def get_modes(api_key: str = Security(get_api_key)) -> Dict[str, str]:
    otp_url = config.OTP_URL
    # Use the first API key if available
    api_key = API_KEYS[0] if API_KEYS else None
    available_modes = get_available_modes(otp_url, api_key=api_key)
    return available_modes


@router.post("/_compute", response_model=IsochroneResponse, response_model_exclude_none=True)
async def compute_isochrones(
    data: IsochroneData,
    # api_key: str = Security(get_api_key),
) -> IsochroneResponse:
    """Compute isochrones and points of interest based on the provided data."""
    otp_url = config.OTP_URL
    # Use the first API key if available
    api_key = API_KEYS[0] if API_KEYS else None
    # parse datetime in ISO 8601 format into an object
    datetime_obj = datetime.fromisoformat(data.datetime)
    try:
        isochrones = calculate_isochrones(
            lat=data.lat,
            lon=data.lon,
            cutoffSec=data.cutoffSec,
            date_time=datetime_obj,
            mode=data.mode if hasattr(data, 'mode') else 'WALK',
            otp_url=otp_url,
            api_key=api_key,
            bike_speed=data.bikeSpeed if hasattr(data, 'bikeSpeed') else 13.0,
            router='default',
        )
        return IsochroneResponse(isochrones=isochrones.__geo_interface__)
    except Exception as e:
        logging.error(e, exc_info=True)
        return IsochroneResponse(isochrones=FeatureCollection(type="FeatureCollection", features=[]), pois=None)
