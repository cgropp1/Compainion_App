import pandas as _pandas
from sklearn.model_selection import train_test_split as _train_test_split
from sklearn.ensemble import RandomForestClassifier as _RandomForestClassifier
from sklearn.metrics import accuracy_score as _accuracy_score
from typing import List, Tuple

from src.user import User
from src.apiInterface import apiInterface

class Agent:
    def __init__(self, _api_interface: apiInterface):
        self.api_interface = _api_interface
        self.matches: List[Tuple[User, User, int]] = []

    def include_matches(self, _matches: List[Tuple[User, User, int]]) -> None:
        for match in _matches:
            user1, user2, outcome = match
            self.matches.append([user1, user2, outcome])
            inverse_outcome = 1 if outcome == 0 else 0 if outcome == 1 else 2
            self.matches.append([user2, user1, inverse_outcome])

    def flatten_dict(self, d: dict, parent_key: str = '', sep: str = '_') -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(self.flatten_dict({f"{k}_{i}": item}, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def train(self) -> None:
        X = []
        y = []

        for user1, user2, outcome in self.matches:
            user1_features = self.flatten_dict(user1.get_dict())
            user2_features = self.flatten_dict(user2.get_dict())
            combined_features = {**user1_features, **{f"user2_{k}": v for k, v in user2_features.items()}}
            X.append(combined_features)
            y.append(outcome)

        X = _pandas.DataFrame(X)
        y = _pandas.Series(y)

        # One-hot encode categorical features
        X = _pandas.get_dummies(X)

        X_train, X_test, y_train, y_test = _train_test_split(X, y, test_size=0.2, random_state=42)

        clf = _RandomForestClassifier(random_state=0)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        print(_accuracy_score(y_test, y_pred))

    def predict(self, user1: User, user2: User) -> int:
        user1_features = self.flatten_dict(user1.get_dict())
        user2_features = self.flatten_dict(user2.get_dict())
        combined_features = {**user1_features, **{f"user2_{k}": v for k, v in user2_features.items()}}
        X = _pandas.DataFrame([combined_features])

        # One-hot encode categorical features
        X = _pandas.get_dummies(X)

        clf = _RandomForestClassifier(random_state=0)
        clf.fit(X, [0])  # Dummy fit to avoid error, replace with actual model
        prediction = clf.predict(X)
        return prediction[0]