# Input data from CSV files into the MySQL database

import pandas as pd
import mysql.connector
from datetime import datetime
import locale

# Set locale to German for date parsing
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Load CSV data
all_proposals = pd.read_csv('data/all_proposals.csv')
all_projects = pd.read_csv('data/all_projects.csv')
all_comments = pd.read_csv('data/all_comments.csv')


# Connect to MySQL database
# TODO: Update the password and database name as needed
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="12345678",
    database="CitizenParticipation"
)
cursor = conn.cursor()

# Insert unique cities into the database
def insert_cities():
    cities = pd.concat([
        all_proposals[['City']],
        all_projects[['City']],
        all_comments[['City']]
    ]).drop_duplicates().rename(columns={'City': 'name'})

    print(cities)
    
    for _, row in cities.iterrows():
        cursor.execute("INSERT INTO Cities (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=name", (row['name'],))

    conn.commit()

insert_cities()

# Insert unique users into the database
def insert_users():    
    proposal_users = all_proposals[['Author']].rename(columns={'Author': 'username'})
    proposal_users['verified_status'] = 'not verified'
    
    comment_users = all_comments[['Username']].rename(columns={'Username': 'username'})
    comment_users['verified_status'] = 'not verified'
    
    users = pd.concat([proposal_users, comment_users]).fillna('Unknown').drop_duplicates()
    
    for _, row in users.iterrows():
        cursor.execute("INSERT INTO Users (username, verified_status) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username=username", (row['username'], row['verified_status']))

    conn.commit()

insert_users()

# Insert projects into the database
def insert_projects():
    projects = all_projects[['Project Title', 'Project Description', 'City', 'Proposal Count', 'Project URL']].rename(columns={
        'Project Title': 'title',
        'Project Description': 'description',
        'City': 'city_name',
        'Proposal Count': 'proposal_count',
        'Project URL': 'project_url'
    })
    
    for _, row in projects.iterrows():
        cursor.execute("SELECT id FROM Cities WHERE name=%s", (row['city_name'],))
        city_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO Projects (title, description, city_id, proposal_count, project_url) VALUES (%s, %s, %s, %s, %s)", 
                       (row['title'], row['description'], city_id, row['proposal_count'], row['project_url']))

    conn.commit()

insert_projects()

# Insert proposals into the database
def insert_proposals():
    proposals = all_proposals[['Title', 'Description', 'Proposed for Project', 'Author', 'Supporters', 'URL', 'City']].rename(columns={
        'Title': 'title',
        'Description': 'description',
        'Proposed for Project': 'project_title',
        'Author': 'author_username',
        'Supporters': 'supporters',
        'URL': 'proposal_url',
        'City': 'city_name'
    })
    
    # 🔹 Use separate cursors for reading and writing
    read_cursor = conn.cursor(buffered=True)  
    write_cursor = conn.cursor()

    for _, row in proposals.iterrows():
        try:
            # 🔹 Fetch project_id
            read_cursor.execute("SELECT id FROM Projects WHERE title = %s", (row['project_title'],))
            project_result = read_cursor.fetchone()
            read_cursor.fetchall()  # Prevent unread results
            project_id = project_result[0] if project_result else None  

            # 🔹 Fetch author_id
            author_username = row['author_username'].strip() if pd.notna(row['author_username']) else 'Unknown'
            read_cursor.execute("SELECT id FROM Users WHERE username = %s", (author_username,))
            author_result = read_cursor.fetchone()
            read_cursor.fetchall()  # Prevent unread results
            author_id = author_result[0] if author_result else None

            if author_id is None:
                read_cursor.execute("SELECT id FROM Users WHERE username = 'Unknown'")
                unknown_user_result = read_cursor.fetchone()
                read_cursor.fetchall()
                author_id = unknown_user_result[0] if unknown_user_result else None  

            # 🔹 Fetch city_id
            read_cursor.execute("SELECT id FROM Cities WHERE name = %s", (row['city_name'],))
            city_result = read_cursor.fetchone()
            read_cursor.fetchall()  # Prevent unread results
            city_id = city_result[0] if city_result else None

            print(f"Inserting Proposal: {row['title']}")
            print(f"  Project ID: {project_id}, Author ID: {author_id}, City ID: {city_id}")
            print(f"  Supporters: {row['supporters']}, URL: {row['proposal_url']}")

            if project_id is None:
                print(f"❌ Skipping: Project '{row['project_title']}' not found")
                continue
            if city_id is None:
                print(f"❌ Skipping: City '{row['city_name']}' not found")
                continue

            # 🔹 Insert Proposal
            write_cursor.execute("""
                INSERT INTO Proposals (title, description, project_id, author_id, supporters, proposal_url, city_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (row['title'], row['description'], project_id, author_id, row['supporters'], row['proposal_url'], city_id))

        except mysql.connector.Error as err:
            print(f"⚠️ MySQL Error: {err}")
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")

    conn.commit()
    read_cursor.close()
    write_cursor.close()

insert_proposals()

# Insert comments into the database
def insert_comments():
    comments = all_comments[['Text', 'Username', 'Project', 'Date', 'Likes', 'Dislikes']].rename(columns={
        'Text': 'text',
        'Username': 'username',
        'Project': 'project_title',
        'Date': 'date',
        'Likes': 'likes',
        'Dislikes': 'dislikes'
    })
    
    # Convert date format
    comments['date'] = comments['date'].apply(lambda x: datetime.strptime(x, '%d. %B %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))
    
    # Use separate cursors for reading and writing
    read_cursor = conn.cursor(buffered=True)
    write_cursor = conn.cursor()

    for _, row in comments.iterrows():
        try:
            # Find project_id
            read_cursor.execute("SELECT id FROM Projects WHERE title=%s", (row['project_title'],))
            project_result = read_cursor.fetchone()
            read_cursor.fetchall()  # Prevent unread results
            project_id = project_result[0] if project_result else None

            # Find user_id
            username = row['username'].strip() if pd.notna(row['username']) else 'Unknown'
            read_cursor.execute("SELECT id FROM Users WHERE username=%s", (username,))
            user_result = read_cursor.fetchone()
            read_cursor.fetchall()  # Prevent unread results
            user_id = user_result[0] if user_result else None

            if user_id is None:
                read_cursor.execute("SELECT id FROM Users WHERE username='Unknown'")
                unknown_user_result = read_cursor.fetchone()
                read_cursor.fetchall()
                user_id = unknown_user_result[0] if unknown_user_result else None

            print(f"Inserting Comment: {row['text'][:30]}...")
            print(f"  Project ID: {project_id}, User ID: {user_id}")
            print(f"  Date: {row['date']}, Likes: {row['likes']}, Dislikes: {row['dislikes']}")

            if project_id is None:
                print(f"❌ Skipping: Project '{row['project_title']}' not found")
                continue

            # Insert Comment
            write_cursor.execute("""
                INSERT INTO Comments (text, user_id, project_id, date, likes, dislikes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['text'], user_id, project_id, row['date'], row['likes'], row['dislikes']))

        except mysql.connector.Error as err:
            print(f"⚠️ MySQL Error: {err}")
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")

    conn.commit()
    read_cursor.close()
    write_cursor.close()

insert_comments()

# Close the connection
conn.close()
