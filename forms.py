from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, MonthField
from wtforms.validators import DataRequired


class BudgetCreation(FlaskForm):
    name = StringField('Budget name', validators=[DataRequired()])
    start_month = MonthField('Budget start month', validators=[DataRequired()])
    end_month = MonthField('Budget end month', validators=[DataRequired()])
    submit = SubmitField('Create Budget!')


# Create a form to register new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")
