"""KOPIS (Korean Performing Arts Information System) API Service"""

from typing import Dict, List, Any
import requests
import xmltodict
from fastapi import HTTPException

from app.core.config import settings


class KopisService:
    """Service for interacting with KOPIS API"""

    BASE_URL = "http://www.kopis.or.kr/openApi/restful"

    def __init__(self):
        self.api_key = settings.kopis_api_key

    def get_concerts(
        self,
        stdate: str,
        eddate: str,
        cpage: int = 1,
        rows: int = 20,
        shcate: str = "CCCD"  # CCCD = 대중음악
    ) -> Dict[str, Any]:
        """
        Fetch concert listings from KOPIS API

        Args:
            stdate: Start date (YYYYMMDD format)
            eddate: End date (YYYYMMDD format)
            cpage: Page number (default: 1)
            rows: Results per page (default: 20)
            shcate: Genre code (default: CCCD for popular music)

        Returns:
            Dict containing metadata, raw response, and normalized items
        """
        url = f"{self.BASE_URL}/pblprfr"
        params = {
            "service": self.api_key,
            "stdate": stdate,
            "eddate": eddate,
            "cpage": str(cpage),
            "rows": str(rows),
            "shcate": shcate,
        }

        try:
            response = requests.get(url, params=params, timeout=15)
        except requests.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"KOPIS request failed: {e}"
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"KOPIS upstream returned {response.status_code}"
            )

        try:
            parsed = xmltodict.parse(response.text)
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Failed to parse KOPIS XML response"
            )

        # Extract items from response
        dbs = parsed.get("dbs", {})
        items = dbs.get("db", [])

        # Handle single item case (KOPIS returns dict instead of list)
        if isinstance(items, dict):
            items = [items]

        # Normalize items for frontend consumption
        normalized = self._normalize_items(items)

        return {
            "meta": {
                "cpage": cpage,
                "rows": rows,
                "stdate": stdate,
                "eddate": eddate,
                "shcate": shcate
            },
            "raw": parsed,
            "items": normalized
        }

    def _normalize_items(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize KOPIS items to a consistent format"""
        return [
            {
                "mt20id": item.get("mt20id"),
                "prfnm": item.get("prfnm"),
                "prfpdfrom": item.get("prfpdfrom"),
                "prfpdto": item.get("prfpdto"),
                "fcltynm": item.get("fcltynm"),
                "poster": item.get("poster"),
                "genrenm": item.get("genrenm"),
                "area": item.get("area"),
                "openrun": item.get("openrun"),
            }
            for item in items
        ]

    def get_concert_detail(self, mt20id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific concert
        (To be implemented when needed)

        Args:
            mt20id: Concert ID from KOPIS

        Returns:
            Detailed concert information
        """
        # TODO: Implement concert detail endpoint
        raise NotImplementedError("Concert detail endpoint not yet implemented")


# Global service instance
kopis_service = KopisService()
