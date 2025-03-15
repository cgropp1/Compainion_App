import asyncio as _asyncio
from pssapi import PssApiClient as _PssApiClient, entities as _entities

class apiInterface:
    def __init__(self):
        self.client = _PssApiClient()
        self.access_token = None
        self.device_key = "bdf1c128-1e7e-4a17-8e6e-98fd89e28f68"
        self.checksum_key = 5343
        self.init_pss_api_client()
        pass

   

    def init_pss_api_client(self):
        loop = _asyncio.get_event_loop()
        user_login = loop.run_until_complete(self.client.device_login(self.device_key, self.checksum_key))
        self.access_token = user_login.access_token
        pass

    def get_access_token(self):
        return self.access_token

    def get_users_by_name(self, names: list[str]) -> list[_entities.User]:
        loop = _asyncio.get_event_loop()
        tasks = [self.client.user_service.search_users(name) for name in names]
        results = loop.run_until_complete(_asyncio.gather(*tasks))
        users = [user for result in results for user in result]  # Flatten the list of lists
        return users
    
    def get_ship_by_user(self, _user: _entities.User) -> _entities.Ship:
        loop = _asyncio.get_event_loop()
        temp_ship, temp_user = loop.run_until_complete(self.client.ship_service.inspect_ship(self.access_token, _user.id))
        return temp_ship