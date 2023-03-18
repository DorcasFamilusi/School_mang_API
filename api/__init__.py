from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from werkzeug.exceptions import NotFound, MethodNotAllowed
from api.auth.views import auth_namespace
from .Students.views import students_ns
from .config.config import config_dict
from .models.admin import Admin
from .models.course import Course
from .models.lecturer import Lecturer
from .models.score import Score
from .models.student import Student
from .models.studentCourse import StudentCourse
from .models.user import User
from .portal.views.courses import courses_namespace
from .utils import db


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; ** token to authorize"
        }
    }

    api = Api(app,
        title='Student REST API',
        description='A student management API',
        authorizations=authorizations,
        security='Bearer Auth'

    )

    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(students_ns, path='/student')
    api.add_namespace(courses_namespace, path='/courses')

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 404

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Lecturer': Lecturer,
            'Score': Score,
            'Admin': Admin,
            'Student': Student,
            'StudentCourse': StudentCourse,
            'Course': Course,
        }

    return app

