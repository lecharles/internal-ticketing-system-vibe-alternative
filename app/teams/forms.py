from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Team

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=2, max=64)
    ])
    description = TextAreaField('Description', validators=[
        Length(max=256)
    ])
    submit = SubmitField('Save Team')
    
    def validate_name(self, name):
        team = Team.query.filter_by(name=name.data).first()
        if team is not None:
            raise ValidationError('Please use a different team name.')

class AddMemberForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Member') 