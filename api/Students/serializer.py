from flask_restx import fields

add_students_score_fields_serializer = {
    'student_id': fields.Integer(required=False),
    'course_id': fields.Integer(required=True),
    'score': fields.Integer(required=True)
}

courses_fields_serializer = {
    'course_id': fields.String(required=True),
}

students_fields_serializer = {
    'id': fields.String(),
    'identifier': fields.String(required=False),
    'email': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'admission_no': fields.String(required=True)
}
