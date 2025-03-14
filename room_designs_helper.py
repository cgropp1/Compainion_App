import re
import json
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

def parse_room_design(text):
    """
    Given a text string like:
      <RoomDesign key1=value1, key2=value2, ...>
    this function returns a dictionary with the key-value pairs.
    """
    # Remove the surrounding <RoomDesign ...> markers.
    if text.startswith("<RoomDesign") and text.endswith(">"):
        inner = text[len("<RoomDesign"): -1].strip()
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

def main():
    input_file = "room_designs.txt"
    output_file = "room_designs.json"
    
    with open(input_file, "r") as f:
        content = f.read()
    
    # Use regex to extract all RoomDesign entries.
    # This assumes each entry is contained in a <RoomDesign ...> block.
    room_entries = re.findall(r"<RoomDesign\s+([^>]+)>", content)
    
    room_designs = {}
    for entry in room_entries:
        room_text = "<RoomDesign " + entry + ">"
        room_data = parse_room_design(room_text)
        room_id = room_data.get("RoomDesignId")
        if room_id is not None:
            room_designs[room_id] = room_data
    
    # Write the parsed room designs to a JSON file.
    with open(output_file, "w") as f:
        json.dump(room_designs, f, indent=2)
    
    print(f"Converted {len(room_designs)} room designs to {output_file}")

if __name__ == "__main__":
    main()
