from src import dslParser as _dslParser

class Room_Context:
    """
    This class is a context for the rules engine.
    It provides the necessary information for the rules to evaluate:
    room_design_id: int The type id of the room.
    room_id: int The id of the room.
    room_x: int The x size of the room.
    room_y: int The y size of the room.
    room_row: int The row size of the room.
    room_column: int The column size of the room.
    room_isPowered: bool The power status of the room.
    room_armor: int The armor value of the room.
    room_type: str The type of the room.
    """
    def __init__ (self, _room_id: int, _ship_layout: dict, _room_designs: dict):
        self.room_id = _room_id
        self.rood_design_id = _ship_layout
