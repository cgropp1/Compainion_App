from src import apiInterface as _apiInterface, user as _user, agent as _agent, screenReader as _screenReader
from src import ruleEngine as _ruleEngine
#from src import designs as _designs
import matches as _matches
from typing import List, Tuple
import os as _os
import sys as _sys
import asyncio as _asyncio
import json

def __main__():
    apiinterface = _apiInterface.apiInterface()

    #_asyncio.run(_designs.save_designs_to_files(apiinterface))

    with open('room_designs.json', 'r') as f:
        room_designs = json.load(f)
    with open('ship_designs.json', 'r') as f:
        ship_designs = json.load(f)

    tempUsr = apiinterface.get_users_by_name(["C3R3S1"])

    # Filter to find the exact match
    exact_user = next((user for user in tempUsr if user["Name"] == "C3R3S1"), None)
    if not exact_user:
        print("No users found with the exact name 'C3R3S1'")
        return

    tempShip = apiinterface.get_ship_by_user(exact_user)

    User = _user.User(_api_interface=apiinterface, _user=exact_user, room_designs=room_designs, ship_designs=ship_designs)
    User.to_file()
    rulesDSL = r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl"
    userFile = r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\V_1\user_data\C3R3S1_6366452.gz"

    #ruleEnginge = _ruleEngine.RuleEngine(api_interface=apiinterface, rules_file=rulesDSL, user_file=userFile)
    ruleEnginge = _ruleEngine.RuleEngine(api_interface=apiinterface, rules_file=rulesDSL, user=User)
    print(ruleEnginge.evaluate_all_rooms())
    
if __name__ == "__main__":
   __main__()