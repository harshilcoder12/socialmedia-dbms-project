import mysql.connector 
import pymongo
import datetime 

class Database_connector:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
    @staticmethod
    def write_logs(text , error=None):
        file = open('logs.txt','a')
        write = f"{datetime.datetime.now()}  {text}  {error} \n"
        file.write(write)
        file.close()
    #connecting to mysql database
    def connect_sql_db(self):
        try:
            self.conn = mysql.connector.connect(user='root',password ='harshiljain',database='socialmedia')
            self.cursor = self.conn.cursor()
            Database_connector.write_logs(' successfully connected to database')
        except Exception as e:
            Database_connector.write_logs(' error occured in connecting to the database: ',e)
    #Connecting to mongodb database
    def connect_mongo_db(self):
        try:
            db = self.client['socialmedia']
            Database_connector.write_logs('Successfully connected to mongodb')
        except Exception as e:
            Database_connector.write_logs('Not able to connect to the mongodb database ',e)
    #function to add documents in mongodb
    def add_data_mongo(self,collection,data):
        try:
            db = self.client['socialmedia']
            col = db[collection]
            col.insert_many(data)
            Database_connector.write_logs('successfully added to mongodb database')
        except Exception as e:
            Database_connector.write_logs('cannot add data to mongodb collection ',e)
'''
database = Database_connector()
database.connect_sql_db()
database.connect_mongo_db()
database.add_data_mongo('x',{
    "name": "Harshil Jain",
    "age": 18,
    "city": "Ahmedabad",
    "hobbies": ["coding", "football"]
})'''