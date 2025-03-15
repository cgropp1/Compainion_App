from src import apiInterface as _apiInterface
import json as _json
import re
import ast

def split_attributes(s):
    """Splits a string of key=value pairs on commas that are not inside brackets."""
    attrs = []
    current = ""
    bracket_stack = []
    for char in s:
        if char in "[{":
            bracket_stack.append(char)
            current += char
        elif char in "]}":
            if bracket_stack:
                bracket_stack.pop()
            current += char
        elif char == "," and not bracket_stack:
            attrs.append(current.strip())
            current = ""
        else:
            current += char
    if current:
        attrs.append(current.strip())
    return attrs

def convert_value(val):
    """Converts a value string to int, float, bool, None, a literal (list/dict) or leaves it as string."""
    if val == "None":
        return None
    if val == "True":
        return True
    if val == "False":
        return False
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    # If the value looks like a list or dict, try to evaluate it safely.
    if (val.startswith("[") and val.endswith("]")) or (val.startswith("{") and val.endswith("}")):
        try:
            return ast.literal_eval(val)
        except Exception:
            pass
    # Otherwise, return the value as a string.
    return val

def parse_design(text, design_type):
    """
    Given a text string like:
      <DesignType key1=value1, key2=value2, ...>
    this function returns a dictionary with the key-value pairs.
    """
    # Remove the surrounding <DesignType ...> markers.
    if text.startswith(f"<{design_type}") and text.endswith(">"):
        inner = text[len(f"<{design_type}"): -1].strip()
    else:
        inner = text.strip()
    
    data = {}
    # Split on commas that are not inside brackets
    parts = split_attributes(inner)
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            data[key] = convert_value(value)
    return data

async def get_designs(_api_interface: _apiInterface.apiInterface, service_method, design_type) -> list[dict]:
    designs = await service_method()
    designs_text = str(designs)
    design_entries = re.findall(rf"<{design_type}\s+([^>]+)>", designs_text)
    
    parsed_designs = []
    for entry in design_entries:
        design_text = f"<{design_type} " + entry + ">"
        design_data = parse_design(design_text, design_type)
        parsed_designs.append(design_data)
    
    return parsed_designs

async def get_room_designs(_api_interface: _apiInterface.apiInterface) -> list[dict]:
    return await get_designs(_api_interface, _api_interface.client.room_service.list_room_designs, "RoomDesign")

async def get_item_designs(_api_interface: _apiInterface.apiInterface) -> list[dict]:
    return await get_designs(_api_interface, _api_interface.client.item_service.list_item_designs, "ItemDesign")

async def get_ship_designs(_api_interface: _apiInterface.apiInterface) -> list[dict]: 
    return await get_designs(_api_interface, _api_interface.client.ship_service.list_all_ship_designs, "ShipDesign")

async def get_crew_designs(_api_interface: _apiInterface.apiInterface) -> list[dict]:
    return await get_designs(_api_interface, _api_interface.client.character_service.list_all_character_designs, "CharacterDesign")

async def get_all_designs(_api_interface: _apiInterface.apiInterface) -> dict:
    room_designs = await get_room_designs(_api_interface)
    item_designs = await get_item_designs(_api_interface)
    ship_designs = await get_ship_designs(_api_interface)
    crew_designs = await get_crew_designs(_api_interface)
    return {"room_designs": room_designs, "item_designs": item_designs, "ship_designs": ship_designs, "crew_designs": crew_designs}

async def get_all_designs_to_files(_api_interface: _apiInterface.apiInterface) -> None:
    room_designs = await get_room_designs(_api_interface)
    item_designs = await get_item_designs(_api_interface)
    ship_designs = await get_ship_designs(_api_interface)
    crew_designs = await get_crew_designs(_api_interface)

    with open('room_designs.json', 'w') as f:
        _json.dump(room_designs, f, indent=2)

    with open('item_designs.json', 'w') as f:
        _json.dump(item_designs, f, indent=2)

    with open('ship_designs.json', 'w') as f:
        _json.dump(ship_designs, f, indent=2)

    with open('crew_designs.json', 'w') as f:
        _json.dump(crew_designs, f, indent=2)