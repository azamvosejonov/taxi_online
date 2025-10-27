import aiohttp
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class MapService:
    """Xarita xizmatlari uchun asosiy klass"""
    
    OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving/"
    
    @classmethod
    async def get_route(
        cls, 
        start_lon: float, 
        start_lat: float, 
        end_lon: float, 
        end_lat: float
    ) -> Dict:
        """Ikki nuqta orasidagi eng qisqa yo'lni topish"""
        url = f"{cls.OSRM_BASE_URL}{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"OSRM API xatosi: {response.status}")
                        return {"error": "Yo'nalish topilmadi"}
                    
                    data = await response.json()
                    
                    if data.get('code') != 'Ok':
                        return {"error": data.get('message', 'Nomalum xatolik yuz berdi')}
                    
                    # Faqat kerakli ma'lumotlarni qaytaramiz
                    route = data['routes'][0]
                    return {
                        "distance": route['distance'],  # metrda
                        "duration": route['duration'],  # sekundda
                        "geometry": route['geometry']   # GeoJSON LineString
                    }
                    
        except Exception as e:
            logger.error(f"Xarita xizmatida xatolik: {str(e)}")
            return {"error": f"Xarita xizmatida xatolik: {str(e)}"}
    
    @staticmethod
    def calculate_eta(distance: float, avg_speed_kmh: float = 30.0) -> int:
        """Masofaga qarab yetib borish vaqtini hisoblash"""
        # avg_speed_kmh - o'rtacha tezlik km/soat
        if distance <= 0 or avg_speed_kmh <= 0:
            return 0
            
        # Masofani km ga o'tkazamiz va soatga bo'lamiz
        hours = (distance / 1000) / avg_speed_kmh
        return int(hours * 60)  # daqiqalarga aylantiramiz
