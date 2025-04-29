from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import User

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired()
    ])
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in progress', 'In Progress'),
        ('done', 'Done')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ])
    assignee = SelectField('Assignee', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.assignee.choices = [(0, 'Unassigned')] + [
            (user.id, user.username) 
            for user in User.query.order_by(User.username).all()
        ]

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=1, max=1000)
    ])
    submit = SubmitField('Add Comment') 