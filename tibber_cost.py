import os
from dotenv import load_dotenv

load_dotenv()

tibber_token = os.getenv('TIBBER_TOKEN')
house_id = os.getenv('HOUSE_ID')