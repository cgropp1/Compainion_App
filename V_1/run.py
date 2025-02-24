from src import apiInterface as _apiInterface, user as _user, agent as _agent, screenReader as _screenReader
import matches as _matches
from typing import List, Tuple
import os as _os

def get_matches_input(_apiInterface: _apiInterface) -> List[Tuple[_user.User, _user.User, int]]:
    print("Input player one name: ")
    player1 = input()
    print("Input player two name: ")
    player2 = input()
    print("Input match outcome: (0 = player1 wins, 1 = player2 wins, 2 = draw)")
    outcome = int(input())
    users = _apiInterface.get_users_by_name([player1, player2])
    return [(_user.User(_apiInterface, users[0]), _user.User(_apiInterface, users[1]), outcome)]

def create_matches_from_user(_apiInterface: _apiInterface) -> List[Tuple[_user.User, _user.User, int]]:
    print("Enter the names of the players and the outcome of the match")
    matches: List[Tuple[_user.User, _user.User, int]] = []
    add_another = "y"
    while add_another == "y":
        matches.extend(get_matches_input(_apiInterface))
        print("Do you want to add another match? (y/n)")
        add_another = input().lower()
        if add_another != "y" and add_another != "n":
            while add_another != "y" and add_another != "n":
                print("Invalid input, please enter 'y' or 'n'")
                add_another = input().lower()
        _os.system('cls' if _os.name == 'nt' else 'clear')

    return matches

def match_callback(results, match_manager, api_interface):
    user1_name, user2_name, outcome = results
    users = api_interface.get_users_by_name([user1_name, user2_name])
    match = (_user.User(api_interface, users[0]), _user.User(api_interface, users[1]), outcome)
    match_manager.include_matches([match])
    print(f"Match Captured: {match}")

def __main__():
    apiInterface = _apiInterface.apiInterface()
    agent = _agent.Agent(apiInterface)
    match_manager = _matches.Match_Manager(_apiInterface = apiInterface)
    screenReader = _screenReader.ScreenReader(match_callback=lambda results: match_callback(results, match_manager, apiInterface), num_regions=2)
    screenReader.run()

    print(match_manager)
    

if __name__ == "__main__":
    __main__()