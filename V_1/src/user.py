import asyncio as _asyncio
import json as _json
import os as _os
import gzip as _gzip
from datetime import datetime as _datetime, timedelta as _timedelta
from pssapi import entities as _entities

from src import ship as _Ship
from src import room as _Room
from src import apiInterface as _apiInterface

class User:
    def __init__(self, _api_interface: _apiInterface.apiInterface, _user: _entities.User = None, room_designs: dict = None, ship_designs:dict = None) -> None:
        if _user and room_designs and ship_designs:
            self.user_id = _user.id
            self.user_name = _user.name
            self.design = ship_designs.get(str(_api_interface.get_ship_by_user(_user = _user).ship_design_id), None)
            print(f"Found design: {'Yes' if self.design else 'No'}")
            self.user = {
                "user_id": _user.id,
                "user_name": _user.name,
                "dated_data": 
                [
                    {
                    "date": _datetime.now().isoformat(),
                    "highest_trophy": _user.highest_trophy,
                    "user_ship": _Ship.Ship(_ship = _api_interface.get_ship_by_user(_user = _user), _room_designs=room_designs, _ship_design = self.design).to_dict()
                    }
                ]
            }
            # print(f"user_ship data: {self.user['dated_data'][-1]['user_ship']}")  # Debugging output
        elif _user:
            self.user_id = _user.id
            self.user_name = _user.name           
        else:
            self.user = None

    def set_name(self, _user_name: str) -> None:
        self.user_name = _user_name

    def set_id(self, _user_id: int) -> None:
        self.user_id = _user_id

    def soft_init(self, _user_id: int, _user_name: str) -> None:
        self.set_id(_user_id)
        self.set_name(_user_name)

    def to_dict(self) -> dict:
        return self.user
    
    def from_dict(self, _user: dict) -> None:
        self.user = _user

    def to_dict_dated_data(self) -> list:
        return self.user["dated_data"][-1]
    
    def to_file(self, check_time: bool = True, file_path: str = None) -> None:
        new_data = self.to_dict_dated_data()
        #print(f"New data to be saved: {new_data}")  # Debugging output

        if not file_path:
            # Ensure the directory exists
            directory = _os.path.join(_os.path.dirname(__file__), '..', 'user_data')
            _os.makedirs(directory, exist_ok=True)

            file_path = _os.path.join(directory, f"{self.user_name}_{self.user_id}.gz")

        else:
            if not file_path.endswith(".gz"):
                file_path += ".gz"
            directory = _os.path.dirname(file_path)
            _os.makedirs(directory, exist_ok=True)

        if _os.path.exists(file_path):
            with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                try:
                    previous_data = _json.load(file)
                except _json.JSONDecodeError as e:
                    print(f"Error loading JSON data: {e}")
                    previous_data = {"dated_data": []}
                previous_dates = [data["date"] for data in previous_data["dated_data"]]
                most_recent_date = max(previous_dates)
                most_recent_datetime = _datetime.fromisoformat(most_recent_date)
                current_datetime = _datetime.now()

                if current_datetime - most_recent_datetime < _timedelta(minutes=1) and check_time:
                    print("Data not appended. Less than 30 minutes since the last entry.")
                    return

            previous_data["dated_data"].append(new_data)
        else:
            previous_data = self.to_dict()

        with _gzip.open(file_path, 'wt', encoding='utf-8') as file:
            _json.dump(previous_data, file)

    def from_file(self, _file_path: str) -> None:
        directory = _os.path.join(_os.path.dirname(__file__), '..', 'user_data')
        file_path = _file_path if _file_path else _os.path.join(directory, f"{self._user_name}_{self._user_id}.gz")

        if not _os.path.exists(file_path):
            print("No data found for this user.")
            return

        with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
            try:
                data = _json.load(file)
                #print(f"Loaded data: {data}")  # Debugging output
            except _json.JSONDecodeError as e:
                print(f"Error loading JSON data: {e}")
                data = None

        if data:
            self.from_dict(data)

    @property
    def rooms(self) -> list[_Room.Room]:
        rooms = []
        user_ship = self.to_dict_dated_data().get("user_ship", {})
        #print(f"user_ship in rooms property: {user_ship}")  # Debugging output
        ship_rooms = user_ship.get("ship_rooms", [])
        for room in ship_rooms:
            if room:  # Ensure room data is not None
                _room = _Room.Room()
                _room.from_dict(room)
                rooms.append(_room)
        return rooms

    def __repr__(self) -> str:
        return str(self.to_dict())
    
    def __str__(self) -> str:
        return self.__repr__()