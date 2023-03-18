from flask_restx import fields

course_retrieve_fields_serializer = {
    'id': fields.Integer(),
    'name': fields.String(required=True, description="course title"),
    'course_code': fields.String(description="Course code"),
    'lecturer_id': fields.Integer(),
    'created_at': fields.DateTime(description="Date of course registration"),
}
