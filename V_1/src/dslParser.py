#!/usr/bin/env python3
import re

class DSLRule:
    def __init__(self, name, condition, actions):
        self.name = name              # e.g. "Unpowered Room Armor Check"
        self.condition = condition    # e.g. "not room.powered and room.armor > 0"
        self.actions = actions        # e.g. [("penalty", -5), ("message", "Unpowered room {name} should not have armor.")]

def parse_dsl_file(file_path):
    with open(file_path, "r") as f:
        dsl_text = f.read()
    return parse_dsl_text(dsl_text)

def parse_dsl_text(dsl_text):
    # This regex captures the rule name, condition, and actions.
    rule_pattern = re.compile(
        r'RULE\s+"(.*?)"\s*[\r\n]+\s*WHEN\s+(.*?)\s*[\r\n]+\s*THEN\s+(.*?)(?=(\nRULE\s+"|$))',
        re.DOTALL
    )
    rules = []
    for match in rule_pattern.finditer(dsl_text):
        name = match.group(1).strip()
        condition = match.group(2).strip()
        actions_str = match.group(3).strip()
        actions = parse_actions(actions_str)
        rules.append(DSLRule(name, condition, actions))
    return rules

def parse_actions(actions_str):
    """
    Parse actions separated by commas.
    Each action is expected to be in the form: actionName(parameter)
    """
    actions = []
    parts = re.split(r',\s*(?![^()]*\))', actions_str)
    for part in parts:
        part = part.strip()
        m = re.match(r'(\w+)\((.*)\)', part)
        if m:
            action_name = m.group(1)
            param = m.group(2).strip()
            # Remove quotes if parameter is a string.
            if (param.startswith('"') and param.endswith('"')) or (param.startswith("'") and param.endswith("'")):
                param = param[1:-1]
            else:
                try:
                    param = int(param)
                except ValueError:
                    try:
                        param = float(param)
                    except ValueError:
                        pass
            actions.append((action_name, param))
    return actions

if __name__== "__main__":
    rules = parse_dsl_file(r"C:\Users\coleg\Documents\GitHub\PSS\Compainion_App\ROOM_RULES.dsl")
    for rule in rules:
        print("Rule:", rule.name)
        print(" Condition:", rule.condition)
        print(" Actions:", rule.actions)
