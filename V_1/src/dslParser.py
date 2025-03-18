import logging
import re

# Get logger for this module
logger = logging.getLogger('pss_companion.dslParser')

class Rule:
    def __init__(self, name, condition, actions):
        self.name = name
        self.condition = condition
        self.actions = actions
        logger.debug(f"Rule created: {name} with {len(actions)} actions")

def parse_dsl_file(file_path):
    """Parse a DSL file containing rules"""
    logger.info(f"Parsing DSL file: {file_path}")
    rules = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.debug(f"DSL file read successfully, content length: {len(content)}")
        
        # Extract rule blocks
        rule_pattern = r'RULE\s+"([^"]+)"\s+WHEN\s+(.*?)\s+THEN\s+(.*?)(?=RULE|$)'
        rule_blocks = re.findall(rule_pattern, content, re.DOTALL)
        
        for name, condition, actions_block in rule_blocks:
            # Clean up condition - REMOVE COMMENTS HERE TOO
            condition = re.sub(r'//.*$', '', condition, flags=re.MULTILINE)
            condition = condition.strip()
            logger.debug(f"Parsed condition for rule '{name}': {condition}")
            
            # Parse actions properly
            actions = []
            
            # Strip comments
            actions_block = re.sub(r'//.*$', '', actions_block, flags=re.MULTILINE)
            
            # Find penalty actions
            penalty_match = re.search(r'penalty\(([-+]?\d*\.?\d+)\)', actions_block)
            if penalty_match:
                penalty_value = float(penalty_match.group(1))
                actions.append(('penalty', penalty_value))
                logger.debug(f"Added penalty action: {penalty_value}")
            
            # Find message actions
            message_match = re.search(r'message\("([^"]*)"\)', actions_block)
            if message_match:
                message_text = message_match.group(1)
                actions.append(('message', message_text))
                logger.debug(f"Added message action: {message_text}")
            
            # If no actions found, add default
            if not actions:
                logger.warning(f"No actions found for rule '{name}'")
                actions = [('penalty', 0), ('message', 'No actions defined')]
            
            rule = Rule(name, condition, actions)
            rules.append(rule)
            logger.info(f"Added rule: {name} with {len(actions)} actions")
        
        logger.info(f"Parsed {len(rules)} rules from DSL file")
        return rules
    
    except Exception as e:
        logger.error(f"Error parsing DSL file: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return []