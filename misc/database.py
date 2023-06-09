import base64
import io
import json
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pendulum import timezone

# ~~~~ MYSQL ~~~~
# import os
# from dotenv import load_dotenv
# from mysql.connector import Error
# from mysql.connector import Error
# import mysql.connector
# load_dotenv()
# connection = mysql.connector.connect(
#     host=os.getenv("DB_HOST"),
#     database=os.getenv("DB_DATABASE"),
#     user=os.getenv("DB_USERNAME"),
#     password=os.getenv("DB_PASSWORD"),
#     ssl_ca=os.getenv("SSL_CERT"),
# )
# try:
#     if connection.is_connected():
#         cursor = connection.cursor()
#     cursor.execute("select @@version ")
#     version = cursor.fetchone()
#     if version:
#         print('Running version: ', version)
#     else:
#         print('Not connected.')
# except Error as e:
#     print("Error while connecting to MySQL", e)
# finally:
#     connection.close()
# import os
# from dotenv import load_dotenv
# from mysql.connector import Error
# import mysql.connector


# connection = mysql.connector.connect(
# host=os.getenv("HOST"),
# database=os.getenv("DATABASE"),
# user=os.getenv("USERNAME"),
# password=os.getenv("PASSWORD"),
# ssl_ca=os.getenv("SSL_CERT")
# )

# try:
#     if connection.is_connected():
#         cursor = connection.cursor()
#     cursor.execute("select @@version ")
#     version = cursor.fetchone()
#     if version:
#         print('Running version: ', version)
#     else:
#         print('Not connected.')
# except Error as e:
#     print("Error while connecting to MySQL", e)
# finally:
#     connection.close()

# ~~~~ PRISMA ~~~~
from prisma import Prisma, Json, Base64
from prisma.models import UserProfile
from prisma.bases import BaseUserProfile, BaseModule, BaseModuleEnrollment
from PIL import Image, ImageOps

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
    test = prisma.institution.find_many(include={"school": True})
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
    print(f"Lecturer created:\n{lecturer.json(indent=2)}\n")
    lecturer2 = prisma.lecturer.create(
        data={
            "school": {
                "connect": {
                    "id": school.id
                }
            },
            "userProfile": {
                "create": {
                    "fullName": "Wei Jian Teng",
                    "email": "weijian.teng@newinti.edu.my",
                    "password": "hehe1234",
                    "contactNo": "+60123456789"
                }
            }
        },
        include={"userProfile": True, "modules": True, "school": True}
    )
    print(f"Lecturer created:\n{lecturer2.json(indent=2)}\n")
    lecturer3 = prisma.lecturer.create(
        data={
            "school": {
                "connect": {
                    "id": school.id
                }
            },
            "userProfile": {
                "create": {
                    "fullName": "Shyamala Nadarajan",
                    "email": "shyamala.nadarajan@s.newinti.edu.my",
                    "password": "hehe1234",
                    "contactNo": "+60164154155"
                }
            }
        },
        include={"userProfile": True, "modules": True, "school": True}
    )
    print(f"Lecturer created:\n{lecturer3.json(indent=2)}\n")
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
    lecturer2 = prisma.lecturer.find_first(
        where={
            "userProfile": {"fullName": "Wei Jian Teng"}
        },
        include={"userProfile": True, "modules": True, "school": True}
    )
    lecturer3 = prisma.lecturer.find_first(
        where={
            "userProfile": {"fullName": "Shyamala Nadarajan"}
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
    thirdcourse = prisma.module.create(
        data={
            "moduleCode": "INT4068CEM",
            "moduleTitle": "Mathematics for Computer Science",
            "moduleDesc": """This module aims to provide students with a comprehensive understanding of the fundamental concepts of mathematics for computer science.""",
            "programme": {
                "connect": {
                    "id": programme.id
                }
            },
            "lecturer": {
                "connect": {
                    "id": lecturer2.id
                }
            }
        },
    )
    fourthcourse = prisma.module.create(
        data={
            "moduleCode": "INT4003CEM",
            "moduleTitle": "Object-Oriented Programming",
            "moduleDesc": """This module aims to provide students with a comprehensive understanding of the fundamental concepts of object-oriented programming.""",
            "programme": {
                "connect": {
                    "id": programme.id
                }
            },
            "lecturer": {
                "connect": {
                    "id": lecturer3.id
                }
            }
        }
    )
    print(f"Module 3 created:\n{thirdcourse.json(indent=2)}\n")
    print(f"Module 4 created:\n{fourthcourse.json(indent=2)}\n")
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
    programme = prisma.programme.find_first(
        where={
            "programmeCode": "BCSCU"
        }
    )
    module = prisma.module.create(
        data={
            "moduleCode": "INT40"
        }
    )
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
    # actualmodules = prisma.module.find_many()
    # counter = 0
    # for m in actualmodules:
    #     counter += 1
    #     # print(f"Module {counter}:\n{m.json(indent=2)}\n")
    #     module = prisma.module.find_first(
    #         where={
    #             "moduleTitle": m.moduleTitle
    #         },
    #         include={
    #             "lecturer": True,
    #             "programme": True,
    #             "moduleEnrollments": True,
    #         }
    #     )
    #     print(f"{counter}. {m.moduleTitle}:\n{module.json(indent=2)}\n")
    #     for m in module.moduleEnrollments:
    #         search = m.studentId
    #         student = prisma.student.find_first(
    #             where={
    #                 "id": search
    #             },
    #             include={
    #                 "userProfile": True,
    #             }
    #         )
    #         print(
    #             f"Student {student.userProfile.fullName} in {module.moduleTitle}:\n{student.json(indent=2)}\n")
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
            "contactNo": "+60193884019"
        },
    )
    print(user.id)
    _user = prisma.userprofile.find_first(
        where={
            "fullName": "Matthew Loh Yet Marn"
        },
    )
    print(f"User:\n{user.json(indent=2)}\n")
    print(f"_User:\n{_user.json(indent=2)}\n")


