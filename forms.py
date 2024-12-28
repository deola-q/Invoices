from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    psw = PasswordField('Пароль', validators=[DataRequired()])
    role = SelectField('Роль', choices=[('admin', 'Администратор'), ('worker', 'Работник склада')], validators=[DataRequired()])
    submit = SubmitField('Войти')
