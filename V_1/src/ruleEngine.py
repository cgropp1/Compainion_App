import logging
import traceback
import asyncio
import json as _json

from src import dslParser as _dslParser
from src import room as _room
from src import ship as _ship
from src import user as _user
from src import config as _config

# Get logger for this module
logger = logging.getLogger('pss_companion.ruleEngine')

class apiInterface:
    pass
    
class RuleEngine:

    def __init__(self) -> None:
        self.rules = None
        self.user = None
        self.rooms = None
        self.lifts = None
        self.ship_armor_value = None
        self.np_multiplier = 1.0


    @classmethod
    async def create(cls, api_interface: apiInterface, rules_file: str, user_file: str = None, user: _user.User = None):
        """Factory method to create and initialize a RuleEngine object asynchronously"""
        # Create instance with minimal init
        instance = cls()
        await instance.init_ruleEngine(api_interface, rules_file, user_file, user)
        return instance

    async def init_ruleEngine(self, api_interface: apiInterface, rules_file: str, user_file: str = None, user: _user.User = None) -> None:
        try:
            logger.info(f"Initializing Rule Engine with rules file: {rules_file}")
            self.rules = _dslParser.parse_dsl_file(rules_file)
            logger.debug(f"Loaded {len(self.rules)} rules from DSL file")

            
            if user_file:
                logger.info(f"Loading user data from file: {user_file}")
                self.user = await _user.User.create(api_interface)
                self.user.from_file(user_file)
            else:
                logger.info(f"Using provided user object")
                self.user = user
                
            self.lifts = self.user.ship.Lifts
            logger.debug(f"Retrieved {len(self.lifts)} lifts from user data")
            
            self.rooms = self.user.rooms
            logger.debug(f"Retrieved {len(self.rooms)} rooms from user data")
            
            self.ship_armor_value = self.user.to_dict_dated_data()["user_ship"]["ship_armor_value"]
            logger.info(f"Ship armor value: {self.ship_armor_value}")
        except Exception as e:
            logger.error(f"Error initializing Rule Engine: {e}")
            raise

    def evaluate_room(self, room: _room.Room) -> tuple[str, str, int]:
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

                        # Run acttions basses on essensal rooms
                        if room.type in _config.get_essential_rooms():
                            logger.info(f"Room {room_name} is essential")
                            self.np_multiplier += .01
                        
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
            if room.type in _config.get_essential_rooms():
                logger.info(f"Room {room_name} is essential, reducing NP multiplier")
                self.np_multiplier -= .01
            return [room_name, 0, "No Rule Triggered"]
                    
            
        except Exception as e:
            logger.error(f"Error in evaluate_room: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return ["Error", 0, str(e)]
        
    def evaluate_lift(self, lift: _ship.lift) -> tuple[str, int, str]:
        """Evaluate a lift object against lift-specific rules"""
        try:
            if not lift or not hasattr(lift, 'rooms'):
                logger.warning("Skipping invalid lift in evaluation")
                return ["Unknown", 0, "Invalid Lift"]
                
            lift_id = f"Lift-{id(lift)}"  # Create a unique identifier for this lift
            logger.debug(f"Evaluating rules for lift with {lift.langth} rooms")
            
            # For the LFT_LENGTH rule
            if lift.type == "LiftOBJ" and lift.langth > 5:
                penalty_value = -0.25 * lift.langth
                message = "Lifts should be short"
                logger.info(f"Rule 'LFT_LENGTH' triggered for lift with {lift.langth} rooms")
                return [lift_id, penalty_value, message]
                
            return [lift_id, 0, "No Rule Triggered"]
        except Exception as e:
            logger.error(f"Error in evaluate_lift: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return ["Error", 0, str(e)]

    def evaluate_lifts(self) -> tuple[float, list[tuple[str, int, str]]]:
        """Evaluate all lifts and return results"""
        logger.info("Starting evaluation of all lifts")
        evaluations = []
        issues = []

        try:
            for lift in self.lifts:
                result = self.evaluate_lift(lift)
                evaluations.append(result)
                if result[1] != 0:
                    issues.append(result)
                    
            # Calculate score based on penalties
            score = sum(eval_item[1] for eval_item in evaluations)
            
            logger.info(f"Lift evaluation complete. Score contribution: {score}")
            return score, evaluations, issues
        except Exception as e:
            logger.error(f"Error in evaluate_lifts: {e}")
            return 0.0, [], []

    def evaluate_all_rooms(self) -> tuple[float, list[tuple[str, int, str]]]:
        logger.info("Starting evaluation of all rooms and lifts")
        score = 100.0
        room_evaluations = []
        lift_evaluations = []
        issues = []
        
        try:
            # Evaluate regular rooms
            for room in self.rooms:
                if room.type in ["Wall", "Corridor", "Lift"]:
                    logger.debug(f"Skipping room {room.id} of type {room.type}")
                    continue
                    
                result = self.evaluate_room(room)
                room_evaluations.append(result)
                if result[1] != 0:
                    issues.append(result)
            
            # Evaluate lifts
            lift_score, lift_evals, lift_issues = self.evaluate_lifts()
            lift_evaluations.extend(lift_evals)
            issues.extend(lift_issues)
            
            # Combine all evaluations
            all_evaluations = room_evaluations + lift_evaluations

            # Apply NP multiplier to appropriate room evaluations
            logger.info(f"Applying NP multiplier: {self.np_multiplier}")
            for evaluation in room_evaluations:
                if evaluation[2] == 'Non-powered rooms should not have armor':
                    logger.debug(f"Applying NP multiplier to room {evaluation[0]}")
                    evaluation[1] *= self.np_multiplier
            
            # Calculate final score
            total_penalty = sum(eval_item[1] for eval_item in all_evaluations)
            score += total_penalty
            
            logger.debug(f"Detailed evaluations: {all_evaluations}")
            logger.info(f"Evaluation complete. Final score: {score} / 100")
            return score, all_evaluations, issues
            
        except Exception as e:
            logger.error(f"Error in evaluate_all_rooms: {e}")
            return 0.0, [], []
