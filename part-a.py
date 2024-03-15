from flask import Flask
import requests
import mysql.connector
import json

app = Flask(__name__)

# Create Dummy Api app_id 
app_id = "65f2d1ecd01b0a7c789abafa"

# Connect to PhpMySQL Database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='rohit123',
    database='test'
)

#Function to fetch data from api
def fetch_data_from_api():
    users_url = "https://dummyapi.io/data/v1/user"
    headers = {'app-id': app_id}
    response = requests.get(users_url, headers=headers)

    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Failed to fetch data from the API:", response.status_code)
        return None


#Fuction to store data to the phpMySQL from API
def store_data_to_mysql(data):
    try:
        cursor = connection.cursor()

        # Define table schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(10),
            firstName VARCHAR(100),
            lastName VARCHAR(100),
            picture TEXT
        )
        """
        cursor.execute(create_table_query)

        # Insert data into MySQL
        for item in data:
            query = "INSERT INTO users (id, title, firstName, lastName, picture)  VALUES (%s ,%s, %s, %s, %s)"
            values = (item['id'], item['title'], item['firstName'], item['lastName'], item['picture'])  # Replace with your actual data and column names
            cursor.execute(query, values)

        # Commit the transaction
        connection.commit()
        print("Data stored successfully in MySQL")

    except mysql.connector.Error as error:
        print("Failed to store data in MySQL:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")


# Function to fetch posts data from the API
def fetch_posts_data_from_api(user_id):
    url = f'https://dummyapi.io/data/v1/user/{user_id}/post'
    headers = {'app-id': app_id}  # Replace 'your_dummyapi_app_id' with your actual app ID
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to fetch posts data for user {user_id}:", response.status_code)
        return ['data']

# Function to store posts data in the database
def store_posts_data_to_database(posts_data):
    try:
        cursor = connection.cursor()

        # Define table schema for owners
        create_owners_table_query = """
        CREATE TABLE IF NOT EXISTS owners (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(50),
            firstName VARCHAR(50),
            lastName VARCHAR(50),
            picture VARCHAR(255)
        )
        """
        cursor.execute(create_owners_table_query)

        # Define table schema for posts
        create_posts_table_query = """
        CREATE TABLE IF NOT EXISTS posts (
            id VARCHAR(50) PRIMARY KEY,
            image VARCHAR(255),
            likes INT,
            tags VARCHAR(255),
            text VARCHAR(255),
            publishDate VARCHAR(50),
            ownerId VARCHAR(50),
            FOREIGN KEY (ownerId) REFERENCES owners(id)
        )
        """
        cursor.execute(create_posts_table_query)

        # Insert owner data into owners table
        for post in posts_data:
            owner = post['owner']
            insert_owner_query = """
            INSERT IGNORE INTO owners (id, title, firstName, lastName, picture)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_owner_query, (
                owner['id'],
                owner['title'],
                owner['firstName'],
                owner['lastName'],
                owner['picture']
            ))

        # Insert posts data into posts table
        for post in posts_data:
            owner = post['owner']
            insert_post_query = """
            INSERT INTO posts (id, image, likes, tags, text, publishDate, ownerId)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_post_query, (
                post['id'],
                post['image'],
                post['likes'],
                ','.join(post['tags']),
                post['text'],
                post['publishDate'],
                owner['id']
            ))


        # Commit the transaction
        connection.commit()
        print("Posts data stored successfully in the database")

    except mysql.connector.Error as error:
        print("Failed to store posts data in the database:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")


if __name__ == '__main__':
    #Get the data from API
    data = fetch_data_from_api()
    # If data exists 
    if(data):
        store_data_to_mysql(data)

    #Fecth the Corresponding posts data using API e.g.
    user = fetch_posts_data_from_api('60d0fe4f5311236168a109ca')
    # Posts Store in Database
    store_posts_data_to_database(user)