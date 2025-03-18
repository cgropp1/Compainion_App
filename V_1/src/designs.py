import json
import logging
from pssapi import PssApiClient

from src import fileManager as _fileManager

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
        return {str(d[id_key]): serialize_obj(d) for d in designs if id_key in d}
    except Exception as e:
        logger.error(f"Error fetching designs: {e}")
        raise

async def get_all_designs(api_interface) -> dict:
    """Fetches all designs from the API in a format matching room_designs.json."""
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

async def save_designs_to_files(api_interface, file_manager: _fileManager.FileManager = None) -> bool:
    """Downloads and saves design data to JSON files."""
    logger.info("Starting download of design data")
    
    try:
        # Get room designs from API
        logger.info("Fetching room designs")
        room_designs = await get_all_designs(api_interface)

        if file_manager:
            if file_manager.create_dir('designs'):
                logger.info("Saving designs to files")
                logger.info(f"Created room designs files at: {file_manager.save_json(filepath='designs/room_designs.json', data=room_designs['room_designs'])}")
                logger.info(f"Created item designs files at: {file_manager.save_json(filepath='designs/item_designs.json', data=room_designs['item_designs'])}")
                logger.info(f"Created ship designs files at: {file_manager.save_json(filepath='designs/ship_designs.json', data=room_designs['ship_designs'])}")
                logger.info(f"Created crew designs files at: {file_manager.save_json(filepath='designs/crew_designs.json', data=room_designs['crew_designs'])}")
            else:
                logger.error("Failed to create designs directory")
                return
        else:
            logger.info("Using legacy file manager")
            basepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/designs')
            with open(f'{basepath}room_designs.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(room_designs["room_designs"], indent=4))
            logger.info("Room designs download complete")

            with open(f'{basepath}item_designs.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(room_designs["item_designs"], indent=4))
            logger.info("Item designs download complete")

            with open(f'{basepath}ship_designs.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(room_designs["ship_designs"], indent=4))
            logger.info("Ship designs download complete")

            with open(f'{basepath}crew_designs.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(room_designs["crew_designs"], indent=4))
            logger.info("Crew designs download complete")

        logger.info("Design data download complete")
        return True
    except Exception as e:
        logger.error(f"Error saving designs to files: {e}")
        return False

# async def write_raw_designs_to_file(api_interface, file_path: str):
#     raw_data = await get_all_designs(api_interface)
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(jsonpickle.encode(raw_data, indent=4))