class ModuleWithID(BaseModule):
    id: int


def creatingmoduleenrollments():
    prisma.connect()
    # data = {
    #     "fullName": "Matthew Loh Yet Marn",
    #     "email": "dummy",
    #     "password": "test1234",
    #     "contactNo": "+60193884019",
    #     "school": "SOC",
    #     # "session": "APR2023",
    #     "tenure": "FULLTIME",
    #     "currentCourses": ["Mathematics for Computer Science", "Object-Oriented Programming",
    #                        "Computer Science Activity Led Learning 2", "Computer Architecture and Networks"],
    #     # "role": "STUDENT",
    #     "role": "LECTURER",
    # }
    data = {
        "fullName": "Wei Jian Teng",
        "email": "weijian.teng@newinti.edu.my",
        "password": "testpassword",
        "contactNo": "+60191234567",
        "school": "SOC",
        # "session": "APR2023",
        "tenure": "FULLTIME",
        "currentCourses": ["Mathematics for Computer Science"],
        # "role": "STUDENT",
        "role": "LECTURER",
    }

    # try:
    if data["role"] == "STUDENT":
        school = prisma.school.find_first(
            where={
                "schoolCode": data["school"]
            }
        )
        prisma.moduleenrollment.delete_many(
            where={
                "student": {
                    "is": {
                        "userProfile": {
                            "is": {
                                "email": "dummy"
                            }
                        }
                    }
                }
            }
        )
        prisma.student.delete_many(
            where={
                "userProfile": {
                    "is": {
                        "email": "dummy"
                    }
                }
            }
        )
        prisma.userprofile.delete_many(
            where={
                "email": "dummy"
            }
        )
        student = prisma.student.create(
            data={
                "userProfile": {
                    "create": {
                        "fullName": data["fullName"],
                        "email": data["email"],
                        "password": data["password"],
                        "contactNo": data["contactNo"],
                    }
                },
                "school": {
                    "connect": {
                        "id": school.id
                    }
                },
                "session": data["session"],
            }
        )
        modulestoconnect = []
        for module in data["currentCourses"]:
            module = prisma.module.find_first(
                where={
                    "moduleTitle": module
                }
            )
            modulestoconnect.append(module.id)
        print(modulestoconnect)
        for i in range(len(modulestoconnect)):
            student = prisma.student.find_first(
                where={
                    "userProfile": {
                        "is": {
                            "email": "dummy",
                        }
                    }
                }
            )
            # print(f"Student:\n{student.json(indent=2)}\n")
            update = prisma.student.update(
                where={
                    "id": student.id
                },
                data={
                    "modules": {
                        "create": {
                            "enrollmentGrade": 0,
                            "moduleId": modulestoconnect[i]
                        }
                    }
                },
                include={
                    "userProfile": True,
                    "modules": True,
                }
            )
        print(f"Updated Student:\n{update.json(indent=2)}\n")
    elif data["role"] == "LECTURER":
        school = prisma.school.find_first(
            where={
                "schoolCode": data["school"]
            }
        )
        modules = prisma.module.find_many(
            where={
                "lecturer": {
                    "is": {
                        "userProfile": {
                            "is": {
                                "email": data["email"]
                            }
                        }
                    }
                }
            }
        )
        for module in modules:
            prisma.module.update(
                where={
                    "id": module.id
                },
                data={
                    "lecturer": {
                        "disconnect": True
                    }
                }
            )
        prisma.lecturer.delete_many(
            where={
                "userProfile": {
                    "is": {
                        "email": data["email"]
                    }
                }
            }
        )
        prisma.userprofile.delete_many(
            where={
                "email": data["email"]
            }
        )
        lecturer = prisma.lecturer.create(
            data={
                "userProfile": {
                    "create": {
                        "fullName": data["fullName"],
                        "email": data["email"],
                        "password": data["password"],
                        "contactNo": data["contactNo"],
                    }
                },
                "school": {
                    "connect": {
                        "id": school.id
                    }
                },
                "tenure": data["tenure"],
            }
        )
        for modules in data["currentCourses"]:
            module = prisma.module.find_first(
                where={
                    "moduleTitle": modules
                }
            )
            newmodule = prisma.module.update(
                where={
                    "id": module.id
                },
                data={
                    "lecturer": {
                        "connect": {
                            "id": lecturer.id
                        }
                    }
                },
                include={
                    "lecturer": {
                        "include": {
                            "userProfile": True
                        }
                    },
                    "moduleEnrollments": {
                        "include": {
                            "student": {
                                "include": {
                                    "userProfile": {
                                        "include": {
                                            "student": True
                                        }
                                    }
                                }
                            },
                        }
                    },
                }
            )
        print(f"Lecturer:\n{lecturer.json(indent=2)}\n")
        print(f"Modules:\n{newmodule.json(indent=2)}\n")
    # except Exception as e:
    #     print(e)
    prisma.disconnect()


