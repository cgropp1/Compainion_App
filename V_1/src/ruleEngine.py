from src import dslParser as _dslParser
from src import room as _Room
from src import user as _User

class apiInterface:
    pass
    
class RuleEngine:

    def __init__(self, api_interface: apiInterface,  rules_file: str, user_file: str = None, user: _User.User = None) -> None:
        self.rules = _dslParser.parse_dsl_file(rules_file)
        print(f"Generated user using user_file: {'Yes' if user_file else 'No'}, user: {'Yes' if user else 'No'}")
        if user_file:
            self.user = _User.User(api_interface)
            self.user.from_file(user_file)
        else:
            self.user = user
        self.rooms = self.user.rooms
        self.ship_armor_value = self.user.to_dict_dated_data()["user_ship"]["ship_armor_value"]

    def evaluate_room(self, room: _Room.Room) -> tuple[str, str, int]:
        print(f"Evaluating rules for room: {room.short_name}")
        for rule in self.rules:
            if eval(rule.condition):
                if rule.actions[0][0] == "penalty":
                    print([room.short_name, rule.actions[0][1], rule.actions[1][1]])
                    return [room.short_name, rule.actions[0][1], rule.actions[1][1]]
                else:
                    print([room.short_name, rule.actions[1][1], rule.actions[0][1]])
                    return [room.short_name, rule.actions[1][1], rule.actions[0][1]]
        return [room.short_name, 0, "No Rule Triggered"]

    def evaluate_all_rooms(self) -> tuple[int, list[tuple[str, int, str]]]:
        score = 0
        evaluations = []
        for room in self.rooms:
            if room.type == "Wall" or room.type == "Lift" or room.type == "Corridor":
                continue
            evaluations.append(self.evaluate_room(room))
            score += evaluations[-1][1]
        return score, evaluations




