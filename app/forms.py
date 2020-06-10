from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, SelectField, HiddenField, validators
from wtforms.fields.html5 import DateField
import app.pylib.win_user
from app.pylib.auth_user import User

class RegisterForm(FlaskForm):
    department = SelectField(
        'Department',
        choices=app.pylib.win_user.ous,
        validators=[],
        render_kw={'placeholder': 'Department'}
        )
    role = StringField(
        'Role',
        validators=[validators.DataRequired(message='Please input your role.'), validators.Length(min=2)],
        render_kw={'placeholder': 'Role or posistion'}
    )
    first_name = StringField(
        'First Name',
        validators=[validators.Length(min=2, max=32), validators.DataRequired(message="Please enter your first name.")],
        render_kw={'placeholder': 'First Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id='fname'
    )
    last_name = StringField(
        'Last Name',
        validators=[validators.Length(min=2, max=32), validators.DataRequired(message="Please enter your last name.")],
        render_kw={'placeholder': 'Last Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id='lname'
    )
    full_name = StringField(
        'Full Name',
        render_kw={'placeholder': 'We\'ll take care of this one', 'readonly': True},
        id='fullname'
    )
    user_name = StringField(
        'Username',
        validators=[validators.Length(max=20, message="Username cannot be longer than 20 charachters, if you have a middlename you can remove it or use its initial.")],
        render_kw={'placeholder': 'Created by username policy', 'readonly': True},
        id='username'
    )
    email = StringField(
        'Email',
        validators=[validators.Email(message='Please enter your email.'), validators.Length(min=6, max=128)],
        render_kw={'placeholder': 'Email'}
    )
    password = PasswordField(
        'Password',
        validators=[validators.DataRequired(message="Please enter a password"), validators.Length(min=3)],
        render_kw={'placeholder': 'Password'}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[validators.EqualTo('password', message='Passwords must match!')],
        render_kw={'placeholder': 'Confirm Password'}
    )
    terms = BooleanField(
        'Terms',
        validators=[validators.DataRequired('You must agree to the terms and conditions')]
    )
    submit = SubmitField('Register User', render_kw={'class': 'btn'})

class LoginForm(FlaskForm):
    username = StringField(
        'Username', 
        validators=[validators.DataRequired()],
        render_kw={'placeholder': 'Username'}
    )
    password = PasswordField(
        'Password',
        validators=[validators.DataRequired()],
        render_kw={'placeholder': 'Password'}
    )
    login = SubmitField('Log In', render_kw={'class': 'btn'})

class UserEdit(FlaskForm):
    givenName = StringField(
        'First Name',
        validators=[validators.DataRequired("Cannot be empty.")],
        render_kw={'placeholder': 'First Name'}
    )
    sn = StringField(
        'Last Name',
        validators=[validators.DataRequired("Cannot be empty.")],
        render_kw={'placeholder': 'Last Name'}
    )
    displayName = StringField(
        'Display Name',
        validators=[validators.DataRequired("Cannot be empty.")],
        render_kw={'placeholder': 'Display Name'}
    )
    description = StringField(
        'Description',
        render_kw={'placeholder': 'Description'}
    )
    mail = StringField(
        'Mail',
        validators=[validators.Email(message="Please enter a valid email")],
        render_kw={'placeholder': 'Email'}
    )
    confirm = BooleanField(
        'Confirm Changes',
        validators=[validators.DataRequired('You have to confirm that you want to make any changes,')]
    )
    apply = SubmitField('Apply', render_kw={'class': 'btn'})
    '''def __init__(self, givenName_, sn_, displayName_, description_, mail_):
        givenName = StringField(
            'First Name',
            render_kw={'placeholder': 'First Name', 'value': str(givenName_)}
        )
        sn = StringField(
            'Last Name',
            render_kw={'placeholder': 'Last Name', 'value': str(sn_)}
        )
        displayName = StringField(
            'Display Name',
            render_kw={'placeholder': 'Display Name', 'value': str(displayName_)}
        )
        description = StringField(
            'Description',
            render_kw={'placeholder': 'Description', 'value': str(description_)}
        )
        mail = StringField(
            'Mail',
            render_kw={'placeholder': 'Mail', 'value': str(mail_)}
        )
        confirm = BooleanField(
            'Confirm',
            validators=[validators.DataRequired('You have to confirm that you want to make any changes.')]
        )
        apply = SubmitField('Apply', render_kw={'class': 'btn btn-primary'})'''

class UserOldPwd(FlaskForm):
    username = HiddenField('Username')
    password = PasswordField(
        'Current Password',
        validators=[validators.DataRequired(message="You need to provide your old password.")],
        render_kw={'placeholder': 'Current Password'}
    )
    proceed = SubmitField('Proceed', render_kw={'class': 'btn'})

class UserChangePwd(FlaskForm):
    username = HiddenField('Username')
    password = PasswordField(
        'New Password',
        validators=[validators.Length(min=3, max=128, message="Your password must meet the minimum requirements!")],
        render_kw={'placeholder': 'New Password'}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[validators.EqualTo('password', message="The passwords must match!")],
        render_kw={'placeholder': 'Retype New Password'}
    )
    change = SubmitField('Change Password', render_kw={'class': 'btn'})