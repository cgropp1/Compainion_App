import logging
from src import dslParser as _dslParser
from src import room as _Room
from src import user as _User

# Get logger for this module
logger = logging.getLogger('pss_companion.ruleEngine')

class apiInterface:
    pass
    
class RuleEngine:

    def __init__(self, api_interface: apiInterface, rules_file: str, user_file: str = None, user: _User.User = None) -> None:
        try:
            logger.info(f"Initializing Rule Engine with rules file: {rules_file}")
            self.rules = _dslParser.parse_dsl_file(rules_file)
            logger.debug(f"Loaded {len(self.rules)} rules from DSL file")
            
            if user_file:
                logger.info(f"Loading user data from file: {user_file}")
                self.user = _User.User(api_interface)
                self.user.from_file(user_file)
            else:
                logger.info(f"Using provided user object")
                self.user = user
                
            self.rooms = self.user.rooms
            logger.debug(f"Retrieved {len(self.rooms)} rooms from user data")
            
            self.ship_armor_value = self.user.to_dict_dated_data()["user_ship"]["ship_armor_value"]
            logger.info(f"Ship armor value: {self.ship_armor_value}")
        except Exception as e:
            logger.error(f"Error initializing Rule Engine: {e}")
            raise

    def evaluate_room(self, room: _Room.Room) -> tuple[str, str, int]:
        """Evaluate room against rules and return results"""
        try:
            if not room or not hasattr(room, 'room') or not room.room:
                logger.warning(f"Skipping invalid room in evaluation")
                return ["Unknown", 0, "Invalid Room"]
                
            room_name = room.short_name if hasattr(room, 'short_name') else "Unknown"
            logger.debug(f"Evaluating rules for room: {room_name}")
            
            for rule in self.rules:
                try:
                    # Convert condition to valid Python syntax
                    condition = rule.condition
                    # Replace JavaScript operators with Python operators
                    condition = condition.replace('&&', ' and ')
                    condition = condition.replace('||', ' or ')
                    
                    # Handle self.ship_armor_value references
                    if 'self.ship_armor_value' in condition:
                        condition = condition.replace('self.ship_armor_value', str(self.ship_armor_value))
                    
                    # Create a safe locals dictionary for evaluation
                    eval_locals = {"room": room}
                    
                    # Safely evaluate the condition
                    logger.debug(f"Evaluating condition for {room_name}: {condition}")
                    result = eval(condition, {"__builtins__": {}}, eval_locals)
                    
                    if result:
                        logger.info(f"Rule '{rule.name}' triggered for room {room_name}")
                        
                        # Extract rule actions safely
                        try:
                            # Make sure we have enough actions
                            if not hasattr(rule, 'actions') or not rule.actions:
                                logger.warning(f"Rule {rule.name} has no actions defined")
                                continue
                                
                            if len(rule.actions) < 2:
                                logger.warning(f"Rule {rule.name} has insufficient actions: {rule.actions}")
                                # Return what we can
                                action_value = 0
                                action_message = "Incomplete rule"
                                
                                if len(rule.actions) == 1:
                                    if len(rule.actions[0]) >= 2:
                                        if rule.actions[0][0] == "penalty":
                                            action_value = rule.actions[0][1]
                                            action_message = "Penalty"
                                        else:
                                            action_value = rule.actions[0][1]
                                            action_message = "Reward"
                                
                                return [room_name, action_value, action_message]
                            
                            # We have at least 2 actions, check their format
                            action1 = rule.actions[0]
                            action2 = rule.actions[1]
                            
                            if not isinstance(action1, (list, tuple)) or len(action1) < 2:
                                logger.warning(f"Invalid action1 format: {action1}")
                                action1 = ("unknown", 0)
                                
                            if not isinstance(action2, (list, tuple)) or len(action2) < 2:
                                logger.warning(f"Invalid action2 format: {action2}")
                                action2 = ("unknown", "No message")
                            
                            # Now safely extract the values
                            if action1[0] == "penalty":
                                return [room_name, action1[1], action2[1]]
                            else:
                                return [room_name, action2[1], action1[1]]
                                
                        except Exception as e:
                            logger.error(f"Error extracting rule results: {e}")
                            import traceback
                            logger.debug(traceback.format_exc())
                            return [room_name, 0, f"Error: {str(e)}"]
                except Exception as e:
                    logger.error(f"Error evaluating rule condition '{condition}': {str(e)}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
                    
            return [room_name, 0, "No Rule Triggered"]
        except Exception as e:
            logger.error(f"Error in evaluate_room: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return ["Error", 0, str(e)]

    def evaluate_all_rooms(self) -> tuple[float, list[tuple[str, int, str]]]:
        logger.info("Starting evaluation of all rooms")
        score = 0.0
        evaluations = []
        issues = []
        
        try:
            for room in self.rooms:
                if room.type in ["Wall", "Lift", "Corridor"]:
                    logger.debug(f"Skipping room {room.id} of type {room.type}")
                    continue
                    
                result = self.evaluate_room(room)
                evaluations.append(result)
                if evaluations[-1][1] != 0:
                    issues.append(evaluations[-1])
                score += result[1]
                
            logger.info(f"Evaluation complete. Final score: {score}")
            logger.debug(f"Detailed evaluations: {evaluations}")
            return score, evaluations, issues
            
        except Exception as e:
            logger.error(f"Error in evaluate_all_rooms: {e}")
            return 0.0, []