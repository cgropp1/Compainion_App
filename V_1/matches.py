import logging

import os as _os
import json as _json
import gzip as _gzip
from typing import List, Tuple
from src.user import User

class Match:
    def __init__(self, _match_JSON: dict = None, match_tuple: Tuple[User, User, int] = None):
        try:
            if _match_JSON:
                self.from_dict(_match_JSON)
            elif match_tuple:
                self.user1, self.user2, self.outcome = match_tuple
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def from_dict(self, _match_JSON: dict):
        try:
            self.user1 = User(_user_id=_match_JSON["user1_id"], _user_name=_match_JSON["user1_name"])
            self.user2 = User(_user_id=_match_JSON["user2_id"], _user_name=_match_JSON["user2_name"])
            self.outcome = _match_JSON["outcome"]
        except Exception as e:
            logging.error(f'Error in from_dict(self,: {e}')
            raise

    def to_dict(self) -> dict:
        try:
            return {
                "user1_id": self.user1.user_id,
                "user1_name": self.user1.user_name,
                "user2_id": self.user2.user_id,
                "user2_name": self.user2.user_name,
                "outcome": self.outcome
            }
        except Exception as e:
            logging.error(f'Error in to_dict(self): {e}')
            raise

    def to_tuple(self) -> Tuple[User, User, int]:
        try:
            return (self.user1, self.user2, self.outcome)
        except Exception as e:
            logging.error(f'Error in to_tuple(self): {e}')
            raise

class Match_Manager:
    def __init__(self, _apiInterface=None):
        try:
            self.apiInterface = _apiInterface
            self.matches: List[Match] = []

            directory = _os.path.join(_os.path.dirname(__file__), 'match_data')
            _os.makedirs(directory, exist_ok=True)

            file_path = _os.path.join(directory, f"match_data.gz")
            if _os.path.exists(file_path):
                with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                    self.from_dict(_json.load(file))
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def include_matches(self, _matches: List[Tuple[User, User, int]]) -> None:
        try:
        except Exception as e:
            logging.error(f'Error in include_matches(self,: {e}')
            raise
        self.matches.extend([Match(match_tuple=match) for match in _matches])

    def to_dict(self) -> dict:
        try:
        except Exception as e:
            logging.error(f'Error in to_dict(self): {e}')
            raise
        return {
            "matches": [match.to_dict() for match in self.matches]
        }
    
    def from_dict(self, _match_manager_JSON: dict):
        try:
        except Exception as e:
            logging.error(f'Error in from_dict(self,: {e}')
            raise
        self.matches = [Match(_match_JSON=match) for match in _match_manager_JSON["matches"]]

    def get_matches_as_tuples(self) -> List[Tuple[User, User, int]]:
        try:
            return [match.to_tuple() for match in self.matches]
        except Exception as e:
            logging.error(f'Error in get_matches_as_tuples(self): {e}')
            raise

    def save_to_file(self, file_path: str) -> None:
        try:
            directory = _os.path.dirname(file_path)
            if directory:
                _os.makedirs(directory, exist_ok=True)

            if _os.path.exists(file_path):
                with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                    previous_data = _json.load(file)
                    previous_data["matches"].extend(self.to_dict()["matches"])
            else:
                previous_data = self.to_dict()

            with _gzip.open(file_path, 'wt', encoding='utf-8') as file:
                _json.dump(previous_data, file, indent=4)
        except Exception as e:
            logging.error(f'Error in save_to_file(self,: {e}')
            raise

    def load_from_file(self, file_path: str) -> None:
        try:
            if _os.path.exists(file_path):
                with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                    data = _json.load(file)
                    self.from_dict(data)
        except Exception as e:
            logging.error(f'Error in load_from_file(self,: {e}')
            raise

    def __str__(self) -> str:
        try:
            return str(self.get_matches_as_tuples())
        except Exception as e:
            logging.error(f'Error in __str__(self): {e}')
            raise