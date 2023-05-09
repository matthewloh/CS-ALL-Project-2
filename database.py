import json
import logging
import datetime
import os
from dotenv import load_dotenv
# ~~~~ MYSQL ~~~~
# import os
# from dotenv import load_dotenv
# from mysql.connector import Error
# from mysql.connector import Error
# import mysql.connector
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

# ~~~~ PRISMA ~~~~
from prisma import Prisma
load_dotenv()

logging.basicConfig()

prisma = Prisma()
# the model goes as such, first create an institution and a school.


def prismaCreateInstitution():
    prisma.connect()
    prisma.school.delete_many()
    prisma.institution.delete_many()
    institution = prisma.institution.create(
        data={
            "institutionCode": "IICP",
            "school": {
                "create": {
                    "schoolCode": "SOC",
                    "name": "School of Computing",
                    "description": "The School Of Computing includes BCSCU, BCTCU, DCS for now.",

                }
            }
        },
        include={"school": True}
    )

    print(f"{institution.json(indent=2)}\n")


def prismaCreateProgramme():
    prisma.connect()
    test = (prisma.institution.find_many(include={"school": True}))
    for i in test:
        print(f"Institutions:\n{i.json(indent=2)}\n")

    """
    Returns:
    [Institution(id='clhf0quvy0000vtmka1lvufai', institutionCode='IICP', school=[School(id='clhf0quvy0001vtmkv6i6pmqu', schoolCode='SOC', name='School of Computing', description='The School Of Computing includes BCSCU, BCTCU, DCS for now.', institutionId='clhf0quvy0000vtmka1lvufai', institution=None, programme=None, students=None)])]
    """
    # print(jsonified)
    findschool = prisma.school.find_first(where={"schoolCode": "SOC"})
    """
    Returns:
    [School(id='clhf0quvy0001vtmkv6i6pmqu', schoolCode='SOC', name='School of Computing', description='The School Of Computing includes BCSCU, BCTCU, DCS for now.', institutionId='clhf0quvy0000vtmka1lvufai', institution=None, programme=None, students=None)]
    """
    # findschool.json(indent=2)
    print(f"School:\n{findschool.json(indent=2)}\n")
    prisma.programme.delete_many()
    programme = prisma.programme.create(
        data={
            "programmeCode": "BCSCU",
            "programmeName": "Bachelor of Computer Science in Collaboration with Coventry University",
            "programmeDesc": "Computer science explores the core of modern technology, offering powerful problem-solving methods.",
            "school": {
                "connect": {
                    "id": findschool.id
                }
            }
        },
        # include={"school": True, "modules": True, "lecturers": True}
    )
    print(f"Programme:\n{programme.json(indent=2)}\n")
    prisma.disconnect()


def prismaCreateModules():
    prisma.connect()
    programme = prisma.programme.find_first(where={"programmeCode": "BCSCU"})
    prisma.module.delete_many()
    modules = prisma.module.create(
        data={
            "moduleCode": "INT4004CEM",
            "moduleTitle": "Computer Architecture and Networks",
            "moduleDesc": "This module aims to provide students with a comprehensive understanding of the fundamental concepts of computer architecture and networks.",
            "programme": {
                "connect": {
                    "id": programme.id
                }
            },
            "lecturer": ""
        }
    )
    print(f"{modules.json(indent=2)}\n")


def prismaCreateLecturer():
    prisma.connect()
    school = prisma.school.find_first(where={"schoolCode": "SOC"})
    prisma.module.delete_many()
    prisma.lecturer.delete_many()
    prisma.userprofile.delete_many()
    lecturer = prisma.lecturer.create(
        data={
            "school": {
                "connect": {
                    "id": school.id
                }
            },
            "userProfile": {
                "create": {
                    "fullName": "Dr. Vaithegy Doraisamy",
                    "email": "vaithegy.doraisamy@newinti.edu.my",
                    "password": "hashofapassword",
                    "contactNo": "+60149447359"
                }
            }
        },
        include={"userProfile": True, "modules": True, "school": True}
    )
    # lecturer = prisma.lecturer.create(
    #     data={
    #         "fullName": "Dr. Vaithegy Doraisamy",
    #         "email": "vaithegy.doraisamy@newinti.edu.my",
    #         "password": "hashofapassword",
    #         "contactNo": "+60149447359",
    #         "school": {
    #             "connect": {
    #                 "id": school.id
    #             }
    #         }
    #     },
    #     include={
    #         "school": True,
    #         "modules": True
    #     }
    # )
    print(f"Lecturer created:\n{lecturer.json(indent=2)}\n")
    prismaCreateModules()