def checkModuleEnrollMents():
    prisma.connect()
    moduleEnrollments = prisma.moduleenrollment.find_many(
        where={
            "student": {
                "is": {
                    "userProfile": {
                        "is": {
                            "email": "p21013568@student.newinti.edu.my"
                        }
                    }
                }
            },

        },
        include={
            "student": {
                "include": {
                    "userProfile": True
                }
            },
            "module": {
                "include": {
                    "lecturer": {
                        "include": {
                            "userProfile": True
                        }
                    },
                }
            }
        }
    )
    # print(len(moduleEnrollments))
    for i in range(len(moduleEnrollments)):
        mod = moduleEnrollments[i]
        module = mod.module
        # WHAT WE NEED TO KNOW TO RENDER THE ELEMENTS
        # 1.
        print("Module Code:", module.moduleCode)
        print("Module Title:", module.moduleTitle)
        print("Module Description:", module.moduleDesc)
        # print(mod.module.moduleTitle)
        # print(mod.student.userProfile.fullName)
        # try:
        #     print(module.lecturer.userProfile.json(indent=2))
        # except AttributeError:
        #     print("No lecturer")
        # print(mod.json(indent=2))
        # print(moduleEnrollments[i].json(indent=2))
        # print(moduleEnrollments[i].module.moduleTitle)
        # print(moduleEnrollments[i].student.userProfile.fullName)
    # for m in moduleEnrollments:
    #     print(m.module.moduleTitle)
    #     try:
    #         print(m.module.lecturer.userProfile.fullName)
    #     except AttributeError:
    #         print("No lecturer")
    #     try:
    #         print(m.student.userProfile.fullName)
    #     except AttributeError:
    #         print("No student")
        # print(m.json(indent=2))


