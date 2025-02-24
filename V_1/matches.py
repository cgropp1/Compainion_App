import os as _os
import json as _json
import gzip as _gzip
from typing import List, Tuple
from src.user import User

class Match:
    def __init__(self, _match_JSON: dict = None, match_tuple: Tuple[User, User, int] = None):
        if _match_JSON:
            self.from_dict(_match_JSON)
        elif match_tuple:
            self.user1, self.user2, self.outcome = match_tuple

    def from_dict(self, _match_JSON: dict):
        self.user1 = User(_user_id=_match_JSON["user1_id"], _user_name=_match_JSON["user1_name"])
        self.user2 = User(_user_id=_match_JSON["user2_id"], _user_name=_match_JSON["user2_name"])
        self.outcome = _match_JSON["outcome"]

    def to_dict(self) -> dict:
        return {
            "user1_id": self.user1.user_id,
            "user1_name": self.user1.user_name,
            "user2_id": self.user2.user_id,
            "user2_name": self.user2.user_name,
            "outcome": self.outcome
        }

    def to_tuple(self) -> Tuple[User, User, int]:
        return (self.user1, self.user2, self.outcome)

class Match_Manager:
    def __init__(self, _apiInterface=None):
        self.apiInterface = _apiInterface
        self.matches: List[Match] = []

        directory = _os.path.join(_os.path.dirname(__file__), 'match_data')
        _os.makedirs(directory, exist_ok=True)

        file_path = _os.path.join(directory, f"match_data.gz")
        if _os.path.exists(file_path):
            with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                self.from_dict(_json.load(file))

    def include_matches(self, _matches: List[Tuple[User, User, int]]) -> None:
        self.matches.extend([Match(match_tuple=match) for match in _matches])

    def to_dict(self) -> dict:
        return {
            "matches": [match.to_dict() for match in self.matches]
        }
    
    def from_dict(self, _match_manager_JSON: dict):
        self.matches = [Match(_match_JSON=match) for match in _match_manager_JSON["matches"]]

    def get_matches_as_tuples(self) -> List[Tuple[User, User, int]]:
        return [match.to_tuple() for match in self.matches]

    def save_to_file(self, file_path: str) -> None:
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

    def load_from_file(self, file_path: str) -> None:
        if _os.path.exists(file_path):
            with _gzip.open(file_path, 'rt', encoding='utf-8') as file:
                data = _json.load(file)
                self.from_dict(data)

    def __str__(self) -> str:
        return str(self.get_matches_as_tuples())