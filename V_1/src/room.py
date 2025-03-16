from pssapi import entities as _entities
import json as _json

class Room:
    """
    This class will hold all of the data that is needed for a room.
    room_design_id: int The type id of the room.        #THIS ID IS ALWAYS THE SAME ON ANY SHIP FOR THIS ROOM#
    room_id: int The id of the room.                    #THIS ID IS UNIQUE FOR EACH ROOM ON A SHIP#
    room_cords: Tuple[int, int] The x and y cords of the room.
    room_size: Tuple[int, int] The x and y size of the room.
    room_type: str The type of the room.
    room_short_name: str The short name of the room.    #THIS IS THE SHORT NAME W/O THE LEVEL (IE: FRE NOT FRE: 1)#
    room_lvl: int The level of the room.
    room_isPowered: bool The power status of the room.  #IS THE ROOM POWERED (NO MATTER HOW MUCH POWER)#
    room_armor: int The armor value of the room.
    room_isUpgrading: bool The upgrade status of the room.
    room_modules_id: list[int] The modules in the room. #THIS IS A LIST OF MODULE IDS#
    room_essential: bool Is the room essential.         #---THIS IS NOT FROM GAME DATA---#
    room_numCrew: int The number of crew that can be held if it is a bedroom
    room_Power: int The power of the room.              #---THIS IS POSITIVE IF POWER GEN AND NEGATIVE IF POWER CON---#
    """

    def __init__(self, _essensal_rooms: list[str] = None, _room: _entities.Room = None, _design: dict = None) -> None:
        if _room and _design:
            roomIsUpgrading = _room.room_status == "Upgrading"
            roomIsPowered = _design.get('MaxSystemPower', 0) > 0
            roomShortname = _design.get('RoomShortName', None).split(':')[0] if _design.get('RoomShortName', None) else None
            roomNumCrew = _design.get('Capacity', 0) if roomShortname == "Bedroom" else 0
            roomPower = _design.get('MaxPowerGenerated', 0) if _design.get('MaxPowerGenerated', 0) != 0 else -1*_design.get('MaxSystemPower', 0)
            roomArmorAbl = _design.get('Capacity', 0) if _design.get('RoomType') == "Wall" else 0
            roomIsEssential = _design.get("RoomType", None) in _essensal_rooms

            self.room = {
                #"""PER SHIP"""
                #From Room Entity#
                "room_design_id": _room.room_design_id,
                "room_id": _room.id,
                "room_cords": (_room.column, _room.row),
                "modules_id": _room.item_ids, #TODO: make modules have more data?
                "isUpgrading": roomIsUpgrading,
                #From Design Dict#
                "room_lvl": _design.get('Level', None),
                #"""PER ROOM"""
                "room_type": _design.get('RoomType', None),
                "room_size": (_design.get('Rows', None), _design.get('Columns', None)),
                "room_isPowered": roomIsPowered,
                "room_short_name": roomShortname,
                "room_essential": roomIsEssential,
                "room_numCrew": roomNumCrew,
                "room_Power": roomPower,
                #"""PER SHIP LAYOUT"""
                "room_armor": 0,
                "room_armor_abl": roomArmorAbl
            }
        else:
            self.room = None
            # print(f"Room initialization failed: _room is {_room}, _design is {_design}")

    def to_dict(self) -> dict:
        return self.room

    def from_dict(self, _room: dict) -> None:
        self.room = _room

    def getNumCrew(self) -> int:
        return self.room["room_numCrew"]

    def getPower(self) -> int:
        return self.room["room_Power"]    
    
    def getType(self) -> str:
        return self.room["room_type"]

    def isAjacent(self, _room: 'Room') -> bool:
        x1, y1 = self.room["room_cords"]
        width1, height1 = self.room["room_size"]
        x2, y2 = _room.room["room_cords"]
        width2, height2 = _room.room["room_size"]

        if (x1 == x2 + width2 or x1 + width1 == x2) and (y1 < y2 + height2 and y1 + height1 > y2):
            return True
        if (y1 == y2 + height2 or y1 + height1 == y2) and (x1 < x2 + width2 and x1 + width1 > x2):
            return True

        return False

    def setArmor(self, _armorRoom: 'Room'):
        self.room["room_armor"] += _armorRoom.room["room_armor_abl"]

    @property
    def design_id(self) -> int:
        return self.room["room_design_id"]

    @property
    def power(self) -> int:
        return self.room["room_Power"]
    
    @property
    def num_crew(self) -> int:
        return self.room["room_numCrew"]
    
    @property
    def powered(self) -> bool:
        return self.room["room_isPowered"]
    
    @property
    def armor(self) -> int:
        return self.room["room_armor"]

    @property
    def type(self) -> str:
        return self.room["room_type"]

    @property
    def short_name(self) -> str:
        return self.room["room_short_name"]

    @property
    def essential(self) -> bool:
        return self.room["room_essential"]
    
    @property
    def size(self) -> tuple[int, int]:
        return self.room["room_size"]

    def __repr__(self) -> str:
        return str(self.to_dict())
    
    def __str__(self) -> str:
        return self.__repr__()