from dataclasses import dataclass
import json
import jsonpickle

#TODO: This still does not seem to work...

def serialize_obj(obj):
    """ Converts an object to a JSON-safe dictionary. """
    if isinstance(obj, dict):
        return {k: serialize_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_obj(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):  # Primitive types
        return obj
    elif hasattr(obj, "__dict__"):  # Handles objects
        return {
            k: serialize_obj(getattr(obj, k))
            for k in dir(obj) if not k.startswith("_") and not callable(getattr(obj, k, None))
        }
    return str(obj)  # Fallback for unsupported types

@dataclass
class Design:
    attributes: dict

async def fetch_designs(api_method, id_key) -> dict:
    designs = await api_method()
    
    return {
        str(d[id_key]): serialize_obj(d)
        for d in designs if id_key in d
    }

async def get_all_designs(api_interface) -> dict:
    return {
        "room_designs": await fetch_designs(api_interface.client.room_service.list_room_designs, "RoomDesignId"),
        "item_designs": await fetch_designs(api_interface.client.item_service.list_item_designs, "ItemDesignId"),
        "ship_designs": await fetch_designs(api_interface.client.ship_service.list_all_ship_designs, "ShipDesignId"),
        "crew_designs": await fetch_designs(api_interface.client.character_service.list_all_character_designs, "CharacterDesignId"),
    }

async def save_designs_to_files(api_interface):
    designs = await get_all_designs(api_interface)
    for category, data in designs.items():
        with open(f"{category}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    print("Designs saved to JSON files.")

async def write_raw_designs_to_file(api_interface, file_path: str):
    raw_data = await get_all_designs(api_interface)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(jsonpickle.encode(raw_data, indent=4))