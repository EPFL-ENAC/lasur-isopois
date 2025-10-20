import logging
import requests
from typing import Dict
from ..models.domain import FeatureCollection
from ..config import config


class LasurService:
    def __init__(self):
        pass

    async def get_transport_modes(self) -> Dict[str, str]:
        """Get available transport modes from the LASUR web service.

        Returns:
            Dict[str, str]: A dictionary of available modes.
        """
        try:
            url = f"{config.LASUR_WS_URL}/isochrones/modes"
            headers = {
                "x-api-key": config.LASUR_WS_API_KEY,
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(
                    f"Failed to get available modes: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logging.error(e, exc_info=True)
            return {}

    async def get_isochrones(self, lon: float, lat: float, cutoffSec: int, datetime: str, mode: str, bikeSpeed: float) -> FeatureCollection:
        """Compute isochrones based on the provided parameters.
        Args:
            lon (float): Longitude of the location.
            lat (float): Latitude of the location.
            cutoffSec (int): Cutoff time in seconds.
            datetime (str): Date and time for the isochrone calculation.
            mode (str): Travel mode.
            bikeSpeed (float): Bike speed in km/h.
        Returns:

            FeatureCollection: GeoJSON FeatureCollection of isochrones.
        """
        try:
            url = f"{config.LASUR_WS_URL}/isochrones/compute"
            headers = {
                "x-api-key": config.LASUR_WS_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "lon": lon,
                "lat": lat,
                "cutoffSec": cutoffSec,
                "datetime": datetime,
                "mode": mode,
                "bikeSpeed": bikeSpeed,
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data["isochrones"]
            else:
                logging.error(
                    f"Failed to compute isochrones: {response.status_code} - {response.text}")
                return FeatureCollection(type="FeatureCollection", features=[])
        except Exception as e:
            logging.error(e, exc_info=True)
            return FeatureCollection(type="FeatureCollection", features=[])

    async def get_osm_pois(self, bbox: list[float], categories: list[str] = None, cached: bool = True) -> FeatureCollection:
        """Get available OSM features for isochrone calculations.
        If no bbox or categories are provided, use default from config.

        Args:
            bbox (list[float]): Bounding box [min_lon, min_lat, max_lon, max_lat].
            categories (list[str], optional): List of OSM categories. Defaults to None.
            cached (bool, optional): Whether to use cached data. Defaults to True.

        Returns:
            FeatureCollection: GeoJSON FeatureCollection of OSM features.
        """
        try:
            # request lasur ws service: POST /isochrones/pois
            url = f"{config.LASUR_WS_URL}/isochrones/pois"
            headers = {
                "x-api-key": config.LASUR_WS_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "bbox": bbox,
                "categories": categories,
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return FeatureCollection(type="FeatureCollection", features=data.get("features", []), bbox=bbox)
            else:
                logging.error(
                    f"Error fetching POIs: {response.status_code} {response.text}")
                return FeatureCollection(type="FeatureCollection", features=[], bbox=bbox)
        except Exception as e:
            logging.error(e, exc_info=True)
            return FeatureCollection(type="FeatureCollection", features=[], bbox=bbox)