def createAppointment():
    prisma.connect()
    prisma.appointment.delete_many()
    lecturer = prisma.lecturer.find_first(
        where={
            "userProfile": {
                "is": {
                    "email": "vaithegy.doraisamy@newinti.edu.my"
                }
            }
        }
    )
    student = prisma.student.find_first(
        where={
            "userProfile": {
                "is": {
                    "email": "p21013568@student.newinti.edu.my"
                }
            }
        }
    )
    appointment = prisma.appointment.create(
        data={
            "lecturerId": lecturer.id,
            "studentId": student.id,
            "location": "Zoom",
            # human readable to datetime today it's 18/05/2023
            # a meeting from 18/05/2023 10:00AM to 18/05/2023 11:00AM
            "startTime": datetime.utcnow(),
            "endTime": datetime.utcnow() + timedelta(hours=1),
        },
        include={
            "lecturer": {
                "include": {
                    "userProfile": True
                }
            },
            "student": {
                "include": {
                    "userProfile": True
                }
            }
        }
    )
    utctime = datetime.utcnow()
    # appointment2 = prisma.appointment.create(
    #     data={
    #         "lecturerId": prisma.lecturer.find_first(
    #             where={
    #                 "userProfile": {
    #                     "is": {
    #                         "email": "weijian.teng@newinti.edu.my"
    #                     }
    #                 }
    #             }
    #         ).id,
    #         "studentId": prisma.student.find_first(
    #             where={
    #                 "userProfile": {
    #                     "is": {
    #                         "email": "p21013568@student.newinti.edu.my"
    #                     }
    #                 }
    #             }
    #         ).id,
    #         "startTime": datetime.utcnow(),
    #         "endTime": datetime.utcnow() + timedelta(hours=1),
    #         "date": datetime.now(),
    #         "location": "Teams"
    #     },
    #     include={
    #         "lecturer": {
    #             "include": {
    #                 "userProfile": True
    #             }
    #         },
    #         "student": {
    #             "include": {
    #                 "userProfile": True
    #             }
    #         }
    #     }
    # )
    print(f"Appointment:\n{appointment.json(indent=2)}\n")
    # print(f"Appointment:\n{appointment2.json(indent=2)}\n")
    # print(appointment.startTime, appointment.endTime, appointment.date)
    # 2023-05-18 10:00:00+00:00 2023-05-18 11:00:00+00:00 2023-05-18 00:00:00+00:00
    # converting to days, month, year
    # print(appointment.startTime.day, appointment.startTime.month, appointment.startTime.year)
    # converting to Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    # print(appointment.startTime.strftime(r"%A %d %B %Y %H:%M:%S %z"))
    # print(appointment.endTime.strftime("%A %d %B %Y %H:%M:%S %z"))
    # print(appointment.json(indent=2))


def createModulePost():
    prisma.connect()
    user = prisma.userprofile.find_first(
        where={
            "email": "p21013568@student.newinti.edu.my"
        }
    )
    module = prisma.module.find_first(
        where={
            "moduleCode": "INT4004CEM"
        }
    )
    prisma.modulepost.delete_many()
    # print(f"User:\n{user.json(indent=2)}\n")
    # print(f"Module:\n{module.json(indent=2)}\n")
    modulepost = prisma.modulepost.create(
        data={
            "authorId": user.id,
            "moduleId": module.id,
            "title": "Computer Architecture and Network Question...",
            "content": "What does a parallel binary adder do?",
        },
        # include={
        #     "author": {
        #         "include": {
        #             "student": {
        #                 "include": {
        #                     "userProfile": True
        #                 }
        #             }
        #         }
        #     }
        # }
    )
    print(f"Module Post:\n{modulepost.json(indent=2)}\n")
    modulepost2 = prisma.modulepost.create(
        data={
            "authorId": user.id,
            "moduleId": module.id,
            "title": "On Homework for Yesterday...",
            "content": "Does anybody know the answer to question 3?",
        },
    )
    print(f"Module Post:\n{modulepost2.json(indent=2)}\n")
    modulepost3 = prisma.modulepost.create(
        data={
            "authorId": user.id,
            "moduleId": module.id,
            "title": "Quiz Answers, I need help...",
            "content": "Can anybody explain to me how to do question 2?",
        }
    )
    print(f"Module Post:\n{modulepost3.json(indent=2)}\n")


