import requests
from bs4 import BeautifulSoup
import mysql.connector


# Connect to PhpMySQL Database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='rohit123',
    database='books'
)


# Scrape the Data
url = 'http://books.toscrape.com/' 
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Assuming you want to scrape book titles
book_titles = [title.text.strip() for title in soup.find_all('h3')]

# Organize the Data 
# A) Prices
prices = [price.text.strip() for price in soup.find_all('p', class_='product_price')]

# B) Prices
availability = [availability.text.strip() for availability in soup.find_all('p', class_='instock availability')]

# C) ratings
rating_elements = soup.find_all('p', class_='star-rating') 
# Extract ratings from the elements and store in a list
ratings = [rating['class'][1] for rating in rating_elements]


def store_books_database():
    try:
        cursor = connection.cursor()

        # Define table schema for books
        create_books_table = """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150),
            price VARCHAR(10),
            availability VARCHAR(50),
            rating VARCHAR(10)
        )
        """
        cursor.execute(create_books_table)

        # Insert Data
        for title, price, avail, rating in zip(book_titles, prices, availability, ratings):
            cursor.execute("""
            INSERT INTO books (name, price, availability, rating)
            VALUES (%s, %s, %s, %s)
            """, (title, price, avail, rating))
            
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
    # Store books data in database
    store_books_database()
