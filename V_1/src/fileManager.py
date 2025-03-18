import logging
import json
import gzip
import os
import shutil
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import atexit

# Get logger for this module
logger = logging.getLogger('pss_companion.fileManager')

class FileManager:
    """
    A class to manage file operations.
    - Saves and loads JSON files
    - Saves and loads GZIP compressed JSON files
    - Tracks files and can mark them as temporary
    - Cleans up temporary files on application exit
    - Provides foundation for future database integration
    """

    def __init__(self, base_dir: str = None, auto_cleanup: bool = True):
        """
        Initialize the FileManager.
        
        Args:
            base_dir: Base directory for all file operations. If None, uses current directory.
            auto_cleanup: Whether to automatically clean up temporary files on exit.
        """
        self.base_dir = base_dir or os.getcwd()
        self.auto_cleanup = auto_cleanup
        
        # Track all files managed by this class
        self.tracked_files = {}  # {filepath: {is_temp: bool, type: str, created: datetime, last_accessed: datetime}}
        
        # Create necessary directories
        os.makedirs(self.base_dir, exist_ok=True)
        
        logger.info(f"FileManager initialized with base directory: {self.base_dir}")
        
        # Register cleanup on program exit if auto_cleanup is enabled
        if auto_cleanup:
            atexit.register(self.cleanup_temp_files)
    
    def save_json(self, data: Any, filepath: str, is_temp: bool = False, pretty: bool = True) -> str:
        """
        Save data as JSON to the specified file.
        
        Args:
            data: The data to save
            filepath: Path to save the file (relative to base_dir unless absolute)
            is_temp: Whether this is a temporary file to be cleaned up later
            pretty: Whether to format the JSON with indentation
            
        Returns:
            The absolute path to the saved file
        """
        try:
            # Handle relative paths
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.base_dir, filepath)
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the data
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2)
                else:
                    json.dump(data, f)
            
            # Track the file
            self._track_file(filepath, is_temp, 'json')
            
            logger.debug(f"JSON data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving JSON data to {filepath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise
    
    def load_json(self, filepath: str, default: Any = None) -> Any:
        """
        Load JSON data from the specified file.
        
        Args:
            filepath: Path to load the file from (relative to base_dir unless absolute)
            default: Value to return if file doesn't exist or can't be loaded
            
        Returns:
            The loaded data or default value
        """
        try:
            # Handle relative paths
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.base_dir, filepath)
                
            # Check if file exists
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return default
                
            # Load the data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update access time for this file if tracked
            if filepath in self.tracked_files:
                self.tracked_files[filepath]['last_accessed'] = datetime.now()
            
            logger.debug(f"JSON data loaded from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading JSON data from {filepath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return default
    
    def save_gzip_json(self, data: Any, filepath: str, is_temp: bool = False) -> str:
        """
        Save data as compressed JSON to the specified file.
        
        Args:
            data: The data to save
            filepath: Path to save the file (relative to base_dir unless absolute)
            is_temp: Whether this is a temporary file to be cleaned up later
            
        Returns:
            The absolute path to the saved file
        """
        try:
            # Handle relative paths
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.base_dir, filepath)
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert data to JSON and compress
            json_data = json.dumps(data).encode('utf-8')
            with gzip.open(filepath, 'wb') as f:
                f.write(json_data)
            
            # Track the file
            self._track_file(filepath, is_temp, 'gzip_json')
            
            logger.debug(f"Compressed JSON data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving compressed JSON data to {filepath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise
    
    def load_gzip_json(self, filepath: str, default: Any = None) -> Any:
        """
        Load compressed JSON data from the specified file.
        
        Args:
            filepath: Path to load the file from (relative to base_dir unless absolute)
            default: Value to return if file doesn't exist or can't be loaded
            
        Returns:
            The loaded data or default value
        """
        try:
            # Handle relative paths
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.base_dir, filepath)
                
            # Check if file exists
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return default
                
            # Load and decompress the data
            with gzip.open(filepath, 'rb') as f:
                json_data = f.read().decode('utf-8')
                data = json.loads(json_data)
            
            # Update access time for this file if tracked
            if filepath in self.tracked_files:
                self.tracked_files[filepath]['last_accessed'] = datetime.now()
            
            logger.debug(f"Compressed JSON data loaded from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading compressed JSON data from {filepath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return default
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file.
        
        Args:
            filepath: Path to the file to delete (relative to base_dir unless absolute)
            
        Returns:
            True if file was deleted, False otherwise
        """
        try:
            # Handle relative paths
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.base_dir, filepath)
                
            # Check if file exists
            if not os.path.exists(filepath):
                logger.warning(f"File not found for deletion: {filepath}")
                return False
                
            # Delete the file
            os.remove(filepath)
            
            # Remove from tracking
            if filepath in self.tracked_files:
                del self.tracked_files[filepath]
            
            logger.debug(f"File deleted: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def cleanup_temp_files(self) -> int:
        """
        Delete all temporary files that have been tracked.
        
        Returns:
            Number of files deleted
        """
        try:
            count = 0
            temp_files = [filepath for filepath, info in self.tracked_files.items() if info['is_temp']]
            
            for filepath in temp_files:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    count += 1
                    logger.debug(f"Temporary file deleted: {filepath}")
                
                # Remove from tracking regardless
                del self.tracked_files[filepath]
            
            logger.info(f"Cleaned up {count} temporary files")
            return count
            
        except Exception as e:
            logger.error(f"Error during temporary file cleanup: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return 0
    
    def get_tracked_files(self, temp_only: bool = False) -> List[str]:
        """
        Get a list of all tracked files.
        
        Args:
            temp_only: If True, only return temporary files
            
        Returns:
            List of file paths
        """
        if temp_only:
            return [filepath for filepath, info in self.tracked_files.items() if info['is_temp']]
        else:
            return list(self.tracked_files.keys())
    
    def mark_as_temp(self, filepath: str) -> bool:
        """
        Mark an existing file as temporary.
        
        Args:
            filepath: Path to the file (relative to base_dir unless absolute)
            
        Returns:
            True if file was marked, False otherwise
        """
        # Handle relative paths
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.base_dir, filepath)
            
        if filepath in self.tracked_files:
            self.tracked_files[filepath]['is_temp'] = True
            logger.debug(f"File marked as temporary: {filepath}")
            return True
        elif os.path.exists(filepath):
            # File exists but isn't tracked, so track it now
            self._track_file(filepath, True, 'unknown')
            logger.debug(f"Existing file now tracked and marked as temporary: {filepath}")
            return True
        else:
            logger.warning(f"Cannot mark non-existent file as temporary: {filepath}")
            return False
    
    def _track_file(self, filepath: str, is_temp: bool, file_type: str) -> None:
        """Internal method to track a file with metadata"""
        now = datetime.now()
        self.tracked_files[filepath] = {
            'is_temp': is_temp,
            'type': file_type,
            'created': now,
            'last_accessed': now
        }
    
    def create_dir(self, dirpath: str) -> str:
        """
        Create a directory.
        
        Args:
            dirpath: Path to the directory to create (relative to base_dir unless absolute)
            
        Returns:
            True if directory was created, False otherwise
        """
        try:
            # Handle relative paths
            if not os.path.isabs(dirpath):
                dirpath = os.path.join(self.base_dir, dirpath)
                
            # Create the directory
            os.makedirs(dirpath, exist_ok=True)
            logger.debug(f"Directory created: {dirpath}")
            return dirpath
            
        except Exception as e:
            logger.error(f"Error creating directory {dirpath}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def __del__(self):
        """Clean up temporary files when this object is destroyed"""
        if self.auto_cleanup:
            try:
                self.cleanup_temp_files()
            except:
                # Don't let exceptions in __del__ propagate
                pass
    #TODO: Implement the following methods
    # Future database integration methods
    def upload_to_db(self, data: Any, collection: str) -> bool:
        """
        Placeholder for future database integration - upload data.
        
        Args:
            data: The data to upload
            collection: The database collection to upload to
            
        Returns:
            Success status
        """
        logger.warning("Database integration not implemented yet")
        return False
        
    def download_from_db(self, query: Dict, collection: str) -> Any:
        """
        Placeholder for future database integration - download data.
        
        Args:
            query: The database query
            collection: The database collection to query
            
        Returns:
            The retrieved data or None
        """
        logger.warning("Database integration not implemented yet")
        return None