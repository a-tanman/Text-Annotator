from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required, Email, DataRequired, ValidationError, Optional
from flask import g

class StartForm(FlaskForm):
    
    submit = SubmitField('Start')

class SignupForm(FlaskForm):
    name = TextField('Please enter a unique key (e.g. name_id) to identify the data you are labelling :\
    <h6> This is necessary so that you can manage multiple sets of data you may be labelling (write this key down!).\
    You can also enter a previous unique key and upload the same original data to continue a previous labelling effort. </h6>', validators=[Required()])

    # Custom validator to check that file is csv
    def validate_csv(form, field):
        
        if not field.data.filename.endswith('csv'):
            
            raise ValidationError('Not a CSV file!')

    sample_file = FileField('.csv file for labelling :', validators=[Required(), validate_csv])
    
    # Uncomment if there are terms and conditions
    # eula = BooleanField(u'I have read the terms and conditions',
    #                    validators=[Required('You must agree to the T&C!')])

    submit = SubmitField('Upload')
    
# This form is used on the display data page to allow the user to sample a number of rows and also input different labels

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

# This form creates a dropdown list to select a new row to annotate
class GotoRowForm(FlaskForm):

    def __init__(self, nrow = None, **kw):
        super(GotoRowForm, self).__init__(**kw)

        # Create list of tuples for the SelectField
        row_list = []
        for i in range(nrow):
            
            row_list.append((i, i))

        self.sel_row.choices = row_list

    sel_row = SelectField('Select Row Number:', default = 0, coerce = int, validators = None)

    row_selected = SubmitField('Go To Selected Row')

# This form is used to add labels from the annotation page
class AddLabelForm(FlaskForm):

    new_lab = TextField('Type any additional label names, one at a time.', default = "")

    add_lab = SubmitField('Add Labels')