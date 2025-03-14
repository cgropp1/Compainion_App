from datetime import datetime as _datetime
from pssapi import entities as _entities
import json as _json

from src import room as _Room

essensal_rooms = [
    "Shield",
    "Engine",
    "Stealth",
    "Teleport",
    "Android"
]

class Ship:
    """
    This class is used to hold the data for a ship at a spesific datetime.
    ship_datetime: datetime The datetime of the ship.
    ship_design_id: int The type id of the ship.
    ship_id: int The id of the ship.
    ship_rooms: List[Room] The rooms on the ship.
    ship_power: int The power of the ship.
    ship_maxCrew: int The max number of crew that can be held.
    ship_crew: List[Crew] The crew on the ship.
    """

    def __init__(self, _ship: _entities.Ship = None, _designs: dict = None) -> None:
        if _ship and _designs:
            #print(_designs)
            
            self.shipRooms = []
            self.shipArmor = []
            for room in _ship.rooms:
                print(f"Room Design ID: {room.room_design_id}")
                design = _designs.get(str(room.room_design_id), None)
                if design is None:
                    print(f"Design not found for Room Design ID: {room.room_design_id}, room name: {room.upgrade_room_design_id}")
                else:
                    print(f"Design found for Room Design ID: {room.room_design_id}: {design}")
                    self.shipRooms.append(_Room.Room(_essensal_rooms = essensal_rooms, _room = room, _design = design))
                    if self.shipRooms[-1].getType() == "Wall":
                        self.shipArmor.append(self.shipRooms[-1])
                        

            self.ship = {
                #"""PER DATE"""#
                "ship_datetime": str(_datetime.now()),
                "ship_design_id": _ship.ship_design_id,
                "ship_id": _ship.id,
                
                #"""PER LAYOUT"""#
                "ship_rooms": [room.to_dict() for room in self.shipRooms],
            }
            for armor in self.shipArmor:
                for room in self.getAjacentRooms(armor):
                    room.setArmor(armor)
        else:
            self.ship = None

        

    def getAjacentRooms(self, _room: _Room.Room) -> list[_Room.Room]:
        ajacentRooms = []
        for room in self.shipRooms:
            if room.isAjacent(_room):
                ajacentRooms.append(room)
        return ajacentRooms
    
    def to_dict(self) -> dict:
        return self.ship
    
    def from_dict(self, _ship: dict) -> None:
        self.ship = _ship

    def __repr__(self) -> str:
        return self.to_dict()
    
    def __str__(self) -> str:
        return self.__repr__()