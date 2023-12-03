from pymongo import MongoClient
from pprint import pprint
class SlackMessageWithSchema:
    def __init__(self, database_name='week0_network_analysis')-> None:
        self.client = MongoClient("mongodb://127.0.01:27017/")
        self.db = self.client[database_name]
        self.slack_messages_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["msg_type", "msg_content", "sender_name", "msg_sent_time", "msg_dist_type",
                             "time_thread_start", "reply_count", "reply_users_count", "reply_users", "tm_thread_end", "channel"],
                "properties": {
                    "msg_type": {"bsonType": "string", "description": "must be a string and is required"},
                    "msg_content": {"bsonType": "string", "description": "must be a string and is required"},
                    "sender_name": {"bsonType": "string", "description": "must be a string and is required"},
                    "msg_sent_time": {"bsonType": "string", "description": "must be a string and is required"},
                    "msg_dist_type": {"bsonType": "string", "description": "must be a string and is required"},
                    "time_thread_start": {"bsonType": "string", "description": "must be a string and is required"},
                    "reply_count": {"bsonType": "int", "description": "must be an integer and is required"},
                    "reply_users_count": {"bsonType": "int", "description": "must be an integer and is required"},
                    "reply_users": {"bsonType": "string", "description": "must be a string and is required"},
                    "tm_thread_end": {"bsonType": "string", "description": "must be a string and is required"},
                    "channel": {"bsonType": "string", "description": "must be a string and is required"},
                }
            }
        }
        
        
        self.reactions_validator = {
                        "$jsonSchema": {
                            "bsonType": "object",
                
                        }
        }
        
        self.replies_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sender_name", "Message count", "Mention count", "Reply count", "Total count"],
            "properties": {
                "sender_name": {
                    "bsonType": ["string", "null"],
                    "description": "Name of the message sender"
                },
                "Message count": {
                    "bsonType": ["int", "null"],
                    "description": "Count of messages sent by the user"
                },
                "Mention count": {
                    "bsonType": ["int", "null"],
                    "description": "Count of mentions in messages by the user"
                },
                "Reply count": {
                    "bsonType": ["int", "null"],
                    "description": "Count of replies sent by the user"
                },
                "Total count": {
                    "bsonType": ["int", "null"],
                    "description": "Total count of messages, mentions, and replies by the user"
                },
                # Exclude irrelevant fields from validation
            }
        }
    }



        
        try:
            self.db.create_collection("slack_messages")
            self.db.create_collection("reactions")
            self.db.create_collection("replies")
        except Exception as e:
            print(e)
        self.db.command("collMod", "slack_messages", validator= self.slack_messages_validator)
        self.db.command("collMod", "reactions", validator=self.reactions_validator)
        self.db.command("collMod", "replies", validator= self.replies_validator)
        
    def list_collections(self):
        return self.db.list_collection_names()

    def get_validation(self, collection_name: str) -> dict:
        self.check_if_collection_exist(collection_name)
        return self.db.get_collection(collection_name).options()

    def check_if_collection_exist(self, collection_name: str):
        if not self.list_collections().__contains__(collection_name):
            raise Exception(f"Collection, {collection_name} not found.")

    def insert_to_collection(self, collection_name, data):
        self.check_if_collection_exist(collection_name)
        collection = self.db[collection_name]
        return collection.insert_one(data)

    def insert_many_to_collection(self, collection_name, data):
        self.check_if_collection_exist(collection_name)
        result = self.db[collection_name].insert_many(data)
        return result.inserted_ids

    def find_all(self, collection_name):
        self.check_if_collection_exist(collection_name)
        return self.db[collection_name].find()

    def find(self, collection_name, key, value):
        self.check_if_collection_exist(collection_name)
        return self.db[collection_name].find({key: value})

    def find_by_id(self, collection_name, _id):
        self.check_if_collection_exist(collection_name)
        return self.db[collection_name].find

    def find_one(self, collection_name, key, value):
        self.check_if_collection_exist(collection_name)
        return self.db[collection_name].find_one({key: value})


    