import logging
import asyncio as _asyncio
from typing import List, Dict, Any, Optional
from pssapi import PssApiClient, entities

# Get logger for this module
logger = logging.getLogger('pss_companion.apiInterface')

class apiInterface:
    def __init__(self) -> None:
        try:
            self.client = None
            self.access_token = None
            self.device_key = "bdf1c128-1e7e-4a17-8e6e-98fd89e28f68"
            self.checksum_key = 5343
            logger.info("API Interface created")
        except Exception as e:
            logging.error(f'Error in __init__(self):: {e}')
            raise
        pass

    async def init_pss_api_client(self):
        try:
            self.client = PssApiClient()
            user_login = await self.client.device_login(self.device_key, self.checksum_key)
            self.access_token = user_login.access_token
            logger.info("API Interface initialized")
        except Exception as e:
            logging.error(f'Error in init_pss_api_client(self):: {e}')
            raise
        pass

    def get_access_token(self):
        try:
            return self.access_token
        except Exception as e:
            logging.error(f'Error in get_access_token(self):: {e}')
            raise

    async def get_users_by_name(self, names: list[str]) -> List[entities.User]:
        """Get users by name"""
        try:
            # Ensure client is initialized
            if not self.client:
                await self.initialize()

            tasks = [self.client.user_service.search_users(name) for name in names] 
            results = await _asyncio.gather(*tasks)
            users = [user for result in results for user in result] # Flatten the list of lists return users
            return users
        except Exception as e:
            logger.error(f"Error in get_users_by_name(self, names): {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise
            
    async def get_ship_by_user(self, _user: entities.User) -> entities.Ship:
        """Get ship for a user"""
        try:
            # Ensure client is initialized
            if not self.client:
                await self.initialize()
                
            # Implement ship retrieval logic
            logger.info(f"Getting ship for user: {_user.name} (ID: {_user.id})")
            temp_ship, temp_user = await self.client.ship_service.inspect_ship(self.access_token, _user.id)
            return temp_ship
        except Exception as e:
            logger.error(f"Error in get_ship_by_user: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise