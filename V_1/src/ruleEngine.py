from src import dslParser as _dslParser
from src import room as _Room

class Room_Context:
    """
    This class is a context for the rules engine.
    It provides the necessary information for the rules to evaluate:
    room_design_id: int The type id of the room.
    room_power: int The power of the room.
    room_numCrew: int The number of crew in the room.
    room_isPowered: bool The power status of the room.
    room_armor: int The armor value of the room.
    room_type: str The type of the room.
    room_short_name: str The short name of the room.
    room_essential: bool If the room is essential.
    """
    def __init__(self, _room: _Room.Room) -> None:
        self.design_id = _room.design_id
        self.power = _room.power
        self.num_crew = _room.num_crew
        self.is_powered = _room.is_powered
        self.armor = _room.armor
        self.type = _room.type
        self.short_name = _room.short_name
        self.essential = _room.essential


    
class RuleEngine:
    def evaluate_rules(room_context, user):
    # Parse the ROOM_RULES.dsl file
        rules = _dslParser.parse_dsl_file(r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl")
        print(f"Name of Rules: {rules[0].name}")
