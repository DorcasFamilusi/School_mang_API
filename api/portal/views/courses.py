from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from ..serializerCourses import course_retrieve_fields_serializer
from ...Students.serializer import students_fields_serializer
from ...models.admin import Admin
from ...models.course import Course
from ...models.lecturer import Lecturer
from ...models.student import Student
from ...models.studentCourse import StudentCourse
from ...models.user import User
from ...utils import db, random_char

courses_namespace = Namespace('courses', description='Namespace for courses')

course_reg = courses_namespace.model(
    'Course reg ', {
        'name': fields.String(required=True , description="Course name"),
        'course_hours': fields.Integer(description="Course credit hours"),
        'lecturer_id': fields.Integer(required=True, description="Course teacher id"),
    }
)

student_course_register_serializer = courses_namespace.model(
    'Student Course registration Serializer', {
        'student_id': fields.String(required=True),
    }
)

students_serializer = courses_namespace.model('Student Serializer', students_fields_serializer)

course_lecturer_serializer = courses_namespace.model(
    'Course Lecturer serializer', {
        'identifier': fields.String(),
        'email': fields.String(required=True),
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'employee_no': fields.String(required=True),
        'created_at': fields.DateTime(),
    }
)
course_retrieve_serializer = courses_namespace.model('Course Retrieval', course_retrieve_fields_serializer)


@courses_namespace.route('')
class CoursesListView(Resource):

    @courses_namespace.marshal_with(course_retrieve_serializer)
    @courses_namespace.doc(
        description="""
            This allows the retrieval of all the courses
            """
    )
    @jwt_required()
    def get(self):
        """
        Retrieve all courses
        """
        courses = Course.query.all()
        return courses, HTTPStatus.OK

    @courses_namespace.expect(course_reg)
    @courses_namespace.doc(
        description=""" 
            This allows an admin create a new course
            """
    )
    @jwt_required()
    def post(self):
        """
        Create a new course
        """
        authenticated_user_id = get_jwt_identity()
        admin = Admin.query.filter_by(id=authenticated_user_id).first()
        if not admin:
            return {'message': 'You are not an authorized personnel '}, HTTPStatus.UNAUTHORIZED
        data = request.get_json()
        lecturer = Lecturer.query.filter_by(id=data.get('lecturer_id')).first()
        if lecturer:
            code = random_char(12)
            course = Course(
                course_code=code,
                lecturer_id=lecturer.id,
                name=data.get('name'),
            )
            try:
                course.save()
                return {'message': 'Course is registered successfully'}, HTTPStatus.CREATED
            except:
                return {'message': 'An error occurred while trying to save course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Invalid lecturer id'}, HTTPStatus.BAD_REQUEST


@courses_namespace.route('/<int:course_id>')
class CourseRetrievalView(Resource):

    @courses_namespace.marshal_with(course_retrieve_serializer)
    def get(self, course_id):
        """
        Retrieve a course
        """
        course = Course.get_by_id(course_id)
        return course, HTTPStatus.OK

    @courses_namespace.doc(
        description="""
            This allows an admin delete a course
            """
    )
    @jwt_required()
    def delete(self, course_id):
        """
        Delete a course
        """
        authenticated_user_id = get_jwt_identity()
        admin = Admin.query.filter_by(id=authenticated_user_id).first()
        if not admin:
            return {'message': 'You are not an authorized personnel'}, HTTPStatus.UNAUTHORIZED
        course = Course.query.filter_by(course_id).first()
        if not course:
            return {'message': 'Course does not exist'}, HTTPStatus.NOT_FOUND
        try:
            course.delete()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return HTTPStatus.NO_CONTENT


@courses_namespace.route('/<int:course_id>/students/reg_and_drop')
class CourseRetrievalView(Resource):

    @courses_namespace.expect(student_course_register_serializer)
    @courses_namespace.doc(
        description="""
            This allows lecturer add a student to their course
            """
    )
    @jwt_required()
    def post(self, course_id):
        """
        Register a student to a course
        """
        authenticated_user_id = get_jwt_identity()
        lecturer = Lecturer.query.filter_by(id=authenticated_user_id).first()
        if not lecturer:
            return {'message': 'You are not authorized to the endpoint'}, HTTPStatus.UNAUTHORIZED
        data = request.get_json()
        student_id = data.get('student_id')
        # check if student and course does exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(course_id).first()
        if not student or not course:
            return {'message': 'Student or course may not found'}, HTTPStatus.NOT_FOUND
        if student:
            # check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                return {
                           'message': '{} has already registered for this course'.format(student.first_name)
                       }, HTTPStatus.OK
            # Register the student to the course
            add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
            try:
                add_student_to_course.save()
                return {'message': 'Course registered successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while registering course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Student does not exist'}, HTTPStatus.NOT_FOUND

    @courses_namespace.doc(
        description="""
            This allows lecturer remove a student from their course
            """
    )
    @jwt_required()
    def delete(self, course_id):
        """
        Unregister a student course
        """
        authenticated_user_id = get_jwt_identity()
        lecturer = Lecturer.query.filter_by(id=authenticated_user_id).first()
        if not lecturer:
            return {'message': 'You are not an authorized personnel'}, HTTPStatus.UNAUTHORIZED
        data = request.get_json()
        student_id = data.get('student_id')
        # check if student and the course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(course_id).first()
        if not student or not course:
            return {'message': 'Student or course was not found'}, HTTPStatus.NOT_FOUND
        if student:
            # check if student has already registered for the course
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                try:
                    get_student_in_course.delete()
                    return {'message': 'Course delete successfully'}, HTTPStatus.NO_CONTENT
                except:
                    db.session.rollback()
                    return {
                               'message': 'An error occurred while trying to delete the student course'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {
                       'message': '{} has not registered for this course'.format(student.first_name)
                   }, HTTPStatus.BAD_REQUEST


@courses_namespace.route('/<int:course_id>/students')
class CourseStudentsListView(Resource):

    @courses_namespace.marshal_with(students_serializer)
    @courses_namespace.doc(
        description="""
            This endpoint is accessible to an admin and a teacher. 
            It allows the retrieval of all students in a course
            """
    )
    @jwt_required()
    def get(self, course_id):
        """
        Retrieve all registered student in a course
        """
        authenticated_user_id = get_jwt_identity()
        user = User.query.filter_by(id=authenticated_user_id).first()
        if not user or user.user_type == 'student':
            return {
                       'message': 'You are not authorized to the endpoint'
                   }, HTTPStatus.UNAUTHORIZED

        course = Course.get_by_id(course_id)
        get_student_in_course = StudentCourse.get_students_in_course_by(course.id)
        return get_student_in_course, HTTPStatus.OK
