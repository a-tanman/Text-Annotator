# This file contains the app frontend

from functools import lru_cache
from flask import request, session, current_app, Blueprint, render_template, flash, redirect, url_for, g
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_wtf import FlaskForm
from wtforms.fields import *
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
from werkzeug.utils import secure_filename
from forms import *
from nav import nav
import os
import pandas as pd

frontend = Blueprint('frontend', __name__)

# This code adds a navbar 
nav.register_element('frontend_top', Navbar(
    View('Text-Annotator', '.index'),
    View('Home', '.index'),
    View('Upload Data', '.upload_data')))
    # View('Sample Data & Annotation Settings', '.display_data')))
   
@frontend.route('/')
def index():
    return render_template('index.html')


# Create signup form which allows users to upload data
@frontend.route('/upload-data/', methods=('GET', 'POST'))
def upload_data():
    form = SignupForm()
        
    if form.validate_on_submit():
        
        f = form.sample_file.data
        filename = secure_filename(f.filename)

        # Save file into disk for it to be read later - this is better than
        # reading it into memory especially for large files, note that a data
        # folder must be created
        f.save(os.path.join(current_app.root_path, 'data', filename))
        
        # Flash a message when a user completes the upload successfully.
        flash('Hello, {}. Upload {} successful.'
              .format(escape(form.name.data), filename))

        # Redirect to page to that shows samples of data
        return redirect(url_for('.display_data', f_name = filename, user_name = form.name.data))

    return render_template('upload.html', form=form)

# Create template to display csv using pandas and provide fields to input labels
@frontend.route('/display-data', methods=('GET', 'POST'))
def display_data():

    # Filenames are passed as HTTP requests    
    filename = request.args['f_name']
    file_path = os.path.join(current_app.root_path, 'data', filename)
    
    #Use lru_cache function to prevent multiple file I/O
    df = read_df(file_path)
    
    # Set number of characters to show in sample data
    pd.set_option('display.max_colwidth', 1000)
    
    cols = list(df)
    
    # Pass list of column names to DisplayForm, which will then be selected for
    # labelling
    form = DisplayForm(vals = cols)
    
    total_length = len(df)
    disp_len = 0

    if form.validate_on_submit():
        if (form.annotate.data): # Check if SubmitField is clicked for 'sample' or 'annotate'
            session.clear()
            session['counter'] = 0 # This counter is needed to reference the pandas dataframe index
            session['user_name'] = request.args['user_name']

            # Pass filename, colnames, and labels to annotate data view
            return redirect(url_for('.annotate_data', f_name = filename, colname = form.sel_col.data, labels = form.labels.data)) 
        disp_len = int(form.num_rows.data) # Parameter for number of rows of samlpe data to show
        
    return render_template('display.html', f_name = filename, length = total_length, dataframe = df.sample(n = disp_len).to_html(), form = form, cols = cols)

# Route for annotating data, which is a separate page that will show the text
# and buttons to label the text
@frontend.route('/annotate_data/', methods = ('GET', 'POST'))
def annotate_data():
    
    filename = request.args['f_name']
    colname = request.args['colname']
    col_label = colname + '_label'
    labels = request.args['labels'].split(';')
        
    file_path = os.path.join(current_app.root_path, 'data', filename) # Note that a 'data' folder must be created
    res_file = os.path.join(current_app.root_path, 'data', session['user_name'] + '_' + filename + '_' + col_label + 's.csv')
    df = read_df(file_path)
    
    # Read last line and increase counter if lines are already labelled and
    # continue from there, so users can continue labelling even if they close
    # their computer Cannot use cached function for reading DF because file is
    # constantly updated
    if (session['counter'] == 0) and os.path.isfile(res_file):
        res_df = pd.read_csv(res_file)
        session['counter'] = res_df.index[-1] + 1

    # Create class AnnotateForm and dynamically add label buttons
    class AnnotateForm(FlaskForm):
        pass

    for lab in labels:
        setattr(AnnotateForm, lab, SubmitField())

    form = AnnotateForm()

    if form.validate_on_submit():
        
        cur_count = session['counter']
        row = df.iloc[[session['counter']]]
        for key, value in form.data.items():
            if value is True:
                
                row[col_label] = key
        
        with open(res_file, 'a') as f:
            if session['counter'] == 0:
                print_header = True
            else:
                print_header = False
            
            row.to_csv(f, header=print_header)

        session['counter'] += 1
    
    # Show text for labelling within jumbotron
    text = df.at[session['counter'], colname]
    
    return render_template('annotate.html', form = form, text_string = text)

# Use lru cache to minimise multiple file I/O
@lru_cache(maxsize = 32)
def read_df(filepath):
    return pd.read_csv(filepath)