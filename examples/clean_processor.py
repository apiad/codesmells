import json
import os
import logging

logger = logging.getLogger(__name__)

def process_user_data(file_path):
    logger.info(f"Starting to process data from {file_path}")
    
    if not os.path.exists(file_path):
        logger.error("File does not exist!")
        return None
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Do some processing
        processed = [d for d in data if d.get('active', False)]
        
        logger.info(f"Successfully processed {len(processed)} active users.")
        return processed
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON data: {e}")
        return None
    except OSError as e:
        logger.error(f"File system error occurred: {e}")
        return None
