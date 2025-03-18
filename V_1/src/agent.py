import pandas as _pandas
import logging
from sklearn.model_selection import train_test_split as _train_test_split
from sklearn.ensemble import RandomForestClassifier as _RandomForestClassifier
from sklearn.metrics import accuracy_score as _accuracy_score
from typing import List, Tuple

# Get logger for this module
logger = logging.getLogger('pss_companion.agent')

class User:
    pass

class apiInterface:
    pass

class Agent:
    def __init__(self, data: List[dict] = None, model = None) -> None:
        """Initialize the Agent."""
        try:
            self.data = data
            self.model = model
            if data:
                logger.info(f"Agent initialized with {len(data)} data points")
            else:
                logger.info("Agent initialized without data")
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def train(self, data: List[dict] = None) -> None:
        """Train the agent model."""
        try:
            if data:
                self.data = data
                
            if not self.data:
                logger.warning("No data available for training")
                return
                
            logger.info("Starting model training")
            
            # Transform the data
            df = _pandas.DataFrame(self.data)
            
            # Define features and target
            X = df.drop('target', axis=1)
            y = df['target']
            
            # Split the data
            X_train, X_test, y_train, y_test = _train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train the model
            self.model = _RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate the model
            y_pred = self.model.predict(X_test)
            accuracy = _accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained with accuracy: {accuracy:.4f}")
        except Exception as e:
            logging.error(f'Error in train(self,: {e}')
            raise

    def predict(self, data: dict) -> Tuple[str, float]:
        """Make a prediction based on the input data."""
        try:
            if not self.model:
                logger.warning("No model available for prediction")
                return None, 0.0
                
            # Transform the input data
            input_df = _pandas.DataFrame([data])
            
            # Make the prediction
            prediction = self.model.predict(input_df)[0]
            # Get the probability of the prediction
            probability = max(self.model.predict_proba(input_df)[0])
            
            logger.info(f"Prediction: {prediction} with probability {probability:.4f}")
            return prediction, probability
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None, 0.0

    def save_model(self, path: str) -> bool:
        """Save the trained model to the given path."""
        try:
            import pickle
            
            if not self.model:
                logger.warning("No model available to save")
                return False
                
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
                
            logger.info(f"Model successfully saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self, path: str) -> bool:
        """Load a trained model from the given path."""
        try:
            import pickle
            
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
                
            logger.info(f"Model successfully loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False