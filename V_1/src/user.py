import asyncio as _asyncio
import json as _json
import os as _os
import gzip as _gzip
import logging
from datetime import datetime as _datetime, timedelta as _timedelta
from pssapi import entities as _entities

from src import ship as _Ship
from src import room as _Room
from src import apiInterface as _apiInterface
from src import fileManager as _fileManager

# Get logger for this module
logger = logging.getLogger('pss_companion.user')

class User:
    def __init__(self) -> None:
        self.user_id = None
        self.user_name = None
        self.design = None
        self.ship = None
        self.user = None
        logger.info("User object created")

    @classmethod
    async def create(cls, _api_interface, _user, room_designs=None, ship_designs=None):
        """Factory method to create and initialize a User object asynchronously"""
        # Create instance with minimal init
        instance = cls()
        # Initialize it properly
        await instance.init_user(_api_interface, _user, room_designs, ship_designs)
        return instance

    async def init_user(self, _api_interface: _apiInterface.apiInterface, _user: _entities.User, room_designs: dict, ship_designs: dict) -> None:
        try:
            if _user and room_designs and ship_designs:
                try:
                    self.user_id = _user.id
                    self.user_name = _user.name
                    self.ship = await _api_interface.get_ship_by_user(_user = _user)
                    self.design = ship_designs.get(str(self.ship.ship_design_id), None)
                    logger.info(f"Found design for user {self.user_name}: {'Yes' if self.design else 'No'}")
                    self.ship = _Ship.Ship(_ship = self.ship, _room_designs=room_designs, _ship_design = self.design)
                    self.user = {
                        "user_id": _user.id,
                        "user_name": _user.name,
                        "dated_data": 
                        [
                            {
                            "date": _datetime.now().isoformat(),
                            "highest_trophy": _user.highest_trophy,
                            "user_ship": self.ship.to_dict()
                            }
                        ]
                    }
                    logger.debug(f"User ship data initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing user with full data: {e}")
                    raise
            elif _user:
                try:
                    self.user_id = _user.id
                    self.user_name = _user.name
                    logger.info(f"Initialized user {self.user_name} with basic data only")
                except Exception as e:
                    logger.error(f"Error initializing user with basic data: {e}")
                    raise
            else:
                self.user = None
                logger.warning("User initialized without data")
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def set_name(self, _user_name: str) -> None:
        try:
            self.user_name = _user_name
            logger.debug(f"User name set to {_user_name}")
        except Exception as e:
            logging.error(f'Error in set_name(self,: {e}')
            raise

    def set_id(self, _user_id: int) -> None:
        try:
            self.user_id = _user_id
            logger.debug(f"User ID set to {_user_id}")
        except Exception as e:
            logging.error(f'Error in set_id(self,: {e}')
            raise

    def soft_init(self, _user_id: int, _user_name: str) -> None:
        try:
            self.set_id(_user_id)
            self.set_name(_user_name)
            logger.info(f"Soft initialized user {_user_name} (ID: {_user_id})")
        except Exception as e:
            logging.error(f'Error in soft_init(self,: {e}')
            raise

    def to_dict(self) -> dict:
        try:
            return self.user
        except Exception as e:
            logging.error(f'Error in to_dict(self): {e}')
            raise

    def from_dict(self, _user: dict) -> None:
        try:
            self.user = _user
            logger.debug("User data loaded from dictionary")
        except Exception as e:
            logging.error(f'Error in from_dict(self,: {e}')
            raise

    def to_dict_dated_data(self) -> list:
        try:
            return self.user["dated_data"][-1]
        except Exception as e:
            logging.error(f'Error in to_dict_dated_data(self): {e}')
            raise
    
    def to_file(self, _fileManager: _fileManager.FileManager, check_time: bool = True, file_path: str = None) -> None:
        try:
            new_data = self.to_dict_dated_data()
            logger.info(f"Preparing to save user data to file")

            if file_path:
                if not file_path.endswith(".gz"):
                    file_path += ".gz"
                    logger.info(f"Using provided file path: {file_path}")
            else:
                file_path = f"{self.user_name}_{self.user_id}.gz"
                logger.info(f"Using default file path: {file_path}")

            file_path = f"usr_data/{file_path}"
            logger.debug(f"Final file path: {file_path}")

            if _fileManager:
                logger.info("Using provided file manager")
                if _fileManager.create_dir("usr_data"):
                    previous_data = _fileManager.load_gzip_json(filepath=file_path)
                    if previous_data:
                        logger.info("Successfully loaded previous data")
                        logger.info("Checking if data should be appended")
                        logger.debug(f"Previous data: {previous_data}")
                        previous_dates = [data["date"] for data in previous_data["dated_data"]]
                        most_recent_date = max(previous_dates)
                        most_recent_datetime = _datetime.fromisoformat(most_recent_date)
                        current_datetime = _datetime.now()
                    
                        if current_datetime - most_recent_datetime < _timedelta(minutes=1) and check_time:
                            logger.info("Data not appended - less than 1 minute since the last entry")
                            return
                    elif previous_data is None:
                        logger.info("No previous data found: Creating new data structure")
                        previous_data = self.to_dict()
                    else:
                        raise ValueError("Error loading previous data")
                    
                    previous_data["dated_data"].append(new_data)
                    logger.info("Appended new data to existing file")

                    logger.info(f"Saving user data to {_fileManager.save_gzip_json(data=previous_data, filepath=file_path)}")
            else:
                raise ValueError("No file manager provided")         
        except Exception as e:
            logger.error(f"Error saving user data to file: {e}")
            raise

    def from_file(self, _file_path: str) -> None:
        try:
            directory = _os.path.join(_os.path.dirname(__file__), '..', 'user_data')
            file_path = _file_path if _file_path else _os.path.join(directory, f"{self._user_name}_{self._user_id}.gz")

            if not _os.path.exists(file_path):
                logger.warning(f"No data file found at {file_path}")
                return

            with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                try:
                    data = _json.load(file)
                    logger.debug(f"Successfully loaded data from file")
                except _json.JSONDecodeError as e:
                    logger.error(f"Error loading JSON data: {e}")
                    data = None

            if data:
                self.from_dict(data)
                logger.info(f"Successfully loaded user data from {file_path}")
            else:
                logger.warning("No user data loaded - JSON data was empty or invalid")
                
        except Exception as e:
            logger.error(f"Error loading user data from file: {e}")
            raise

    @property
    def rooms(self) -> list[_Room.Room]:
        logger.debug(f"Retrieving rooms from user data")
        try:
            rooms = self.ship.shipRooms            
            logger.debug(f"Retrieved {len(rooms)} rooms from user ship")
            return rooms
        except Exception as e:
            logger.error(f"Error retrieving rooms from user data: {e}")
            return []

    def __repr__(self) -> str:
        try:
            return str(self.to_dict())
        except Exception as e:
            logging.error(f'Error in __repr__(self): {e}')
            raise
    
    def __str__(self) -> str:
        try:
            return self.__repr__()
        except Exception as e:
            logging.error(f'Error in __str__(self): {e}')
            raise