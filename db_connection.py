import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get('MONGODB_URL')
client = pymongo.MongoClient(url)
db = client['archimed']