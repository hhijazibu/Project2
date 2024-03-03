from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime

uri = "mongodb+srv://hhijazi:n5Qitx2U2rtjKgGE@dbclusterinfo.kdno63c.mongodb.net/?retryWrites=true&w=majority&appName=DbClusterInfo"

def auto_populate_db_from_user_input(client):
    db = client['DbClusterInfo']  
    
    documents_collection = db['Documents']
    
    title = input("Enter document title: ")
    fileType = input("Enter document file type (e.g., PDF, DOCX): ")
    contentText = input("Enter document content text: ")
    keywords = input("Enter document keywords (comma-separated): ").split(',')
    positive = float(input("Enter sentiment positive score (0 to 1): "))
    neutral = float(input("Enter sentiment neutral score (0 to 1): "))
    negative = float(input("Enter sentiment negative score (0 to 1): "))
    summary = input("Enter document summary: ")
    
    new_document = {
        "title": title,
        "fileType": fileType,
        "uploadDate": datetime.datetime.utcnow(),
        "contentText": contentText,
        "metadata": {
            "keywords": [keyword.strip() for keyword in keywords],  # Remove any leading/trailing whitespace
            "sentiments": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "summary": summary
        }
    }
    
    result = documents_collection.insert_one(new_document)
    print(f"Inserted document with ID: {result.inserted_id}")

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    auto_populate_db_from_user_input(client)
except Exception as e:
    print(e)
