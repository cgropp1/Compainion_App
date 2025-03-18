from pssapi import entities as _entities
import json as _json
import logging

# Get logger for this module
logger = logging.getLogger('pss_companion.room')

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
        try:
            if _room and _design:
                try:
                    roomIsUpgrading = _room.room_status == "Upgrading"
                    roomIsPowered = _design.get('MaxSystemPower', 0) > 0 or _design.get('MaxPowerGenerated', 0) > 0
                    roomShortname = _design.get('RoomShortName', None).split(':')[0] if _design.get('RoomShortName', None) else None
                    roomNumCrew = _design.get('Capacity', 0) if roomShortname == "Bedroom" else 0
                    roomPower = _design.get('MaxPowerGenerated', 0) if _design.get('MaxPowerGenerated', 0) != 0 else -1*_design.get('MaxSystemPower', 0)
                    roomArmorAbl = _design.get('Capacity', 0) if _design.get('RoomType') == "Wall" else 0
                    if _design.get('RoomType') == "Wall" and roomArmorAbl == 0:
                        logger.warning(f"Wall with no armor ability: {_design}")

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
                        "room_size": (_design.get('Columns', None), _design.get('Rows', None)),
                        "room_isPowered": roomIsPowered,
                        "room_short_name": roomShortname,
                        "room_essential": roomIsEssential,
                        "room_numCrew": roomNumCrew,
                        "room_Power": roomPower,
                        #"""PER SHIP LAYOUT"""
                        "room_armor": 0,
                        "room_armor_abl": roomArmorAbl
                    }
                    logger.debug(f"Room {roomShortname} ({_room.id}) initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing room: {str(e)}")
                    self.room = None
            else:
                self.room = None
                logger.warning(f"Room initialization failed: _room is {_room}, _design is {_design}")
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def to_dict(self) -> dict:
        try:
            return self.room
        except Exception as e:
            logging.error(f'Error in to_dict(self): {e}')
            raise

    def from_dict(self, _room: dict) -> None:
        try:
            self.room = _room
            logger.debug(f"Room loaded from dict, ID: {self.room.get('room_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Error loading room from dict: {e}")
            raise

    def getNumCrew(self) -> int:
        try:
            return self.room["room_numCrew"]
        except Exception as e:
            logging.error(f'Error in getNumCrew(self): {e}')
            raise

    def getPower(self) -> int:
        try:
            return self.room["room_Power"]    
        except Exception as e:
            logging.error(f'Error in getPower(self): {e}')
            raise
    
    def getType(self) -> str:
        try:
            return self.room["room_type"]
        except Exception as e:
            logging.error(f'Error in getType(self): {e}')
            raise

    def isAjacent(self, _room: 'Room') -> bool:
        try:
            x1, y1 = self.room["room_cords"]
            width1, height1 = self.room["room_size"]
            x2, y2 = _room.room["room_cords"]
            width2, height2 = _room.room["room_size"]

            if (x1 == x2 + width2 or x1 + width1 == x2) and (y1 < y2 + height2 and y1 + height1 > y2):
                return True
            if (y1 == y2 + height2 or y1 + height1 == y2) and (x1 < x2 + width2 and x1 + width1 > x2):
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking if rooms are adjacent: {e}")
            return False

    def setArmor(self, _armorRoom: 'Room'):
        try:
            room_name = self.room.get('room_short_name', 'None')
            room_armor = self.room['room_armor']
            armor_ability = _armorRoom.room['room_armor_abl']
            new_armor = room_armor + armor_ability
            armor_room_id = _armorRoom.room['room_id']
            
            logger.debug(f"Setting armor for room {room_name} to {room_armor} + {armor_ability} = {new_armor} from {armor_room_id}")
            self.room["room_armor"] += _armorRoom.room["room_armor_abl"]
        except Exception as e:
            logger.error(f"Error setting armor: {e}")

    @property
    def design_id(self) -> int:
        try:
            return self.room["room_design_id"]
        except Exception as e:
            logging.error(f'Error in design_id(self): {e}')
            raise

    @property
    def power(self) -> int:
        try:
            return self.room["room_Power"]
        except Exception as e:
            logging.error(f'Error in power(self): {e}')
            raise
    
    @property
    def num_crew(self) -> int:
        try:
            return self.room["room_numCrew"]
        except Exception as e:
            logging.error(f'Error in num_crew(self): {e}')
            raise
    
    @property
    def powered(self) -> bool:
        try:
            return self.room["room_isPowered"]
        except Exception as e:
            logging.error(f'Error in powered(self): {e}')
            raise
    
    @property
    def armor(self) -> int:
        try:
            return self.room["room_armor"]
        except Exception as e:
            logging.error(f'Error in armor(self): {e}')
            raise

    @property
    def type(self) -> str:
        try:
            return self.room["room_type"]
        except Exception as e:
            logging.error(f'Error in type(self): {e}')
            raise

    @property
    def short_name(self) -> str:
        try:
            return self.room["room_short_name"]
        except Exception as e:
            logging.error(f'Error in short_name(self): {e}')
            raise

    @property
    def essential(self) -> bool:
        try:
            return self.room["room_essential"]
        except Exception as e:
            logging.error(f'Error in essential(self): {e}')
            raise
    
    @property
    def size(self) -> tuple[int, int]:
        try:
            return self.room["room_size"]
        except Exception as e:
            logging.error(f'Error in size(self): {e}')
            raise
    
    @property
    def id(self) -> int:
        try:
            return self.room["room_id"]
        except Exception as e:
            logging.error(f'Error in id(self): {e}')
            raise

    def __repr__(self) -> str:
        try:
            return str(self.to_dict())
        except Exception as e:
            logging.error(f'Error in __repr__(self): {e}')
            raise
    
    def __str__(self) -> str:
        try:
            return self.__repr__()
        except Exception as e:
            logging.error(f'Error in __str__(self): {e}')
            raise