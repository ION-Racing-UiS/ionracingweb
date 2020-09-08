from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, SelectField, HiddenField, validators, IntegerField, FloatField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.html5 import DateField
import app.pylib.win_user
from app.pylib.auth_user import User

class RegisterForm(FlaskForm):
    ou = SelectField(
        "* Department",
        validators=[validators.DataRequired("You have to pick a department.")],
        render_kw={},
        id="ou"
    )
    description = StringField(
        "Description/Role",
        validators=[],
        render_kw={'placeholder': 'Description'},
        id="description"
    )
    givenName = StringField(
        "* Given Name",
        validators=[validators.DataRequired("You need to enter your first name.")],
        render_kw={'placeholder': 'Given Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id="givenName"
    )
    sn = StringField(
        "* Surname",
        validators=[validators.DataRequired("You need to enter your last name.")],
        render_kw={'placeholder': 'Last Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id="sn"
    )
    full_name = StringField(
        "Full Name",
        validators=[],
        render_kw={'placeholder': 'Generated full name', 'disabled': 'true'},
        id="fullname"
    )
    username = StringField(
        "Username",
        validators=[],
        render_kw={'placeholder': 'Generated username', 'disabled': 'true'},
        id="username"
    )
    mail = StringField(
        "* Email",
        validators=[validators.DataRequired("You need to enter your email."), validators.Email("Has to be a valid email.")],
        render_kw={'placeholder': 'Email'},
        id="mail"
    )
    c = SelectField(
        "Country Code",
        validators=[],
        render_kw={'placeholder': 'Country Code'},
        id="c"
    )
    l = StringField(
        "Location (City)",
        validators=[],
        render_kw={'placeholder': 'Location (City)'},
        id="l"
    )
    st = StringField(
        "State/Province",
        validators=[],
        render_kw={'placeholder': 'State/Province'},
        id="st"
    )
    postalCode = StringField(
        'Postal Code',
        validators=[],
        render_kw={'placeholder': 'Postal Code'},
        id="postalCode"
    )
    streetAddress = StringField(
        "Street Address",
        validators=[],
        render_kw={'placeholder': 'Street Address'},
        id="streetAddress"
    )
    password = PasswordField(
        "* Password",
        validators=[validators.DataRequired("You need to enter a password."), validators.Length(min=4, max=128, message="A minimum length of 4 is required for the password.")],
        render_kw={},
        id="password"
    )
    confirm_password = PasswordField(
        "* Confirm Password",
        validators=[validators.EqualTo('password', message="The passwords must match!")],
        render_kw={},
        id="confirm_password"
    )
    terms = BooleanField(
        "Terms and Agreement",
        validators=[validators.DataRequired("You have to agree to the terms and conditions.")],
        render_kw={},
        id="terms"
    )
    submit = SubmitField(
        "Register User",
        render_kw={'class': 'btn'}
    )

    def __init__(self, ous=[()], countries=[()], *args, **kwargs):
        '''
        This form need a list of tuples for the department field.\n
        Example: `[('IT', 'IT'), ('Electronics', 'Electronics')]`\n
        The departments <type:pyad.adcontainer.ADContainer> can be found in the `IONRacing` ou on a DC.
        '''
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.ou.choices = ous
        self.c.choices = countries
        self.c.data = "NO"

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

class AdminAddCar(FlaskForm):
    year = IntegerField(
        'Year',
        validators=[validators.DataRequired()],
        render_kw={'placeholder': 'Year'}
    )
    name = StringField(
        'Name',
        validators=[],
        render_kw={'placeholder': 'Name'}
    )
    number = IntegerField(
        'Number',
        validators=[],
        render_kw={'placeholder': 'Number'}
    )
    img = FileField(
        'Image',
        validators=[FileAllowed(app.carimages, "Images only!")],
    )
    mass = StringField(
        'Mass',
        validators=[],
        render_kw={'placeholder': 'Mass'}
    )
    engine = StringField(
        'Engine',
        validators=[],
        render_kw={'placeholder': 'Engine'}
    )
    output = StringField(
        'Output',
        validators=[],
        render_kw={'placeholder': 'Output kW/PS'}
    )
    torque = FloatField(
        'Torque',
        validators=[],
        render_kw={'placeholder': 'Torque Nm'}
    )
    submit = SubmitField('Add car', render_kw={'class': 'btn'})

class AdminEditCar(FlaskForm):
    cid = HiddenField()
    year = IntegerField(
        'Year',
        validators=[],
        render_kw={'placeholder': 'Year'}
    )
    name = StringField(
        'Name',
        validators=[],
        render_kw={'placeholder': 'Name'}
    )
    number = IntegerField(
        'Number',
        validators=[],
        render_kw={'placeholder': 'Number'}
    )
    img = FileField(
        'Image',
        validators=[FileAllowed(app.carimages, "Images only!")],
    )
    mass = StringField(
        'Mass',
        validators=[],
        render_kw={'placeholder': 'Mass'}
    )
    engine = StringField(
        'Engine',
        validators=[],
        render_kw={'placeholder': 'Engine'}
    )
    output = StringField(
        'Output',
        validators=[],
        render_kw={'placeholder': 'Output kW/PS'}
    )
    torque = FloatField(
        'Torque',
        validators=[],
        render_kw={'placeholder': 'Torque Nm'}
    )
    confirm = BooleanField(
        'Are you sure you want to make changes?',
        validators=[validators.DataRequired()]
    )
    submit = SubmitField('Save', render_kw={'class': 'btn'})

class AdminRemoveCar(FlaskForm):
    cars = HiddenField(render_kw={'id': 'selected'})
    confirm = BooleanField(
        'Are you sure you want to delete these car(s)?',
        validators=[validators.DataRequired()]
    )
    submit = SubmitField('Remove', render_kw={'class': 'btn'})

class AdminTeamAdd(FlaskForm):
    year = IntegerField(
        'Year',
        validators=[],
        render_kw={'placeholder': 'Year'}
    )
    submit = SubmitField('Create', render_kw={'class': 'btn'})

class AdminTeamRemove(FlaskForm):
    team = SelectField(
        'Team',
        choices=[()],
        validators=[],
        render_kw={'placeholder': 'Team'}
    )
    confirm = BooleanField(
        'Are you sure you want to delete the team?',
        validators=[validators.DataRequired()]
    )
    submit = SubmitField('Delete', render_kw={'class': 'btn'})
    
    '''def __init__(self, choises=[()]):
        \'''
        This form need a list of tuples for the team field.\n
        Example: `[('2019', '2019'), ('2020', '2020')]`\n
        The teams can be found in the Teams ou on a DC.
        \'''
        super(AdminTeamRemove).__init__()
        self.team.choices = choises'''

class AdminUser(FlaskForm):
    c = StringField(
        'Country Code',
        validators=[],
        render_kw={'placeholder': 'Country Code', 'disabled': 'true'},
        id="c"
    )
    cn = StringField(
        'cn',
        validators=[],
        render_kw={'disabled': 'true'},
        id="cn"
    )
    company = StringField(
        'Company',
        validators=[],
        render_kw={'disabled': 'true'},
        id="company"
    )
    displayName = StringField(
        'Display Name',
        validators=[validators.DataRequired(), validators.Length(min=3, message="Display Name must have a min length of 3 charaters.")],
        render_kw={'placeholder': 'Display Name'},
        id="displayName"
    )
    givenName = StringField(
        'Given Name',
        validators=[validators.DataRequired()],
        render_kw={'placeholder': 'Given Name'},
        id="givenName"
    )
    homeDirectory = StringField(
        'homeDirectory',
        validators=[],
        render_kw={'disabled': 'true'},
        id="homeDirectory"
    )
    homeDrive = StringField(
        'homeDrive',
        validators=[],
        render_kw={'disabled': 'true'},
        id="homeDrive"
    )
    l = StringField(
        'Location (City)',
        validators=[],
        render_kw={'disabled': 'true', 'placeholder': 'City'},
        id="l"
    )
    mail = StringField(
        'Email',
        validators=[],
        render_kw={'disabled': 'true', 'placeholder': 'Email'},
        id="mail"
    )
    name = StringField(
        'Name',
        validators=[],
        render_kw={'disabled': 'true'},
        id="name"
    )
    postalCode = StringField(
        'Postal Code',
        validators=[],
        render_kw={'disabled': 'true'},
        id="postalCode"
    )
    profilePath = StringField(
        'profilePath',
        validators=[],
        render_kw={'disabled': 'true'},
        id="profilePath"
    )
    sAMAccountName = StringField(
        'sAMAccountName',
        validators=[],
        render_kw={'disabled': 'true'},
        id="sAMAccountName"
    )
    sn = StringField(
        'sn',
        validators=[validators.DataRequired()],
        render_kw={'placeholder': 'Lastname'},
        id="sn"
    )
    st = StringField(
        'State',
        validators=[],
        render_kw={'disabled': 'true'},
        id="st"
    )
    streetAddress = StringField(
        'streetAddress',
        validators=[],
        render_kw={'disabled': 'true'},
        id="streetAddress"
    )
    userPrincipalName = StringField(
        'userPrincipalName',
        validators=[],
        render_kw={'disabled': 'true'},
        id="userPrincipalName"
    )
    year_select = SelectField(
        'Year select',
        choices=[()],
        render_kw={'onchange': 'changeUserYear();'},
        id="year_select"
    )
    department = StringField(
        'Department',
        validators=[],
        render_kw={'placeholder': 'Department'},
        id="department"
    )
    description = StringField(
        'Description',
        validators=[],
        render_kw={'placeholder': 'Description'},
        id="description"
    )
    title = StringField(
        'Title',
        validators=[],
        render_kw={'placeholder': 'Title'},
        id="title"
    )
    wbemPath = FileField(
        'Image',
        validators=[FileAllowed(app.carimages, "Images Only!")],
        render_kw={},
        id="wbemPath"
    )
    imgPath = HiddenField(
        validators=[],
        render_kw={},
        id="imgPath"
    )
    confirm = BooleanField(
        'Are you sure you want to apply the changes?',
        validators=[validators.DataRequired()],
        render_kw={},
        id="confirm"
    )
    submit = SubmitField(
        'Save',
        validators=[],
        render_kw={'class': 'btn'},
        id="submit"
    )

    def __init__(self, teams=[], country="", *args, **kwargs):
        '''
        This form need a list of tuples for the year_select field.\n
        Example: `[('2019', '2019'), ('2020', '2020')]`\n
        The teams can be found in the Teams ou on a DC.
        '''
        super(AdminUser, self).__init__(*args, **kwargs)
        self.year_select.choices = teams
        self.c.data = country

class AdminCreateUser(FlaskForm):
    ou = SelectField(
        "* Department",
        validators=[validators.DataRequired("You have to pick a department.")],
        render_kw={},
        id="ou"
    )
    description = StringField(
        "Description/Role",
        validators=[],
        render_kw={'placeholder': 'Description'},
        id="description"
    )
    givenName = StringField(
        "* Given Name",
        validators=[validators.DataRequired("You need to enter your first name.")],
        render_kw={'placeholder': 'Given Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id="givenName"
    )
    sn = StringField(
        "* Surname",
        validators=[validators.DataRequired("You need to enter your last name.")],
        render_kw={'placeholder': 'Last Name', 'oninput': 'setUsername()', 'onchange': 'setUsername()'},
        id="sn"
    )
    full_name = StringField(
        "Full Name",
        validators=[],
        render_kw={'placeholder': 'Generated full name', 'disabled': 'true'},
        id="fullname"
    )
    username = StringField(
        "Username",
        validators=[],
        render_kw={'placeholder': 'Generated username', 'disabled': 'true'},
        id="username"
    )
    mail = StringField(
        "* Email",
        validators=[validators.DataRequired("You need to enter your email."), validators.Email("Has to be a valid email.")],
        render_kw={'placeholder': 'Email'},
        id="mail"
    )
    c = SelectField(
        "Country Code",
        validators=[],
        render_kw={'placeholder': 'Country Code'},
        id="c"
    )
    l = StringField(
        "Location (City)",
        validators=[],
        render_kw={'placeholder': 'Location (City)'},
        id="l"
    )
    st = StringField(
        "State/Province",
        validators=[],
        render_kw={'placeholder': 'State/Province'},
        id="st"
    )
    postalCode = StringField(
        'Postal Code',
        validators=[],
        render_kw={'placeholder': 'Postal Code'},
        id="postalCode"
    )
    streetAddress = StringField(
        "Street Address",
        validators=[],
        render_kw={'placeholder': 'Street Address'},
        id="streetAddress"
    )
    submit = SubmitField(
        "Register User",
        render_kw={'class': 'btn'}
    )

    def __init__(self, ous=[()], countries=[()], *args, **kwargs):
        '''
        This form need a list of tuples for the department field.\n
        Example: `[('IT', 'IT'), ('Electronics', 'Electronics')]`\n
        The departments <type:pyad.adcontainer.ADContainer> can be found in the `IONRacing` ou on a DC.
        '''
        super(AdminCreateUser, self).__init__(*args, **kwargs)
        self.ou.choices = ous
        self.c.choices = countries
        self.c.data = "NO"