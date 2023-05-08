# import os
# from dotenv import load_dotenv
# from mysql.connector import Error
# import mysql.connector

import datetime
from prisma import Prisma
import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import logging
logging.basicConfig()
load_dotenv()


prisma = Prisma()


# the user model is essentially the superset of the student and teacher model.
# the user model has - id, fullname, email, password, contact no. and role that is either student or teacher
# the role is a field in the user model that is used to differentiate between a student and a teacher
def prismaFindMany():
    prisma.connect()
    prisma.comment.delete_many()
    prisma.post.delete_many()
    post = prisma.post.create({
        "title": "My new post",
        "published": True,
    })
    print(f"post: {post.json(indent=2)}\n")
    first = prisma.comment.create({
        "content": "First comment!",
        "post": {
            "connect": {
                "id": post.id
            }
        }
    }, include={"post": True}
    )
    print(f"first comment: {first.json(indent=2)}\n")
    second = prisma.comment.create({
        "content": "Second comment!",
        "post": {
            "connect": {
                "id": post.id
            }
        }
    })
    print(f"second comment: {second.json(indent=2)}\n")

    comments = prisma.comment.find_many(
        where={
            "post_id": post.id
        }
    )
    print(f"comments of posts with id {post.id}")
    for comment in comments:
        print(comment.json(indent=2))

    prisma.disconnect()


def prismacreateuser():
    prisma.connect()
    course = prisma.course.create(
        data={
            "name": "Software Engineering",
            "courseDetails": """Software Engineering is the application of engineering to the development of software in a systematic method. 
            Notable definitions of software engineering include: the systematic application of scientific and technological knowledge, methods, 
            and experience to the design, implementation, testing, and documentation of software.""",
        }
    )
    print(f"{course.json(indent=2)}\n")
    user = prisma.user.create(
        data={
            "fullName": "Matthew Loh Yet Marn",
            "email": "p21013568@student.newinti.edu.my",
            "password": "inserthashhere",
            "isAdmin": True,
            "contactNo": "0123456789",
            "courses": {
                "connect": {"userId_courseId": course.id}
            },
        },
    )
# connection = mysql.connector.connect(
#     host=os.getenv("DB_HOST"),
#     database=os.getenv("DB_DATABASE"),
#     user=os.getenv("DB_USERNAME"),
#     password=os.getenv("DB_PASSWORD"),
#     ssl_ca=os.getenv("SSL_CERT"),
# )

# try:
#     if connection.is_connected():
#         c = connection.cursor()
#     with connection:
#         # c.execute("select @@version ")
#         # version = c.fetchone()
#         # if version:
#             # print('Running version: ', version)
#         # else:
#             # print('Not connected.')

#         c.execute("""
#                 SELECT * FROM User
#                 """)
#         results = c.fetchall()
#         print(results)
#     # connection.close()
# except Error as e:
#     print("Error while connecting to MySQL", e)
# finally:
#     connection.close()

# def create_connection():
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#     host=os.getenv("DB_HOST"),
#     database=os.getenv("DB_DATABASE"),
#     user=os.getenv("DB_USERNAME"),
#     password=os.getenv("DB_PASSWORD"),
#     ssl_ca=os.getenv("SSL_CERT")
# )
#         print("Connection to MySQL DB successful")
#     except Error as e:
#         print(f"The error '{e}' occurred")

#     return connection

# def execute_query(connection, query):
#     cursor = connection.cursor(buffered=True)
#     try:
#         cursor.execute(query)
#         connection.commit()
#         print("Query executed successfully")
#     except Error as e:
#         print(f"The error '{e}' occurred")


if __name__ == "__main__":
    # connection = create_connection()
    # execute_query(connection, "SHOW TABLES")
    prismacreateuser()
