from src import apiInterface as _apiInterface, user as _user, agent as _agent, screenReader as _screenReader
from src import ruleEngine as _ruleEngine
import matches as _matches
from typing import List, Tuple
import os as _os
import sys as _sys
import asyncio as _asyncio
import json

# Add the directory containing room_designs_helper.py to the Python path
#_sys.path.append(_os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..')))
#import room_designs_helper as _room_designs_helper 

def room_design_to_dict(room_design) -> dict:
    """Convert a RoomDesign object to a dictionary."""
    return {key: value for key, value in vars(room_design).items() if not callable(value) and not key.startswith('_')}

#TODO: Create a class to get all designs (Ship and Item, CREW?) and save them to json files
async def async_API_calls(_apiInterface) -> List[dict]:
    room_designs = await _apiInterface.client.item_service.list_item_designs()
    with open('room_designs.txt', 'w') as f:
        f.write(str(room_designs))
    return room_designs

def __main__():
    apiinterface = _apiInterface.apiInterface()


    with open('room_designs.json', 'r') as f:
        room_designs = json.load(f)

    user = _user.User(apiinterface)
    user.from_file(_file_path = r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\V_1\user_data\C3R3S1_6366452.gz")
    


    ruleEnginge = _ruleEngine.RuleEngine(api_interface=apiinterface, rules_file=r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl", user_file=r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\V_1\user_data\C3R3S1_6366452.gz")
    print(ruleEnginge.rules[0].name)
    
    
if __name__ == "__main__":
   __main__()