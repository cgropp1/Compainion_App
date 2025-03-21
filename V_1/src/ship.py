from datetime import datetime as _datetime
from pssapi import entities as _entities
import json as _json
import logging

from src import room as _Room
from src import fileManager as _fileManager
from src import config as _config

# Get logger for this module
logger = logging.getLogger('pss_companion.ship')

class lift:
    def __init__(self, _rooms: list[_Room.Room]) -> None:
        try:
            self._type = "LiftOBJ"
            self.rooms = _rooms
        except Exception as e:
            logging.error(f'Error in __init__(self): {e}')
            raise
    
    @property
    def langth(self) -> int:
        try:
            return len(self.rooms)
        except Exception as e:
            logging.error(f'Error in langth(self): {e}')
            raise
    
    @property
    def type(self) -> str:
        try:
            return self._type
        except Exception as e:
            logging.error(f'Error in type(self): {e}')
            raise

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
                    self.ArmorRooms = []
                    self.LiftRooms = []
                    self.Lifts = []
                    logger.info(f"Processing {len(_ship.rooms)} rooms")
                    
                    for room in _ship.rooms:
                        try:
                            design = None
                            if room.room_design_id is not None:
                                # Try as string key first
                                logger.debug(f"Looking up design with string key: {room.room_design_id}")
                                design_id_str = str(room.room_design_id)
                                if design_id_str in _room_designs:
                                    logger.debug(f"Found design with string key: {design_id_str}")
                                    design = _room_designs[design_id_str]
                                    logger.debug(f"Design: {design}")
                                # As a fallback, try direct lookup
                                elif room.room_design_id in _room_designs:
                                    design = _room_designs[room.room_design_id]
                                    logger.debug(f"Found design with direct key: {room.room_design_id}")
                                # Try nested lookup if designs are in "Designs" subkey
                                elif "Designs" in _room_designs and design_id_str in _room_designs["Designs"]:
                                    design = _room_designs["Designs"][design_id_str]
                                    logger.debug(f"Found design with nested key: {design_id_str}")

                            if design is None:
                                logger.warning(f"Design not found for Room Design ID: {room.room_design_id}")
                            else:
                                logger.debug(f"Initializing Room with ID: {room.id}, Design ID: {room.room_design_id}")

                                essensal_rooms = _config.get_essential_rooms()

                                self.shipRooms.append(_Room.Room(_essensal_rooms=essensal_rooms, _room=room, _design=design))
                                if self.shipRooms[-1].getType() == "Wall":
                                    self.ArmorRooms.append(self.shipRooms[-1])
                                    logger.debug(f"Added armor room with ID: {room.id}")
                                if self.shipRooms[-1].getType() == "Lift":
                                    self.LiftRooms.append(self.shipRooms[-1])
                                    logger.debug(f"Added lift room with ID: {room.id}")
                        except Exception as e:
                            logger.error(f"Error processing room {room.id}: {e}")
                    
                    logger.info(f"Ship Level: {_ship_design.get('ship_level', None)}")
                    self.shipArmorValue = _config.get_armor_value(_ship.ship_level)
                    logger.info(f"Ship armor value per block: {self.shipArmorValue}")

                    logger.info(f"Setting armor for adjacent rooms. Armor rooms: {len(self.ArmorRooms)}")
                    for armor in self.ArmorRooms:
                        adjacent_rooms = self.getAjacentRooms(armor)
                        logger.debug(f"Armor room {armor.id} has {len(adjacent_rooms)} adjacent rooms")
                        for room in adjacent_rooms:
                            room.setArmor(armor)


                    # Group lift rooms into vertical lift objects
                    try:
                        logger.info(f"Compiling {len(self.LiftRooms)} lifts into lift objects")
                        
                        # Group lift rooms by their X position
                        lifts_by_x = {}
                        for room in self.LiftRooms:
                            # Get room position from the room object
                            room_x = room.x
                            room_y = room.y
                            
                            # Group by X coordinate (horizontal position)
                            if room_x not in lifts_by_x:
                                lifts_by_x[room_x] = []
                            lifts_by_x[room_x].append(room)
                            logger.debug(f"Adding lift room {room.id} at position ({room_x}, {room_y}) to group")
                        
                        # Create lift objects for each vertical column of lifts
                        self.Lifts = []
                        for x_pos, rooms in lifts_by_x.items():
                            # Sort rooms by Y position (top to bottom)
                            rooms.sort(key=lambda r: r.y)
                            
                            # Create a new lift object with these vertically aligned rooms
                            self.Lifts.append(lift(rooms))
                            logger.debug(f"Created lift at x={x_pos} with {len(rooms)} rooms: {[r.id for r in rooms]}")
                        
                        logger.info(f"Created {len(self.Lifts)} lift objects")
                    except Exception as e:
                        logger.error(f"Error creating lift objects: {e}")
                        import traceback
                        logger.debug(traceback.format_exc())
                    

                    self.ship = {
                        #"""PER DATE"""#
                        "ship_design_id": _ship.ship_design_id,
                        "ship_id": _ship.id,
                        "ship_armor_value": self.shipArmorValue,

                        #"""PER LAYOUT"""#
                        "ship_rooms": [room.to_dict() for room in self.shipRooms],
                    }
                    
                    
                            
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