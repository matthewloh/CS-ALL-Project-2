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
from prisma.models import UserProfile
from prisma.bases import BaseUserProfile



load_dotenv()

logging.basicConfig()

prisma = Prisma(auto_register=True)





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
    school = prisma.school.find_first(where={"schoolCode": "SOC"})
    module1 = prisma.module.find_first(
        where={"moduleCode": "INT4004CEM"},
        include={"lecturer": True, "moduleEnrollments": True, "programme": True}
    )
    findlecturer = prisma.lecturer.find_many(
        where={"id": module1.lecturer.id},
        include={"userProfile": True, "modules": True, "school": True}
    )
    module2 = prisma.module.find_first(
        where={"moduleCode": "INT4007CEM/INT4009CEM"})
    print(f"Find Lecturer:\n{findlecturer.json(indent=2)}\n")
    print(f"Module 1:\n{module1.json(indent=2)}\n")
    print(f"Module 2:\n{module2.json(indent=2)}\n")
    prisma.moduleenrollment.delete_many()
    prisma.student.delete_many()
    prisma.userprofile.delete_many()
    prisma.userprofile.delete(
        where={"email": "p21013568@student.newinti.edu.my"}
    )
    # # We need to use moduleEnrollments to create a student instead of directly using modules
    student = prisma.student.create(
        data={
            "userProfile": {
                "create": {
                    "fullName": "Matthew Loh Yet Marn",
                    "email": "p21013568@student.newinti.edu.my",
                    "password": "hashofapassword",
                    "contactNo": "+60193884019"
                }
            },
            "school": {
                "connect": {
                    "id": school.id
                }
            },
            "modules": {
                "create": [
                    {
                        "enrollmentGrade": 0,
                        "moduleId": module1.id
                    },
                    {
                        "enrollmentGrade": 0,
                        "moduleId": module2.id
                    }
                ]
            }
        }
    )
    print(f"Student created:\n{student.json(indent=2)}\n")
    # getting the programme of the student by getting the linked module's id and then getting the programme's id
    student = prisma.student.find_first(
        where={
            "userProfile": {
                "email": "p21013568@student.newinti.edu.my",
            }
        },
        include={"modules": True, "school": True, "userProfile": True}
    )
    print(f"Student:\n{student.json(indent=2)}\n")
    moduleenrollment = prisma.moduleenrollment.find_many(
        where={"studentId": student.id}
    )
    print(f"Module Enrollment:\n{moduleenrollment}\n")
    for me in moduleenrollment:
        # print(f"Module Enrollment:\n{me.json(indent=2)}\n")
        module = prisma.module.find_first(
            where={
                "id": me.moduleId
            }
        )
        print(f"Module {me.moduleId}:\n{module.json(indent=2)}\n")
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


def prisQueryModuleEnrollment():
    prisma.connect()
    moduleenrollment = prisma.moduleenrollment.find_many(
        include={
            "student": {
                "include": {
                    "userProfile": True,
                    "school": True
                }
            },
            "module": {
                "include": {
                    "lecturer": {
                        "include": {
                            "userProfile": True
                        }
                    },
                    "programme": {
                        "include": {
                            "modules": {"where": {"moduleCode": "INT4004CEM"}}
                        }
                    }
                }
            }
        }
    )
    for me in moduleenrollment:
        print(f"Module Enrollment:\n{me.json(indent=2)}\n")
        module = prisma.module.find_first(
            where={
                "id": me.moduleId
            }
        )
        print(f"Module {me.moduleId}:\n{module.json(indent=2)}\n")


def prisQueryUserProfile():
    prisma.connect()
    userprofile = prisma.userprofile.find_many(
        where={
            "email": {
                "endswith": "@student.newinti.edu.my"
            }
        },
        include={
            "lecturer": {
                "include": {
                    "modules": {
                        "include": {
                            "lecturer": True
                        }
                    },
                    "school": True,
                    "userProfile": True
                }
            },
            "student": {
                "include": {
                    "userProfile": {
                        "include": {
                            "lecturer": True,
                        }
                    },
                    "school": True,
                    "modules": {
                        "include": {
                            "student": True,
                            "module": True
                        }

                    }
                }
            }
        }
    )
    for up in userprofile:
        print(f"User Profile:\n{up.json(indent=2)}\n")


def prisCreateMultipleModules():
    prisma.connect()
    # programme = prisma.programme.find_first(
    #     where={
    #         "programmeCode": "BCSCU"
    #     }
    # )
    # prisma.module.delete_many(
    #     where={
    #         "moduleTitle": "Mathematics for Computer Science" or "Object Oriented Programming",
    #     }
    # )
    # prisma.module.delete(
    #     where={
    #         "moduleCode": "INT4068CEM"
    #     }
    # )
    # prisma.module.delete(
    #     where={
    #         "moduleCode": "INT4003CEM"
    #     }
    # )
    # modules = prisma.module.create_many(
    #     data=[
    #         {
    #             "moduleCode": "INT4068CEM",
    #             "moduleTitle": "Mathematics for Computer Science",
    #             "moduleDesc": "This module introduces the mathematical foundations of computer science, including logic, sets, relations, functions, and graphs. It also covers the basics of counting and discrete probability, and the analysis of algorithms.",
    #             "programmeId": programme.id
    #         },
    #         {
    #             "moduleCode": "INT4003CEM",
    #             "moduleTitle": "Object Oriented Programming",
    #             "moduleDesc": "This module introduces the concepts of object-oriented programming using the C++ programming language. Topics include classes, objects, encapsulation, inheritance, polymorphism, and templates.",
    #             "programmeId": programme.id
    #         }
    #     ],
    # )
    actualmodules = prisma.module.find_many()
    counter = 0
    for m in actualmodules:
        counter += 1
        # print(f"Module {counter}:\n{m.json(indent=2)}\n")
        module = prisma.module.find_first(
            where={
                "moduleTitle": m.moduleTitle
            },
            include={
                "lecturer": True,
                "programme": True,
                "moduleEnrollments": True,
            }
        )
        print(f"{counter}. {m.moduleTitle}:\n{module.json(indent=2)}\n")
        for m in module.moduleEnrollments:
            search = m.studentId
            student = prisma.student.find_first(
                where={
                    "id": search
                },
                include={
                    "userProfile": True,
                }
            )
            print(
                f"Student {student.userProfile.fullName} in {module.moduleTitle}:\n{student.json(indent=2)}\n")
# https://prisma-client-py.readthedocs.io/en/stable/reference/model-actions/
# https://prisma-client-py.readthedocs.io/en/stable/reference/selecting-fields/#writing-queries
class UserInPost(BaseUserProfile):
    fullName: str
    email: str
    contactNo: str
def usingpartialTypes():
    prisma.connect()
    user = UserInPost.prisma().find_first(
        where={
            "fullName": "Matthew Loh Yet Marn"
        },
    )
    _user = prisma.userprofile.find_first(
        where={
            "fullName": "Matthew Loh Yet Marn"
        },
    )
    print(f"User:\n{user.json(indent=2)}\n")
    print(f"_User:\n{_user.json(indent=2)}\n")

if __name__ == "__main__":
    # ~~~~ MYSQL ~~~~
    # connection = create_connection()
    # execute_query(connection, "SHOW TABLES")
    # ~~~~ PRISMA ~~~~
    # prismaCreateInstitution()
    # prismaCreateProgramme()
    # prismaCreateLecturer()
    # prismaCreateStudent()
    # prismaqueryAll()
    # prisQueryModuleEnrollment()
    # prisQueryUserProfile()
    # prisCreateMultipleModules()
    usingpartialTypes()
