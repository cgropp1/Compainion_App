import asyncio as _asyncio
import json as _json
import os as _os
import gzip as _gzip
from datetime import datetime as _datetime, timedelta as _timedelta
from pssapi import entities as _entities

from src import ship as _Ship

# Soft dependency on apiInterface
class apiInterface:
    pass

class User:
    def __init__(self, _api_interface: apiInterface, _user: _entities.User = None, _designs: dict = None) -> None:
        if _user and _designs:
            self.user_id = _user.id
            self.user_name = _user.name
            self.user = {
                "user_id": _user.id,
                "user_name": _user.name,
                "dated_data": 
                [
                    {
                    "date": _datetime.now().isoformat(),
                    "highest_trophy": _user.highest_trophy,
                    "user_ship": _Ship.Ship(_ship=_api_interface.get_ship_by_user(_user = _user), _designs=_designs).to_dict()
                    }
                ]
            }
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
        print(new_data)

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
                previous_data = _json.load(file)
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
            data = _json.load(file)

        self.from_dict(data)

    def __repr__(self) -> str:
        return self.to_dict()
    
    def __str__(self) -> str:
        return self.__repr__()