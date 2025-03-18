from datetime import datetime as _datetime
from pssapi import entities as _entities
import json as _json
import logging

from src import room as _Room

# Get logger for this module
logger = logging.getLogger('pss_companion.ship')

essensal_rooms = [
    "Shield",
    "Engine",
    "Stealth",
    "Teleport",
    "Android"
]

armor_value_per_lvl = {
    "1": 2,
    "2": 4,
    "3": 5,
    "4": 6,
    "5": 7,
    "6": 8,
    "7": 9,
    "8": 10,
    "9": 12,
    "10": 14,
    "11": 16,
    "12": 18,
    "13": 18
}

class Ship:
    """
    This class is used to hold the data for a ship at a specific datetime.
    ship_design_id: int The type id of the ship.
    ship_id: int The id of the ship.
    ship_rooms: List[Room] The rooms on the ship.
    ship_power: int The power of the ship.
    ship_maxCrew: int The max number of crew that can be held.
    ship_crew: List[Crew] The crew on the ship.
    """

    def __init__(self, _ship: _entities.Ship = None, _room_designs: dict = None, _ship_design: dict = None) -> None:
        try:
            logger.info("Generating ship")
            logger.debug(f"Ship generated with ship: {'Yes' if _ship else 'No'}, room_designs: {'Yes' if _room_designs else 'No'}, ship_design: {'Yes' if _ship_design else 'No'}")
            
            if _ship and _room_designs and _ship_design:
                try:
                    self.shipRooms = []
                    self.shipArmor = []
                    logger.info(f"Processing {len(_ship.rooms)} rooms")
                    
                    for room in _ship.rooms:
                        try:
                            design = _room_designs.get(str(room.room_design_id), None)
                            if design is None:
                                logger.warning(f"Design not found for Room Design ID: {room.room_design_id}")
                            else:
                                logger.debug(f"Initializing Room with ID: {room.id}, Design ID: {room.room_design_id}")
                                self.shipRooms.append(_Room.Room(_essensal_rooms=essensal_rooms, _room=room, _design=design))
                                if self.shipRooms[-1].getType() == "Wall":
                                    self.shipArmor.append(self.shipRooms[-1])
                                    logger.debug(f"Added armor room with ID: {room.id}")
                        except Exception as e:
                            logger.error(f"Error processing room {room.id}: {e}")
                    
                    logger.info(f"Ship Level: {_ship_design.get('ship_level', None)}")
                    self.shipArmorValue = armor_value_per_lvl.get(str(_ship.ship_level), 0)
                    logger.info(f"Ship armor value per block: {self.shipArmorValue}")

                    self.ship = {
                        #"""PER DATE"""#
                        "ship_design_id": _ship.ship_design_id,
                        "ship_id": _ship.id,
                        "ship_armor_value": self.shipArmorValue,

                        #"""PER LAYOUT"""#
                        "ship_rooms": [room.to_dict() for room in self.shipRooms],
                    }
                    
                    logger.info(f"Setting armor for adjacent rooms. Armor rooms: {len(self.shipArmor)}")
                    for armor in self.shipArmor:
                        adjacent_rooms = self.getAjacentRooms(armor)
                        logger.debug(f"Armor room {armor.id} has {len(adjacent_rooms)} adjacent rooms")
                        for room in adjacent_rooms:
                            room.setArmor(armor)
                            
                    logger.debug(f"Ship initialization complete. Total rooms: {len(self.shipRooms)}")
                except Exception as e:
                    logger.error(f"Error during ship initialization: {e}")
                    raise
            else:
                self.shipRooms = []
                self.ship = None
                logger.warning("Ship initialization failed - missing required parameters")
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def getAjacentRooms(self, _room: _Room.Room) -> list[_Room.Room]:
        try:
            ajacentRooms = []
            for room in self.shipRooms:
                if room.isAjacent(_room):
                    ajacentRooms.append(room)
                    logger.debug(f"Room {room.short_name} ({room.id}) is adjacent to {_room.short_name} ({_room.id})")
            return ajacentRooms
        except Exception as e:
            logger.error(f"Error finding adjacent rooms: {e}")
            return []

    def to_dict(self) -> dict:
        try:
            return self.ship
        except Exception as e:
            logging.error(f'Error in to_dict(self): {e}')
            raise

    def from_dict(self, _ship: dict) -> None:
        try:
            self.ship = _ship
            self.shipRooms = []
            logger.info(f"Loading ship from dict with {len(_ship.get('ship_rooms', []))} rooms")
            
            for room_dict in _ship.get("ship_rooms", []):
                try:
                    room = _Room.Room()
                    room.from_dict(room_dict)
                    self.shipRooms.append(room)
                except Exception as e:
                    logger.error(f"Error loading room from dict: {e}")
        except Exception as e:
            logger.error(f"Error loading ship from dict: {e}")
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