import os
import secrets
# import environ
import smtplib
import ssl
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def generate_reset_token(length):
    """ This is to generate a password reset token 
    """
    return secrets.token_hex(length)


def random_char(length):
    """ Generate a random string 
    param:
        length : length of string to be generated"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


sender_email = os.getenv('EMAIL_SENDER')
password = os.getenv('EMAIL_PASSWORD')


def get_grade(score):
    """
    if else statement to convert scores to grade
    """
    if score < 100 and score > 70:
        return 'A'
    elif score < 69 and score > 60:
        return 'B'
    elif score < 59 and score > 50:
        return 'C'
    elif score < 49 and score > 45:
        return 'D'
    elif score < 44 and score > 40:
        return 'E'
    elif score < 40:
        return 'F'
    else:
        return 'F'


def convert_grade_to_gpa(grade):
    """
    This is to convert grade to the point system
    """
    if grade == 'A':
        return 4.0
    elif grade == 'B':
        return 3.3
    elif grade == 'C':
        return 2.3
    elif grade == 'D':
        return 1.3
    else:
        return 0.0


class EmailService():
    def forget_password_mail(receiver_email, token):
        """
        This is to send a forget password mail instruction to user
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = "Reset your password"
        message["From"] = sender_email
        message["To"] = receiver_email
        reset_link = f'http://127.0.0.1:5000/password/{token}/reset'
        html = ('accounts/password-reset-mail.html', {'reset_link': reset_link})
        part = MIMEText(html, "html")
        # You can add HTML/plain-text parts to MIMEMultipart message
        message.attach(part)
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