def queryPosts():
    prisma.connect()
    # module = prisma.module.find_first(
    #     where={
    #         "moduleCode": "INT4004CEM"
    #     }
    # )
    # posts = prisma.modulepost.find_many(
    #     where={
    #         "moduleId": module.id
    #     },
    #     include={
    #         "author": {
    #             "include": {
    #                 "student": {
    #                     "include": {
    #                         "userProfile": True
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # )
    # for post in posts:
    #     print(post.createdAt.tzinfo.utcoffset(post.createdAt))
    #     # print(f"Post:\n{post.json(indent=2)}\n")
    #     # print(f"Author:\n{post.author.json(indent=2)}\n")
    #     # print(f"Student:\n{post.author.student.json(indent=2)}\n")
    #     # print(f"User Profile:\n{post.author.json(indent=2)}\n")
    # userprofile = prisma.userprofile.update(
    #     where={
    #         "email": "p21013568@student.newinti.edu.my"
    #     },
    #     data={
    #         "favoritePosts": {
    #             "disconnect": {
    #                 "id": 61
    #             }
    #         }
    #     },
    #     include={
    #         "favoritePosts": True
    #     }
    # )
    # for post in userprofile.favoritePosts:
    #     print(f"Post:\n{post.json(indent=2)}\n")
    # userprofile = prisma.userprofile.update(
    #     where={
    #         "email": "p21013568@student.newinti.edu.my"
    #     },
    #     data={
    #         "favoritePosts": {
    #             "connect": {
    #                 "id": 61
    #             }
    #         }
    #     },
    #     include={
    #         "favoritePosts": True
    #     }
    # )
    # for post in userprofile.favoritePosts:
    #     print(f"Post:\n{post.json(indent=2)}\n")
    utc = timezone("UTC")
    kualalumpur = timezone("Asia/Kuala_Lumpur")
    time = kualalumpur.convert(datetime.now())
    newtime = utc.convert(time)
    # print(time)
    # print(newtime)
    # post = prisma.modulepost.update(
    #     where={
    #         "id": 61
    #     },
    #     data={
    #         "editedAt": newtime
    #     }
    # )
    # linking this post to a userprofile's favorite posts
    # print(f"Post:\n{post.json(indent=2)}\n")
    userprofile = prisma.userprofile.update(
        where={
            "id": "clhrvvvmm0001vts06psqzlye"
        },
        data={
            "favoritePosts": {
                "connect": {
                    "id": 61
                }
            }
        },
        include={
            "favoritePosts": True
        }
    )
    for post in userprofile.favoritePosts:
        print(kualalumpur.convert(post.updatedAt))
        print(kualalumpur.convert(post.editedAt))
        # print(f"Post:\n{post.json(indent=2)}\n")


def queryModules():
    prisma.connect()
    test = prisma.module.update(
        where={
            "moduleCode": "INT4007CEM/INT4009CEM"
        },
        data={
            "lecturer": {
                "disconnect": True
            }
        },
        include={
            "lecturer": True
        }
    )
    print(f"Module:\n{test.json(indent=2)}\n")
    # print(prisma.reply.count(
    #     where={
    #         "author": {
    #             "is": {
    #                 "fullName": "Matthew Loh Yet Marn"
    #             }
    #         }
    #     }
    # ))

    # lecturer = prisma.lecturer.find_first(
    #     where={
    #         "userProfile": {
    #             "is": {
    #                 "email": "vaithegy.doraisamy@newinti.edu.my"
    #             }
    #         }
    #     },
    #     include={
    #         "userProfile": True,
    #         "appointments": {
    #             "include": {
    #                 "student": {
    #                     "include": {
    #                         "userProfile": True
    #                     }
    #                 }
    #             }
    #         },
    #         "modules": {
    #             "include": {
    #                 "moduleEnrollments": {
    #                     "include": {
    #                         "student": {
    #                             "include": {
    #                                 "userProfile": True
    #                             }
    #                         }
    #                     }
    #                 },
    #                 "modulePosts": True
    #                 # {
    #                 #     # "include": {
    #                 #     #     "replies": {
    #                 #     #         "include": {
    #                 #     #             "author": True
    #                 #     #         }
    #                 #     #     }
    #                 #     # }
    #                 # }
    #             }
    #         }
    #     }
    # )
    # print(f"Module Posts:\n{module.modulePosts.json(indent=2)}\n")
    # for post in module.modulePosts:
    #     print(f"Post:\n{post.json(indent=2)}\n")
    #     print(f"Replies:\n{post.replies.json(indent=2)}\n")
    #     for reply in post.replies:
    #         print(f"Reply:\n{reply.json(indent=2)}\n")
    # print(f"Lecturer:\n{lecturer.json(indent=2)}\n")


