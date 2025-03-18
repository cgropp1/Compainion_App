import json
import logging
from pssapi import PssApiClient
import jsonpickle

# Get logger for this module
logger = logging.getLogger('pss_companion.designs')

def serialize_obj(obj):
    """ Converts an object to a JSON-safe dictionary. """
    try:
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
    except Exception as e:
        logging.error(f'Error in serialize_obj(obj):: {e}')
        raise

async def fetch_designs(api_method, id_key) -> dict:
    """Fetches designs from the API using the provided method."""
    try:
        designs = await api_method()
        
        return {
            str(d[id_key]): serialize_obj(d)
            for d in designs if id_key in d
        }
    except Exception as e:
        logger.error(f"Error fetching designs: {e}")
        raise

async def get_all_designs(api_interface) -> dict:
    """Fetches all designs from the API."""
    try:
        return {
            "room_designs": await fetch_designs(api_interface.client.room_service.list_room_designs, "RoomDesignId"),
            "item_designs": await fetch_designs(api_interface.client.item_service.list_item_designs, "ItemDesignId"),
            "ship_designs": await fetch_designs(api_interface.client.ship_service.list_all_ship_designs, "ShipDesignId"),
            "crew_designs": await fetch_designs(api_interface.client.character_service.list_all_character_designs, "CharacterDesignId"),
        }
    except Exception as e:
        logger.error(f"Error fetching designs: {e}")
        raise

async def save_designs_to_files(api_interface):
    """Downloads and saves design data to JSON files."""
    logger.info("Starting download of design data")
    
    try:
        # Get room designs
        logger.info("Fetching room designs")
        room_designs = {}
        try:
            all_rooms = await api_interface.client.list_room_designs()
            for design in all_rooms:
                room_designs[str(design.id)] = design.__dict__
            logger.info(f"Retrieved {len(room_designs)} room designs")
            
            with open('room_designs.json', 'w') as f:
                json.dump(room_designs, f, indent=2)
            logger.info("Room designs saved to room_designs.json")
        except Exception as e:
            logger.error(f"Error fetching room designs: {e}")
            raise
        
        # Get ship designs
        logger.info("Fetching ship designs")
        ship_designs = {}
        try:
            all_ships = await api_interface.client.list_ship_designs()
            for design in all_ships:
                ship_designs[str(design.id)] = design.__dict__
            logger.info(f"Retrieved {len(ship_designs)} ship designs")
            
            with open('ship_designs.json', 'w') as f:
                json.dump(ship_designs, f, indent=2)
            logger.info("Ship designs saved to ship_designs.json")
        except Exception as e:
            logger.error(f"Error fetching ship designs: {e}")
            raise
            
        # Get crew designs
        logger.info("Fetching crew designs")
        crew_designs = {}
        try:
            all_crew = await api_interface.client.list_character_designs()
            for design in all_crew:
                crew_designs[str(design.id)] = design.__dict__
            logger.info(f"Retrieved {len(crew_designs)} crew designs")
            
            with open('crew_designs.json', 'w') as f:
                json.dump(crew_designs, f, indent=2)
            logger.info("Crew designs saved to crew_designs.json")
        except Exception as e:
            logger.error(f"Error fetching crew designs: {e}")
            raise
            
        logger.info("Design data download complete")
        return True
    except Exception as e:
        logger.error(f"Error saving designs to files: {e}")
        return False

async def write_raw_designs_to_file(api_interface, file_path: str):
    raw_data = await get_all_designs(api_interface)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(jsonpickle.encode(raw_data, indent=4))