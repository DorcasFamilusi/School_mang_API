import asyncio
import datetime
from http import HTTPStatus

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from ..dec import admin_required
from ..models.admin import Admin
from ..models.lecturer import Lecturer
from ..models.student import Student
from ..models.user import User
from ..utils import db, random_char, generate_reset_token, EmailService

auth_namespace = Namespace('auth', description='name space for authentication')

password_reset_request = auth_namespace.model(
    'Password_reset_request', {
        'email': fields.String(required=True, description='User email address')
    }
)

password_reset_fields = auth_namespace.model(
    'Password_reset', {
        'token': fields.String(required=True, description="Password reset token"),
        'password1': fields.String(required=True, description="Password"),
        'password2': fields.String(required=True, description="Confirm password")
    }
)

signup_model = auth_namespace.model(
    'SignUp', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description='A password')
    }
)

login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description='A password')
    }
)


@auth_namespace.route('/signup')
class StudentRegistrationView(Resource):

    @auth_namespace.expect(signup_model)
    @auth_namespace.doc(
        description='''
This is used to create an account based on the user type
        '''
    )
    def post(self):
        """
            Sign up a user
        """
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'User already exists'}, HTTPStatus.CONFLICT
        # Create new user
        identifier=random_char(10)  
        current_year =  str(datetime.datetime.now().year)
        admission= 'STD@' + random_char(6) + current_year
        new_user =  Student(
            email=data.get('email'), 
            identifier=identifier,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            user_type = 'student',
            password_hash = generate_password_hash(data.get('password')),
            admission_no=admission
            )
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED


auth_namespace.route('/register/lecturer')
class LecturerCreationView(Resource):
    @auth_namespace.expect(signup_model)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to an admin. 
            It allows admin create a lecturer
            """
    )
    @admin_required()
    def post(self):
        """ Create a new lecturer account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message' : 'Email already exists'} , HTTPStatus.CONFLICT
        # Create new user
        identifier=random_char(10)  
        current_year =  str(datetime.datetime.now().year)
        employee= 'LEC@' + random_char(6) + current_year
        new_user = Lecturer(
            email=data.get('email'), identifier=identifier,
            first_name=data.get('first_name'), last_name=data.get('last_name'),
            user_type = 'lecturer', password_hash = generate_password_hash(data.get('password')),
            employee_no=employee
            )
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED
            
            
          

# Route to refresh Token
@auth_namespace.route('/refresh')
class Refresh(Resource):
    @auth_namespace.doc(
        description="""
            This allows user refresh their tokens
            """
    )
    @jwt_required(refresh=True)
    def post(self):
        """
            Generate Refresh Token
        """
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return {
                   'access_token': access_token,
                   'refresh_token': refresh_token,

               }, HTTPStatus.OK


# Route for user to login 
@auth_namespace.route('/login')
class UserLoginView(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(
        description="""
            This allows user authentication
            """
    )
    def post(self):
        """ User authentication"""
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            response = {'message': 'Invalid username or password'}
            return response, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        return response, HTTPStatus.OK


# Route for requesting to reset password
@auth_namespace.route('/reset_password_request')
class PasswordResetRequestView(Resource):
    @auth_namespace.expect(password_reset_request)
    @auth_namespace.doc(
        description=""" 
            This allows a user to request for a new password if they forget their old password
            """
    )
    async def post(self):
        """ To request for a password reset"""
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a random password reset token
            token = generate_reset_token(48)
            user.password_reset_token = token
            db.session.commit()
            # Send a password reset email
            mail = asyncio.create_task(EmailService.forget_password_mail(user.email, token))

        return {
                   'message': 'An email has been sent with instructions to reset your password.'
               }, HTTPStatus.OK


# Resetting password route
@auth_namespace.route('/reset_password/<token>')
class PasswordResetView(Resource):
    @auth_namespace.expect(password_reset_fields)
    @auth_namespace.doc(
        description="""
            This allows user reset new password
            """
    )
    def post(self):
        """ Reset password"""
        token = request.json.get('token')
        user = User.query.filter_by(password_reset_token=token).first()
        if not user:
            return {
                       'message': 'Invalid or expired token. Please do try again.'
                   }, HTTPStatus.BAD_REQUEST
        password1 = request.json.get('password1')
        password2 = request.json.get('password2')
        if password1 == password2:
            user.set_password(password2)
            user.password_reset_token = None
            db.session.commit()
            return {
                       'message': 'Your password has been reset.'
                   }, HTTPStatus.OK

        return {
                   'message': 'Password does not match.'
               }, HTTPStatus.UNAUTHORIZED
