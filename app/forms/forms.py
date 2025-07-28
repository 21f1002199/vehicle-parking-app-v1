from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Length, Email, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    full_name = StringField('Full Name', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    pin_code = StringField('PIN Code', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=10)])
    submit = SubmitField('Register')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Optional()])
    full_name = StringField('Full Name', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    pin_code = StringField('PIN Code', validators=[InputRequired(), Length(min=4, max=10)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])
    submit = SubmitField('Edit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ParkingLotForm(FlaskForm):
    name = StringField('Lot Name', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    pin_code = StringField('Pin Code', validators=[InputRequired()])
    price = FloatField('Price per unit time', validators=[InputRequired()])
    max_spots = IntegerField('Number of Spots', validators=[InputRequired()])
    submit = SubmitField('Create Lot')

class AdminProfileForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    full_name = StringField('Full Name', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    pin_code = StringField('PIN Code', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update Profile')

class SearchForm(FlaskForm):
    search_type = StringField('Search By (user_id/location)', validators=[InputRequired()])
    keyword = StringField('Keyword', validators=[InputRequired()])
    submit = SubmitField('Search')

class ReservationForm(FlaskForm):
    spot_id = IntegerField('Spot ID')
    lot_id = IntegerField('Lot ID')
    user_id = IntegerField('User ID')
    vehicle_number = StringField('Vehicle Number', validators=[InputRequired()])
    submit = SubmitField('Reserve Spot')

class AdminSearchForm(FlaskForm):
    query = StringField('Search', validators=[InputRequired()])
    search_in = SelectField('Search In', choices=[
        ('users', 'Users (by username)'),
        ('lots', 'Lots (by address or PIN)')
    ])
    submit = SubmitField('Search')
