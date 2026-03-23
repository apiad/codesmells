import json
import os

def process_user_data(file_path):
    print(f"Starting to process data from {file_path}")
    
    if not os.path.exists(file_path):
        print("File does not exist!")
        return None
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Do some processing
        processed = [d for d in data if d.get('active', False)]
        
        print(f"Successfully processed {len(processed)} active users.")
        return processed
        
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return None
