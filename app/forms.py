from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class QandAForm(FlaskForm):
    asin = StringField("asin", validators=[DataRequired()])
    submit = SubmitField('Submit Query')