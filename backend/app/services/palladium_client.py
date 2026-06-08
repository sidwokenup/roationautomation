import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = logging.getLogger(__name__)

class PalladiumAPIError(Exception):
    pass

class PalladiumClient:
    def __init__(self):
        self.base_url = settings.PALLADIUM_API_URL
        self.headers = {
            "Authorization": f"Bearer {settings.PALLADIUM_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, verify=False) # verify=False for self-signed or test

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _post(self, endpoint: str, payload: dict):
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error {exc.response.status_code} while requesting {exc.request.url}.")
            raise PalladiumAPIError(f"API Error: {exc.response.text}")
        except Exception as exc:
            logger.error(f"Error requesting {url}: {exc}")
            raise PalladiumAPIError(f"Request failed: {exc}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error {exc.response.status_code} while requesting {exc.request.url}.")
            raise PalladiumAPIError(f"API Error: {exc.response.text}")
        except Exception as exc:
            logger.error(f"Error requesting {url}: {exc}")
            raise PalladiumAPIError(f"Request failed: {exc}")

    async def create_campaign(self, campaign_data: dict):
        return await self._post("/v1/campaign/createCampaign", campaign_data)

    async def update_campaign(self, campaign_data: dict):
        return await self._post("/v1/campaign/saveCampaign", campaign_data)

    async def get_campaign(self, campaign_id: int):
        return await self._get(f"/v1/campaign/getCampaignById", params={"company": campaign_id})

    async def close(self):
        await self.client.aclose()