def uploadFiles():
    prisma.connect()
    module = prisma.module.find_first(
        where={
            "moduleCode": "INT4004CEM"
        }
    )
    uploader = prisma.lecturer.find_first(
        where={
            "userProfile": {
                "is": {
                    "email": "vaithegy.doraisamy@newinti.edu.my"
                }
            }
        },
        include={
            "userProfile": True
        }
    )
    # prisma.moduleupload.delete_many()
    # data={
    #         "module": {
    #             "connect": {
    #                 "id": module.id
    #             }
    #         },
    #         "uploader": {
    #             "connect": {
    #                 "id": uploader.id
    #             }
    #         },
    #         "title": "Example of a video",
    #         "description": "Example of a video",
    #         "url": "https://streamin.one/v/89c58b96",
    #         "uploadType": "VIDEO"
    #     }
    # uploadedfile = prisma.moduleupload.create(
    #     data={
    #         "module": {
    #             "connect": {
    #                 "id": module.id
    #             }
    #         },
    #         "uploader": {
    #             "connect": {
    #                 "id": uploader.id
    #             }
    #         },
    #         "title": "Uploaded Video",
    #         "description": "Video Upload",
    #         "url": "https://streamin.one/v/89c58b96",
    #         "uploadType": "VIDEO"
    #     },
    #     include={
    #         "uploader": True,
    #         "module": True
    #     }
    # )
    uploadedfile = prisma.moduleupload.create()
    # uploadedfile = prisma.moduleupload.find_many()
    # for u in uploadedfile:
    #     print(f"Uploaded File:\n{u.json(indent=2)}\n")


def makeStructures():
    prisma.connect()
    # emulate selecting an institution and returning a list of that institution's programmes
    ins = "IICP"


def checkLecturerHours():
    prisma.connect()
    lecturer = prisma.lecturer.find_first(
        where={
            "userProfile": {
                "is": {
                    "fullName": "Shyamala Nadarajan"
                }
            }
        },
        include={
            "apptSettings": True,
            "userProfile": True
        }
    )
    # Time only string
    # 10:00PM
    timestrfmt = "%I:%M%p"
    # print(f"Lecturer:\n{lecturer.json(indent=2)}\n")
    kualalumpur = timezone("Asia/Kuala_Lumpur")
    for stg in lecturer.apptSettings:
        starttime = kualalumpur.convert(stg.startTime)
        endtime = kualalumpur.convert(stg.endTime)
        print(f"Lecturer Name: {lecturer.userProfile.fullName}")
        print(f"Day: {stg.day}")
        print(f"Start Time: {starttime.strftime(timestrfmt)}")
        print(f"End Time: {endtime.strftime(timestrfmt)}")
        print(f"Location: {stg.location}")


