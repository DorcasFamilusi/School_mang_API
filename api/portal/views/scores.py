# from ...models.student import Student
from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from ..serializerCourses import course_retrieve_fields_serializer
from ...Students.serializer import students_fields_serializer
from ...models.course import Course
from ...models.lecturer import Lecturer
# from ...models.studentCourse import StudentCourse
# from ...models.user import User
# from ...models.admin import Admin
from ...utils import random_char

courses_namespace = Namespace('courses', description='Namespace for courses')

student_course_register_serializer = courses_namespace.model(
    'Student Course Creation Serializer', {
        'student_id': fields.String(required=True)
    }
)

students_serializer = courses_namespace.model('Student Serializer', students_fields_serializer)

course_creation_serializer = courses_namespace.model(
    'Course creation serializer', {
        'name': fields.String(required=True),
        'lecturer_id': fields.Integer(required=True)
    }
)

course_lecturer_serializer = courses_namespace.model(
    'Course Lecturer serializer', {
        'identifier': fields.String(),
        'email': fields.String(required=True),
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'employee_no': fields.String(required=True),
        'created_at': fields.DateTime()
    }
)
course_retrieve_serializer = courses_namespace.model('Course Retrieval serializer', course_retrieve_fields_serializer)

register_fields_serializer = {
    'email': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'user_type': fields.String(required=True),
    'password': fields.String(required=True)
}


@courses_namespace.route('')
class StudentsScoreAddView(Resource):

    @courses_namespace.marshal_with(course_retrieve_serializer)
    def get(self):
        courses = Course.query.all()
        return courses, HTTPStatus.OK

    @courses_namespace.expect(course_creation_serializer)
    def post(self):
        data = request.get_json()
        lecturer = Lecturer.query.filter_by(id=data.get('lecturer_id')).first()
        if lecturer:
            code = random_char(12)
            course = Course(
                course_code=code,
                lecturer_id=lecturer.id,
                name=data.get('name')
            )
            try:
                course.save()
                return {'message': 'Course was registered successfully'}, HTTPStatus.CREATED
            except:
                return {'message': 'An error occurred while trying to save course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Invalid lecturer id'}, HTTPStatus.BAD_REQUEST
