from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource

from .serializer import students_fields_serializer, courses_fields_serializer, add_students_score_fields_serializer
from ..models.admin import Admin
from ..models.course import Course
from ..models.score import Score
from ..models.student import Student
from ..models.studentCourse import StudentCourse
from ..models.user import User
from ..portal.serializerCourses import course_retrieve_fields_serializer
from ..utils import db, convert_grade_to_gpa, get_grade

students_ns = Namespace('student', description='Namespace for students ')

add_courses_serializer = students_ns.model('Courses add serializer', model=courses_fields_serializer)
add_students_score_serializer = students_ns.model('Courses add serializer', model=add_students_score_fields_serializer)
students_serializer = students_ns.model('Students list serializer', model=students_fields_serializer)
courses_serializer = students_ns.model('Students courses list serializer', model=course_retrieve_fields_serializer)


# Route to login or authenticate the user
@students_ns.route('')
class StudentsListView(Resource):

    @students_ns.marshal_with(students_serializer)
    @students_ns.doc(
        description="""
            This endpoint can only be accessed by an admin. 
            This allows the admin to retrieve all students in school
            """
    )
    @jwt_required()
    def get(self):
        """
        Retrieve all the students 
        """
        # populate_db()- population
        authentication_user_id = get_jwt_identity()  # authentication
        admin = Admin.query.filter_by(id=authentication_user_id).first()
        if not admin:
            return {'message': 'You are not an authorized personnel'}, HTTPStatus.UNAUTHORIZED
        students = Student.query.all()
        return students, HTTPStatus.OK


@students_ns.route('/<int:student_id>')
class StudentReadUpdateDeleteView(Resource):

    @students_ns.marshal_with(students_serializer)
    @students_ns.doc(
        description=""" 
            This allows the retrieval of students which is only accessible 
            by an admin or a 
            """
    )
    @jwt_required()
    def get(self, student_id):
        """
        Retrieve a Student 
        """
        authentication_user_id = get_jwt_identity()
        user = User.query.filter_by(id=authentication_user_id).first()
        if not user or user.user_type == 'student':
            return {'message': 'You are not authorized '}, HTTPStatus.UNAUTHORIZED
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return {'message': 'This student does not exist'}, HTTPStatus.NOT_FOUND
        return student, HTTPStatus.OK


@students_ns.route('/<int:student_id>/courses')
class StudentListOfCoursesView(Resource):

    @students_ns.marshal_with(courses_serializer)
    def get(self, student_id):
        """
        Retrieve a student courses
        """
        courses = StudentCourse.get_student_courses(student_id)
        return courses, HTTPStatus.OK


@students_ns.route('/course/reg_and_drop')
class StudentCourseRegisterView(Resource):

    @students_ns.marshal_with(courses_serializer)
    @students_ns.expect(add_courses_serializer)
    @students_ns.doc(
        description="""
            This allows students to register for a course and it is only 
            accessible to students of the school
            """
    )
    @jwt_required()
    def post(self):
        """ 
        Register for a course 
        """
        authentication_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=authentication_user_id).first()
        if not student:
            return {'message': 'You are not authorized'}, HTTPStatus.UNAUTHORIZED
        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()
        if course:
            # this is to check if the student has registered for this course
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                return {
                           'message': 'Student has registered for this course'
                       }, HTTPStatus.OK
            # Register the student for a course
            add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
            try:
                add_student_to_course.save()
                return {'message': 'Course has been registered successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {
                           'message': 'An error occurred while you were registering for this  course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Course does not exist'}, HTTPStatus.NOT_FOUND

    @students_ns.expect(add_courses_serializer)
    @students_ns.doc(
        description="""
            This allows a student to drop a course
            """
    )
    @jwt_required()
    def delete(self):
        """
        Unregister or drop a course
        """
        data = request.get_json()
        authentication_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=authentication_user_id).first()
        if not student:
            return {'message': 'You are not authorized '}, HTTPStatus.UNAUTHORIZED

        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()
        if course:
            # check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                try:
                    get_student_in_course.delete()
                    return {'message': 'Course deleted successfully'}, HTTPStatus.NO_CONTENT
                except:
                    db.session.rollback()
                    return {'message': 'An error occurred while deleting this course'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {
                       'message': 'You have not register for this course'
                   }, HTTPStatus.BAD_REQUEST

        return {'message': 'Course does not exist'}, HTTPStatus.NOT_FOUND


@students_ns.route('/course/add_score')
class StudentAddCoursesScoreView(Resource):

    @students_ns.expect(add_students_score_serializer)
    @students_ns.doc(
        description='''
            This end point is accessible to only the course lecturer,
            which allows them add the students scores in their course
            '''
    )
    @jwt_required()
    def put(self):
        """
        Add a students score
        """
        authenticated_user_id = get_jwt_identity()
        student_id = request.json['student_id']
        course_id = request.json['course_id']
        score_value = request.json['score']
        user = User.query.filter_by(id=authenticated_user_id).first()
        if not user or user.user_type != 'lecturer':
            return {'message': 'You are not the authorized lecturer'}, HTTPStatus.UNAUTHORIZED
        # we need to check if the student and the course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(id=course_id).first()
        if not student or not course:
            return {'message': 'Student or course was not found'}, HTTPStatus.NOT_FOUND
        #  we need to check if this is the course lecturer
        if course.lecturer_id != user.id:
            return {'message': 'You cannot add score for this student in this course'}, HTTPStatus.UNAUTHORIZED
        # check if student is registered for the course
        student_in_course = StudentCourse.query.filter_by(course_id=course.id, student_id=student.id).first()
        if student_in_course:
            # This is to check if the student already have a score in the course
            score = Score.query.filter_by(student_id=student_id, course_id=course_id).first()
            grade = get_grade(score_value)
            if score:
                score.score = score_value
                score.grade = grade
            else:
                # create a new score then save to database
                score = Score(student_id=student_id, course_id=course_id, score=score_value, grade=grade)
            try:
                score.save()
                return {'message': 'Score added successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {
                           'message': 'An error occurred while saving the student course score'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'This student is not registered for this course'}, HTTPStatus.BAD_REQUEST


@students_ns.route('/<int:student_id>/gpa')
class StudentGPAView(Resource):

    def get(self, student_id):
        """
        Calculate the student gpa 
        """
        student = Student.get_by_id(student_id)
        # get all the courses the students offer
        courses = StudentCourse.get_student_courses(student.id)
        total_weighted_gpa = 0
        total_course_hours = 0
        for course in courses:
            # check if student have a score already
            score_exist = Score.query.filter_by(student_id=student.id, course_id=course.id).first()
            if score_exist:
                grade = score_exist.grade
                # calculate the gpa 
                gpa = convert_grade_to_gpa(grade)
                weighted_gpa = gpa * course.course_hours
                total_weighted_gpa += weighted_gpa
                total_course_hours += course.course_hours
        if total_course_hours == 0:
            return {
                       'message': 'GPA calculation completed.',
                       'gpa': total_course_hours
                   }, HTTPStatus.OK
        else:
            gpa = total_weighted_gpa / total_course_hours
            return {
                       'message': 'GPA calculation is done',
                       'gpa': round(gpa, 2)
                   }, HTTPStatus.OK
