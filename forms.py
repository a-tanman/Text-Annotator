from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required, Email, DataRequired, ValidationError, Optional
from flask import g


class SignupForm(FlaskForm):
    name = TextField(u'Your name', validators=[Required()])

    # Custom validator to check that file is csv
    def validate_csv(form, field):
        
        if not field.data.filename.endswith('csv'):
            
            raise ValidationError('Not a CSV file!')

    sample_file = FileField(u'Your .csv file', validators=[Required(), validate_csv])
    
    # Uncomment if there are terms and conditions
    # eula = BooleanField(u'I have read the terms and conditions',
    #                    validators=[Required('You must agree to the T&C!')])

    submit = SubmitField(u'Upload')
    

class DisplayForm(FlaskForm):

    def __init__(self, vals = None, **kw):
        super(DisplayForm, self).__init__(**kw)
        
        # Create list of tuples because SelectField choices requires it
        tup_list = []
        for val in vals:
            tup_list.append((val, val))
        self.sel_col.choices = tup_list
    
    num_rows = SelectField(u'Sample a Number of Rows', choices = [(str(i), str(i)) for i in range(5,50,5)], validators = [Required()])
    
    sample = SubmitField(u'Sample', validators=[Optional()])

    sel_col = SelectField(u'Select column to annotate')
    labels = TextField(u'Type in label names separated by a \';\'')
      
    annotate = SubmitField(u'Annotate', validators=[Optional()])  

    