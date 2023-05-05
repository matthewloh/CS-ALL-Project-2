# import os
# from dotenv import load_dotenv
# from mysql.connector import Error
# import mysql.connector

import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import logging
logging.basicConfig()
load_dotenv()

from prisma import Prisma

prisma = Prisma()



# the user model is essentially the superset of the student and teacher model.
# the user model has - id, fullname, email, password, contact no. and role that is either student or teacher
# the role is a field in the user model that is used to differentiate between a student and a teacher
def prismaFindMany():
    prisma.connect()
    user = prisma.lecturer.find_many(
        where={
            "currTeachingCourses" : {
                "contains": "Object-Oriented Programming"
            }
        }
        
    )
    for item in user:
        print(str(item) + "\n")
    prisma.disconnect()


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
    prismaFindMany()
