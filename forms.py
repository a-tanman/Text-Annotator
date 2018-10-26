from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required, Email, DataRequired, ValidationError, Optional
from flask import g

class StartForm(FlaskForm):
    
    submit = SubmitField('Start')

class SignupForm(FlaskForm):
    name = TextField('Please enter a unique key (e.g. name_id) to identify the data you are labelling :\
    <h6> This is necessary so that you can manage multiple sets of data you may be labelling, and \
    allows you to continue labelling even though your session has ended. </h6>', validators=[Required()])

    # Custom validator to check that file is csv
    def validate_csv(form, field):
        
        if not field.data.filename.endswith('csv'):
            
            raise ValidationError('Not a CSV file!')

    sample_file = FileField('.csv file for labelling :', validators=[Required(), validate_csv])
    
    # Uncomment if there are terms and conditions
    # eula = BooleanField(u'I have read the terms and conditions',
    #                    validators=[Required('You must agree to the T&C!')])

    submit = SubmitField('Upload')
    

class DisplayForm(FlaskForm):

    def __init__(self, vals = None, **kw):
        super(DisplayForm, self).__init__(**kw)
        
        # Create list of tuples because SelectField choices requires it
        tup_list = []
        for val in vals:
            tup_list.append((val, val))
        self.sel_col.choices = tup_list
    
    num_rows = SelectField('Sample a Number of Rows', choices = [(str(i), str(i)) for i in range(10,110,10)], validators = [Required()])
    
    sample = SubmitField('Sample', validators=[Optional()])

    sel_col = SelectField('<br>Select column to annotate')
    labels = TextField('Type in label names separated by a \';\'')
      
    annotate = SubmitField('Annotate', validators=[Optional()])  

    