def prismaCreateModules():
    # prisma.connect()
    programme = prisma.programme.find_first(where={"programmeCode": "BCSCU"})
    # lecturer = prisma.userprofile.find_first(where={"fullName": "Dr. Vaithegy Doraisamy"})
    lecturer = prisma.lecturer.find_first(
        where={
            "userProfile": {"fullName": "Dr. Vaithegy Doraisamy"}
        },
        include={"userProfile": True, "modules": True, "school": True}
    )
    print(f"Lecturer returned:\n{lecturer.json(indent=2)}\n")
    firstcourse = prisma.module.create(
        data={
            "moduleCode": "INT4004CEM",
            "moduleTitle": "Computer Architecture and Networks",
            "moduleDesc": "This module aims to provide students with a comprehensive understanding of the fundamental concepts of computer architecture and networks.",
            "programme": {
                "connect": {
                    "id": programme.id
                }
            },
            "lecturer": {
                "connect": {
                    "id": lecturer.id
                }
            }
        }, include={"programme": True, "lecturer": True, "moduleEnrollments": True}
    )
    print(f"Module 1 created:\n{firstcourse.json(indent=2)}\n")
    secondcourse = prisma.module.create(
        data={
            "moduleCode": "INT4007CEM/INT4009CEM",
            "moduleTitle": "Computer Science Activity Led Learning Project 2",
            "moduleDesc": """This module hosts the second Activity Led Learning (ALL) Project. Students are set a project related to their chosen course which requires skills and knowledge presented and developed in the other modules studied in the semester, object-oriented programming and computer architecture and network.""",
            "programme": {
                "connect": {
                    "id": programme.id
                }
            },
            "lecturer": {
                "connect": {
                    "id": lecturer.id
                }
            }
        }
    )
    print(f"Module 2 created:\n{secondcourse.json(indent=2)}\n")
    # check = prisma.lecturer.find_first(
    #     where={"fullName": "Dr. Vaithegy Doraisamy"},
    #     include={"modules": True, "school": True}
    # )
    # print(f"Check Lecturer Profile:\n{check.json(indent=2)}\n")
    prisma.disconnect()


def prismaCreateStudent():
    prisma.connect()
    # school = prisma.school.find_first(where={"schoolCode": "SOC"})
    # module1 = prisma.module.find_first(where={"moduleCode": "INT4004CEM"})
    # module2 = prisma.module.find_first(
    #     where={"moduleCode": "INT4007CEM/INT4009CEM"})
    # prisma.moduleenrollment.delete_many()
    # prisma.student.delete_many()
    # # We need to use moduleEnrollments to create a student instead of directly using modules
    # student = prisma.student.create(
    #     data={
    #         "fullName": "Matthew Loh Yet Marn",
    #         "email": "p21013568@student.newinti.edu.my",
    #         "password": "hashofapassword123",
    #         "contactNo": "+60193884019",
    #         "school": {
    #             "connect": {
    #                 "id": school.id
    #             }
    #         },
    #         "modules": {
    #             "create": [
    #                 {
    #                     "enrollmentGrade": 0,
    #                     "moduleId": module1.id
    #                 },
    #                 {
    #                     "enrollmentGrade": 0,
    #                     "moduleId": module2.id
    #                 }
    #             ]
    #         },
    #     }, include={"modules": True, "school": True}
    # )
    # print(f"Student created:\n{student.json(indent=2)}\n")
    # getting the programme of the student by getting the linked module's id and then getting the programme's id
    student = prisma.student.find_first(
        where={"fullName": "Matthew Loh Yet Marn"},
    )
    print(f"Student:\n{student.json(indent=2)}\n")
    moduleenrollment = prisma.moduleenrollment.find_many(
        where={"studentId": student.id}
    )
    for me in moduleenrollment:
        # print(f"Module Enrollment:\n{me.json(indent=2)}\n")
        module = prisma.module.find_first(
            where={"id": me.moduleId}, include={"programme": True, "lecturer": True}
        )
        print(f"Module:\n{module.json(indent=2)}\n")
    # print(f"Programme of student:\n{programme.json(indent=2)}\n")


def prismaqueryAll():
    prisma.connect()
    institution = prisma.institution.find_many(
        include={"school": True}
    )
    for i in institution:
        print(f"Institution: {i.json(indent=2)}\n")
    school = prisma.school.find_many(
        include={"institution": True, "programme": True,
                 "students": True, "lecturer": True}
    )
    for s in school:
        print(f"School: {s.json(indent=2)}\n")
    lecturers = prisma.lecturer.find_many(
        include={"school": True, "modules": True}
    )
    for l in lecturers:
        print(f"Lecturer: {l.json(indent=2)}\n")
    modules = prisma.module.find_many(
        include={"programme": True, "lecturer": True,
                 "moduleEnrollments": True}
    )
    for m in modules:
        print(f"Module: {m.json(indent=2)}\n")
    students = prisma.student.find_many(
        include={"school": True, "modules": True}
    )
    for s in students:
        print(f"Student: {s.json(indent=2)}\n")


if __name__ == "__main__":
    # ~~~~ MYSQL ~~~~
    # connection = create_connection()
    # execute_query(connection, "SHOW TABLES")
    # ~~~~ PRISMA ~~~~
    # prismaCreateInstitution()
    # prismaCreateProgramme()
    prismaCreateLecturer()
    # prismaCreateStudent()
    # prismaqueryAll()
