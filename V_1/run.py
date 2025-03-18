import logging
import traceback
import os

import asyncio as _asyncio
import json
import sys as _sys

from src import apiInterface as _apiInterface
from src import user as _user
from src import ruleEngine as _ruleEngine
from src import designs as _designs
from src import log_config as _log_config
from src import fileManager as _fileManager

# Set up logging
logger, log_file = _log_config.setup_logging(log_level=logging.INFO)

#Set up file manager
file_manager = _fileManager.FileManager(base_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

#TODO: Create a UI that can can be used with the overlay and the companion app
#TODO: Go back over the matches code (ADD rating)
#TODO: Finish the rule engine rules
#TODO: Create a file manager to handle the saving and loading of files
#TODO: Finnish out the AI for the companion app and the overlay
#TODO: Finish the overlay
#TODO: Clean up dependencies and clean up the code with better def comments
#TODO: Create a online database to store the data for the companion app
#TODO: Make it an application that can be used by the public


async def async_main():
    try:
        logger.info("Starting PSS Companion App")
        apiinterface = _apiInterface.apiInterface()
        await apiinterface.init_pss_api_client()

        try:
            designs = await _designs.get_all_designs(apiinterface)
            room_designs = designs["room_designs"]
            ship_designs = designs["ship_designs"]
            if logger.getEffectiveLevel() == logging.DEBUG:
                logger.info("Saving designs to files for debugging")
                await _designs.save_designs_to_files(apiinterface, file_manager)

                logger.info("Checking internal design data with saved files")
                with open('room_designs.json', 'r') as f:
                    room_designs_file = json.load(f)
                with open('ship_designs.json', 'r') as f:
                    ship_designs_file = json.load(f)
                if room_designs != room_designs_file or ship_designs != ship_designs_file:
                    logger.error("Design data does not match saved files")
                    return 1
                logger.info("Design data matches saved files")
            logger.info("Designs fetched")
        except Exception as e:
            logger.error(f"Designs not found: {e}")
            logger.info("Attempting to load designs from files")
            try:
                with open('room_designs.json', 'r') as f:
                    room_designs = json.load(f)
                with open('ship_designs.json', 'r') as f:
                    ship_designs = json.load(f)
                logger.info("Designs fetched")
            except Exception as e:
                logger.error(f"Error loading designs from files: {e}")
                return 1
            except FileNotFoundError as e:
                logger.error(f"Design files not found: {e}")
                return 1

        try:
            rules = r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl"
            logger.info("Evaluating rules")
            if not await rule_eval_async(apiinterface, room_designs, ship_designs, rules):
                raise Exception("Error evaluating rules")  
        except Exception as e:
            logger.critical(f"Critical error in application: {e}")
            logger.debug(traceback.format_exc())
            return 1
        
        logger.info("Application completed successfully")
        print("Log file: ", log_file)
        return 0
    except Exception as e:
        logging.error(f'Error in __main__():: {e}')
        print("Log file: ", log_file)
        return 1
    
def __main__():
    """Main function for the PSS Companion App"""
    return _asyncio.run(async_main())
    
async def rule_eval_async(_api_interface: _apiInterface, _room_designs: dict, _ship_designs: dict, _rules: str) -> bool: 
    try:
        logger.info("Searching for user C3R3S1")
        tempUsr = await _api_interface.get_users_by_name(["C3R3S1"])
        # Filter to find the exact match
        exact_user = next((user for user in tempUsr if user["Name"] == "C3R3S1"), None)
        if not exact_user:
            logger.error("No users found with the exact name 'C3R3S1'")
            return False
        
        logger.info(f"Found user: {exact_user['Name']} (ID: {exact_user['Id']})")
        tempShip = await _api_interface.get_ship_by_user(exact_user)
        logger.info(f"Retrieved ship for user")
        logger.info("Creating User object")
        User = await _user.User.create(_api_interface=_api_interface, _user=exact_user, room_designs=_room_designs, ship_designs=_ship_designs)
        User.to_file(_fileManager = file_manager)
        logger.info("User data saved to file")

        logger.info("Initializing Rule Engine")
        ruleEnginge = await _ruleEngine.RuleEngine().create(api_interface=_api_interface, rules_file=_rules, user=User)
        logger.info("Evaluating rooms")
        score, evaluations, issues = ruleEnginge.evaluate_all_rooms()
        logger.info(f"Evaluation complete. Score: {score}")
        logger.debug(f"Evaluations: {evaluations}")
        logger.info(f"Issues: {issues}")
    except Exception as e:         
        logger.error(f"Error processing user data: {e}")
        logger.debug(traceback.format_exc())
        return False
    return True
    
if __name__ == "__main__":
    _sys.exit(__main__())