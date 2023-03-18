import datetime

from werkzeug.security import generate_password_hash

from .models.admin import Admin
from .models.course import Course
from .models.lecturer import Lecturer
from .models.student import Student
from .models.studentCourse import StudentCourse
from .utils import random_char


def populate_db():
    students = [
        {'first_name': 'Student', 'last_name': 'StudentA', 'email': 'student@gmail.com', 'password': 'password12345', },
        {'first_name': 'Student', 'last_name': 'StudentB', 'email': 'student1@gmail.com',
         'password': 'password123456', },
    ]
    admins = [
        {'first_name': 'Admin', 'last_name': 'AdminA', 'email': 'admin123@gmail.com', 'password': 'password1', },
        {'first_name': 'Admin', 'last_name': 'AdminB', 'email': 'admin124@gmail.com', 'password': 'password12', },
    ]
    courses = [
        {'course_code': 'CSC102', 'course_hours': 2, 'name': '  CSC'},
        {'course_code': 'GNE305', 'course_hours': 4, 'name': 'GNE'},
    ]
    lecturer = [
        {'first_name': 'Lecturer', 'last_name': 'lecturerC', 'email': 'lecturer56@gmail.com',
         'password': 'password123', },
        {'first_name': 'Lecturer', 'last_name': 'lecturerD', 'email': 'lecturer87@gmail.com',
         'password': 'password1234', },
    ]
    for user in admins:
        identifier = random_char(12)
        current_year = str(datetime.datetime.now().year)
        admin = Admin(email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                      password_hash=generate_password_hash(user['password']), user_type='admin',
                      designation='Principal', identifier=identifier
                      )
        try:
            admin.save()
        except:
            pass

    for user in lecturer:
        identifier = random_char(12)
        current_year = str(datetime.datetime.now().year)
        employee_no = 'lecturer@' + random_char(12) + current_year
        admin = Lecturer(email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                         password_hash=generate_password_hash(user['password']), user_type='lecturer',
                         employee_no=employee_no, identifier=identifier
                         )
        try:
            admin.save()
        except:
            pass

    for course in courses:
        lecturer = Lecturer.query.filter_by(email='lecturer1@gmail.com').first()
        data = Course(course_code=course['course_code'], course_hours=course['course_hours'],
                      name=course['name'], lecturer_id=lecturer.id
                      )
        try:
            data.save()
        except:
            pass

    for user in students:
        identifier = random_char(12)
        current_year = str(datetime.datetime.now().year)
        admission_no = 'student@' + random_char(12) + current_year
        student = Student(email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                          password_hash=generate_password_hash(user['password']), user_type='student',
                          admission_no=admission_no, identifier=identifier
                          )
        try:
            student.save()
            course = Course.query.filter_by(course_code='GNE305').first()
            student_course = StudentCourse(student_id=student.id, course_id=course.id)
            student_course.save()
        except:
            pass
