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
        print("Generating ship")
        print(f"Ship generated with ship: {'Yes' if _ship else 'No'}, room_designs: {'Yes' if _room_designs else 'No'}, ship_design: {'Yes' if _ship_design else 'No'}")
        if _ship and _room_designs and _ship_design:
            self.shipRooms = []
            self.shipArmor = []
            for room in _ship.rooms:
                # print(f"Processing Room ID: {room.id}, Design ID: {room.room_design_id}")
                design = _room_designs.get(str(room.room_design_id), None)
                print(f"Room Design ID: {room.room_design_id}")
                if design is None:
                    print(f"Design not found for Room Design ID: {room.room_design_id}")
                else:
                    # print(f"Creating Room with ID: {room.id} and Design: {design}")
                    self.shipRooms.append(_Room.Room(_essensal_rooms=essensal_rooms, _room=room, _design=design))
                    if self.shipRooms[-1].getType() == "Wall":
                        self.shipArmor.append(self.shipRooms[-1])
            print(f"Ship Level: {_ship_design.get('ship_level', None)}")
            self.shipArmorValue = armor_value_per_lvl.get(str(_ship.ship_level), 0)
            self.ship = {
                #"""PER DATE"""#
                "ship_design_id": _ship.ship_design_id,
                "ship_id": _ship.id,
                "ship_armor_value": self.shipArmorValue,

                #"""PER LAYOUT"""#
                "ship_rooms": [room.to_dict() for room in self.shipRooms],
            }
            for armor in self.shipArmor:
                for room in self.getAjacentRooms(armor):
                    room.setArmor(armor)
            # print(f"Ship data: {self.ship}")  # Debugging output
        else:
            self.shipRooms = []
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
        self.shipRooms = [ _Room.Room().from_dict(room) for room in _ship.get("ship_rooms", []) ]

    def __repr__(self) -> str:
        return str(self.to_dict())
    
    def __str__(self) -> str:
        return self.__repr__()