def createJson():
    prisma.connect()
    """
    Example of a quiz json
    
    quizData = {
        "quizAnswer": "This is the answer",
        "quizQuestion": "This is the question",
        "quizOptions": [
            "Invalid Answer 1",
            "Invalid Answer 2",
            "Invalid Answer 3",
        ],
        "quizType": "MULTIPLE_CHOICE"    
    }
    """
    quizType = "MULTIPLE_CHOICE"
    quizData = {
        "numOfQuestions": 10,
        "questions": [
            {
                "question": "What is the binary representation of the decimal number 10?",
                "options": [
                    "1010",
                    "1100",
                    "1110",
                    "1001"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the hexadecimal representation of the binary number 101011?",
                "options": [
                    "2B",
                    "5A",
                    "AB",
                    "BA"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the octal representation of the decimal number 25?",
                "options": [
                    "31",
                    "32",
                    "33",
                    "34"
                ],
                "correctAnswer": 2
            },
            {
                "question": "What is the decimal equivalent of the binary number 1101?",
                "options": [
                    "11",
                    "12",
                    "13",
                    "14"
                ],
                "correctAnswer": 2
            },
            {
                "question": "What is the binary representation of the hexadecimal number 2F?",
                "options": [
                    "101011",
                    "110011",
                    "111011",
                    "100011"
                ],
                "correctAnswer": 1
            },
            {
                "question": "What is the hexadecimal representation of the decimal number 255?",
                "options": [
                    "FF",
                    "EE",
                    "DD",
                    "CC"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the octal representation of the binary number 101010?",
                "options": [
                    "52",
                    "54",
                    "56",
                    "60"
                ],
                "correctAnswer": 1
            },
            {
                "question": "What is the decimal equivalent of the octal number 77?",
                "options": [
                    "63",
                    "64",
                    "65",
                    "66"
                ],
                "correctAnswer": 3
            },
            {
                "question": "What is the binary representation of the decimal number 7?",
                "options": [
                    "0111",
                    "1000",
                    "1001",
                    "1010"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the hexadecimal representation of the binary number 11110000?",
                "options": [
                    "F0",
                    "E0",
                    "D0",
                    "C0"
                ],
                "correctAnswer": 0
            }
        ]
    }
    convertedData = Json(quizData)
    # converting dictionary to json using Prisma's Json Class
    submitQuiz = prisma.modulehubcontent.create(
        data={
            "title": "Quiz Title 1",
            "description": "Quiz Description",
            "contentType": "MULTIPLE_CHOICE",
            "contentInfo": convertedData,
            "author": {
                "connect": {
                    "id": "cli0faxgj0000vtdc5vq2y9pz"
                }
            },
            "module": {
                "connect": {
                    "id": "clhrvr700000cvt9gwh6d7fk6"
                }
            }
        }
    )
    print(f"Quiz:\n{submitQuiz.json(indent=2)}\n")
    # Fill in the Blanks Style Quiz
    # fillBlanks = {
    #     "numOfQuestions": 3,
    #     "questions": [
    #         {
    #             "question": "The _______ is the part of the computer that executes the instructions of a computer program.",
    #             "acceptedAnswers": [
    #                 "CPU", "Central Processing Unit"
    #             ]
    #         },
    #         {
    #             "question": "The _______ is the part of the computer that stores data and instructions.",
    #             "acceptedAnswers": [
    #                 "Memory", "RAM", "Random Access Memory"
    #             ]
    #         }
    #     ]
    # }
    module = prisma.module.find_first(
        where={
            "moduleCode": "INT4004CEM"
        },
        include={
            "moduleHubContent": {
                "include": {
                    "author": {
                        "include": {
                            "userProfile": True
                        }
                    }
                }
            }
        }
    )
    # print(f"Module Hub Content:\n{module.moduleHubContent}\n")
    for c in module.moduleHubContent:
        # print(c.json(indent=2))
        print(c.contentType)
        # print(type(c.contentInfo["questions"]))
        formatted = json.dumps(c.contentInfo["questions"], indent=2)
        print(formatted)
        for q in c.contentInfo["questions"]:
            print(q["question"])
            print(q["options"])
            print(q["correctAnswer"])
            print("\n")


def findManyAppointments():
    prisma.connect()
    appointments = prisma.appointment.find_many(
        where={
            "student": {
                "is": {
                    "userProfile": {
                        "is": {
                            "email": "p21013568@student.newinti.edu.my"
                        }
                    }
                }
            }
        }
    )
    for i in appointments:
        print(i.json(indent=2))
    # print(f"Appointments:\n{appointments.json(indent=2)}\n")


def testUploadBlob():
    prisma.connect()
    # byteIMGIO = io.BytesIO()
    # byteIMG = Image.open(r"Assets\signinguplabel.png")
    # byteIMG.save(byteIMGIO, format="PNG")
    # byteIMGIO.seek(0)
    # byteIMG = byteIMGIO.read()
    # b64 = Base64.encode(byteIMG)
    # decoded = Base64.decode(b64)
    # dataBytesIO = io.BytesIO(decoded)
    # print(dataBytesIO)
    # im = Image.open(dataBytesIO)
    # im.show()
    # image = r"Assets\signinguplabel.png"
    # with open(image, "rb") as f:
    #     # fit the image using PIL and ImageOps
    #     image = Image.open(f)
    #     image = ImageOps.fit(image, (500, 500), Image.ANTIALIAS)
    #     # convert the image to bytes
    #     image = image.convert("RGB")
    #     image = image.tobytes()
    #     # encode the image using base64
    #     image = f.read()
    # print(type(image))
    # finalBytes = image.tobytes()
    # print(type(finalBytes))
    # author = prisma.userprofile.find_first(
    #     where={
    #         "id": "clhrvvvmm0001vts06psqzlye"
    #     }
    # )
    # t = prisma.helpdeskticket.create(
    #     data={
    #         "author": {
    #             "connect": {
    #                 "id": author.id
    #             }
    #         },
    #         "title": "Test Ticket",
    #         "image": Base64.encode(image)
    #     }
    # )
    # print(t.json(indent=2))
    t = prisma.helpdeskticket.find_first(
        where={
            "id": 4
        }
    )
    print(t.image)
    bytes = Base64.decode(t.image)  # -> a bytes object
    # print(bytes)
    img_io = io.BytesIO(bytes)
    img = Image.open(img_io)
    img.show()
    # # Opening the bytes object as an image in PIL
    # imgdata = base64.b64decode(bytes)
    # image = Image.open(io.BytesIO(imgdata))
    # image.show()
    # print(type(bytes))
    # b64 = base64.b64decode(bytes)
    # print(b64)
    # im = io.BytesIO(base64.b64decode(bytes))
    # print(type(im))


def createGame():
    """ 
    quizData = {
        "numOfQuestions": 10,
        "questions": [
            {
                "question": "What is the binary representation of the decimal number 10?",
                "options": [
                    "1010",
                    "1100",
                    "1110",
                    "1001"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the hexadecimal representation of the binary number 101011?",
                "options": [
                    "2B",
                    "5A",
                    "AB",
                    "BA"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the octal representation of the decimal number 25?",
                "options": [
                    "31",
                    "32",
                    "33",
                    "34"
                ],
                "correctAnswer": 2
            },
            {
                "question": "What is the decimal equivalent of the binary number 1101?",
                "options": [
                    "11",
                    "12",
                    "13",
                    "14"
                ],
                "correctAnswer": 2
            },
            {
                "question": "What is the binary representation of the hexadecimal number 2F?",
                "options": [
                    "101011",
                    "110011",
                    "111011",
                    "100011"
                ],
                "correctAnswer": 1
            },
            {
                "question": "What is the hexadecimal representation of the decimal number 255?",
                "options": [
                    "FF",
                    "EE",
                    "DD",
                    "CC"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the octal representation of the binary number 101010?",
                "options": [
                    "52",
                    "54",
                    "56",
                    "60"
                ],
                "correctAnswer": 1
            },
            {
                "question": "What is the decimal equivalent of the octal number 77?",
                "options": [
                    "63",
                    "64",
                    "65",
                    "66"
                ],
                "correctAnswer": 3
            },
            {
                "question": "What is the binary representation of the decimal number 7?",
                "options": [
                    "0111",
                    "1000",
                    "1001",
                    "1010"
                ],
                "correctAnswer": 0
            },
            {
                "question": "What is the hexadecimal representation of the binary number 11110000?",
                "options": [
                    "F0",
                    "E0",
                    "D0",
                    "C0"
                ],
                "correctAnswer": 0
            }
        ]
    }
    """
    prisma.connect()
    # A wordle json structure of 5 letter words related to Computer Architecture and Networks
    wordleJson = {
        "numOfQuestions": 5,
        "questions": [
            {
                "question": "cache",
            },
            {
                "question": "stack",
            },
            {
                "question": "fetch",
            },
            {
                "question": "write",
            },
            {
                "question": "bytes",
            },
        ]
    }
    submittedJson = Json(wordleJson)
    module = prisma.module.find_first(
        where={
            "moduleCode": "INT4004CEM"
        },
        include={
            "lecturer": {
                "include": {
                    "userProfile": True
                }
            }
        }
    )
    wordle = prisma.modulehubcontent.create(
        data={
            "module": {
                "connect": {
                    "id": module.id
                }
            },
            "author": {
                "connect": {
                    "id": module.lecturer.id
                }
            },
            "contentType": "GAME",
            "contentInfo": submittedJson,
            "title": "Wordle!",
            "description": "A wordle game for Computer Architecture and Networks",
        }
    )
    print(wordle.json(indent=2))


if __name__ == "__main__":
    # ~~~~ MYSQL ~~~~
    # ~~~~ PRISMA ~~~~
    # prismaCreateInstitution()
    # prismaCreateProgramme()
    # prismaCreateLecturer()
    # prismaCreateStudent()
    # prismaqueryAll()
    # prisQueryModuleEnrollment()
    # prisQueryUserProfile()
    # prisCreateMultipleModules()
    # usingpartialTypes()
    # creatingmoduleenrollments()
    # checkModuleEnrollMents()
    # createAppointment()
    # createModulePost()
    # queryPosts()
    # queryModules()
    # uploadFiles()
    # makeStructures()
    # checkLecturerHours()
    # createJson()
    # findManyAppointments()
    # testUploadBlob()
    createGame()
