import logging
import os

import asyncio as _asyncio
import json
import sys as _sys
import traceback

from src import apiInterface as _apiInterface
from src import user as _user
from src import ruleEngine as _ruleEngine
from src import designs as _designs
from src import log_config

# Set up logging
logger, log_file = log_config.setup_logging()

def __main__():
    try:
        try:
            logger.info("Starting PSS Companion App")
            apiinterface = _apiInterface.apiInterface()
            logger.info("API Interface initialized")

            try:
                with open('room_designs.json', 'r') as f:
                    room_designs = json.load(f)
                logger.info("Room designs loaded")
                
                with open('ship_designs.json', 'r') as f:
                    ship_designs = json.load(f)
                logger.info("Ship designs loaded")
            except FileNotFoundError as e:
                logger.error(f"Design files not found: {e}")
                logger.info("Downloading design files")
                _asyncio.run(_designs.save_designs_to_files(apiinterface))
                with open('room_designs.json', 'r') as f:
                    room_designs = json.load(f)
                with open('ship_designs.json', 'r') as f:
                    ship_designs = json.load(f)
                logger.info("Design files downloaded and loaded")

            try:
                logger.info("Searching for user C3R3S1")
                tempUsr = apiinterface.get_users_by_name(["C3R3S1"])

                # Filter to find the exact match
                exact_user = next((user for user in tempUsr if user["Name"] == "C3R3S1"), None)
                if not exact_user:
                    logger.error("No users found with the exact name 'C3R3S1'")
                    return

                logger.info(f"Found user: {exact_user['Name']} (ID: {exact_user['Id']})")
                tempShip = apiinterface.get_ship_by_user(exact_user)
                logger.info(f"Retrieved ship for user")

                logger.info("Creating User object")
                User = _user.User(_api_interface=apiinterface, _user=exact_user, room_designs=room_designs, ship_designs=ship_designs)
                User.to_file()
                logger.info("User data saved to file")
                
                rulesDSL = r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl"

                logger.info("Initializing Rule Engine")
                ruleEnginge = _ruleEngine.RuleEngine(api_interface=apiinterface, rules_file=rulesDSL, user=User)
                logger.info("Evaluating rooms")
                score, evaluations, issues = ruleEnginge.evaluate_all_rooms()
                logger.info(f"Evaluation complete. Score: {score}")
                logger.debug(f"Evaluations: {evaluations}")
                logger.info(f"Issues: {issues}")
            except Exception as e:
                logger.error(f"Error processing user data: {e}")
                logger.debug(traceback.format_exc())
                
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
    
if __name__ == "__main__":
    _sys.exit(__main__())