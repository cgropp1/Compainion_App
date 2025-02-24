import asyncio as _asyncio
import json as _json
import os as _os
import gzip as _gzip
from datetime import datetime as _datetime, timedelta as _timedelta
from pssapi import entities as _entities

# Soft dependency on apiInterface
class apiInterface:
    pass

class Room:
    def __init__(self, _room: _entities.Room = None, _room_JSON: dict = None) -> None:
        if _room:
            self.id = _room.id
            self.skin_id = _room.current_skin_key
            self.row = _room.row
            self.column = _room.column
            self.item_ids = _room.item_ids
            self.isUpgrading = _room.room_status == "Upgrading"
        elif _room_JSON:
            self.from_dict(_room_JSON)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "skin_id": self.skin_id,
            "row": self.row,
            "column": self.column,
            "item_ids": self.item_ids,
            "isUpgrading": self.isUpgrading
        }

    def from_dict(self, _room_JSON: dict):
        self.id = _room_JSON["id"]
        self.skin_id = _room_JSON["skin_id"]
        self.row = _room_JSON["row"]
        self.column = _room_JSON["column"]
        self.item_ids = _room_JSON["item_ids"]
        self.isUpgrading = _room_JSON["isUpgrading"]

class Ship:
    def __init__(self, _ship: _entities.Ship = None, _ship_JSON: dict = None) -> None:
        self.rooms = []
        if _ship:
            self.ship_design_id = _ship.ship_design_id
            for room in _ship.rooms:
                self.rooms.append(Room(room))
        elif _ship_JSON:
            self.from_dict(_ship_JSON)

    def get_ship_design_id(self):
        return self.ship_design_id

    def to_dict(self) -> dict:
        return {
            "ship_design_id": self.ship_design_id,
            "rooms": [room.get_dict() for room in self.rooms]
        }

    def from_dict(self, _ship_JSON: dict):
        self.ship_design_id = _ship_JSON["ship_design_id"]
        for room_JSON in _ship_JSON["rooms"]:
            self.rooms.append(Room(_room_JSON=room_JSON))

class User:
    def __init__(self, _api_interface: apiInterface, _user: _entities.User = None, _user_id: int = None, _user_name: str = None, _date: _datetime = None) -> None:
        if _user:
            self._user_id = _user.id
            self._user_name = _user.name
            self._highest_trophy = _user.highest_trophy

            loop = _asyncio.new_event_loop()
            temp_ship, temp_user = loop.run_until_complete(_api_interface.client.ship_service.inspect_ship(_api_interface.access_token, self._user_id))

            self._user_ship = Ship(temp_ship)
        elif _user_id and _user_name:
            print("Loaded and old User")
            self._user_id = _user_id
            self._user_name = _user_name

            loop = _asyncio.new_event_loop()
            temp_ship, temp_user = loop.run_until_complete(_api_interface.client.ship_service.inspect_ship(_api_interface.access_token, self._user_id))

            self._highest_trophy = temp_user.highest_trophy

            self.from_file(_user_id, _user_name, _date)

    def to_dict(self) -> dict:
        return {
            "date": _datetime.now().isoformat(),
            "highest_trophy": self._highest_trophy,
            "user_ship": {
                "ship_design_id": self._user_ship.get_ship_design_id(),
                "rooms": [
                    {
                        "id": room.id,
                        "skin_id": room.skin_id,
                        "row": room.row,
                        "column": room.column,
                        "item_ids": room.item_ids,
                        "isUpgrading": room.isUpgrading
                    } for room in self._user_ship.rooms
                ]
            }
        }
    
    def to_file(self, check_time: bool = True) -> None:
        print("Saving user data to file.")
        dated_data = self.to_dict()

        # Ensure the directory exists
        directory = _os.path.join(_os.path.dirname(__file__), '..', 'user_data')
        _os.makedirs(directory, exist_ok=True)

        file_path = _os.path.join(directory, f"{self._user_name}_{self._user_id}.gz")

        if _os.path.exists(file_path):
            with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                previous_data = _json.load(file)
                previous_dates = [data["date"] for data in previous_data["dated_data"]]
                most_recent_date = max(previous_dates)
                most_recent_datetime = _datetime.fromisoformat(most_recent_date)
                current_datetime = _datetime.now()

                if current_datetime - most_recent_datetime < _timedelta(hours=6) and check_time:
                    print("Data not appended. Less than 6 hours since the last entry.")
                    return

            previous_data["dated_data"].append(dated_data)
        else:
            previous_data = {
                "user_name": self._user_name,
                "user_id": self._user_id,
                "dated_data": [dated_data]
            }

        with _gzip.open(file_path, 'wt', encoding='utf-8') as file:
            _json.dump(previous_data, file)

    def from_dict(self, _user_JSON: dict, _date: _datetime = None) -> None:
        if _date:
            closest_date = min(_user_JSON["dated_data"], key=lambda x: abs(_datetime.fromisoformat(x["date"]) - _date))
        else:
            closest_date = max(_user_JSON["dated_data"], key=lambda x: _datetime.fromisoformat(x["date"]))

        self.highest_trophy = closest_date["highest_trophy"]
        self.user_ship = Ship(_ship_JSON=closest_date["user_ship"])

    def from_file(self, _user_id: int, _user_name: str, _date: _datetime = None) -> None:
        directory = _os.path.join(_os.path.dirname(__file__), '..', 'user_data')
        file_path = _os.path.join(directory, f"{_user_name}_{_user_id}.gz")

        if not _os.path.exists(file_path):
            print("No data found for this user.")
            return

        with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
            data = _json.load(file)

        self.from_dict(data, _date)

    def __str__(self) -> str:
        return f"User: {self._user_name}, ID: {self._user_id}"