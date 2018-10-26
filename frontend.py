# This file contains the app frontend

from functools import lru_cache
from flask import request, session, current_app, Blueprint, render_template, flash, redirect, url_for, g, send_file
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
   
@frontend.route('/', methods=['GET', 'POST'])
def index():
    
    # Create form that starts process
    start_form = StartForm()

    if start_form.validate_on_submit():
        return redirect(url_for('.upload_data'))
    
    return render_template('index.html', form = start_form)


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
        flash('Hello, file {} was uploaded  successfully.'.format(escape(filename)))

        # Redirect to page to that shows samples of data
        return redirect(url_for('.display_data', f_name = filename, user_id = form.name.data))

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
    disp_len = 5

    if form.validate_on_submit():
        if (form.annotate.data): # Check if SubmitField is clicked for 'sample' or 'annotate'
            session.clear()
            session['counter'] = 0 # This counter is needed to reference the pandas dataframe index
            session['user_id'] = request.args['user_id']

            # Pass filename, colnames, and labels to annotate data view
            return redirect(url_for('.annotate_data', f_name = filename, colname = form.sel_col.data, labels = form.labels.data)) 
        disp_len = int(form.num_rows.data) # Parameter for number of rows of samlpe data to show
        
    return render_template('display.html', f_name = filename, length = total_length, dataframe = df.sample(n = disp_len), form = form, cols = cols)

# Route for annotating data, which is a separate page that will show the text
# and buttons to label the text
@frontend.route('/annotate_data/', methods = ('GET', 'POST'))
def annotate_data():
    
    filename = request.args['f_name']
    colname = request.args['colname']
    col_label = colname + '_label'
    labels = request.args['labels'].split(';')
        
    file_path = os.path.join(current_app.root_path, 'data', filename) # Note that a 'data' folder must be created
    res_file = os.path.join(current_app.root_path, 'data', session['user_id'] + '_' + col_label + '_' + filename)
    session['res_file_link'] = res_file
    df = read_df(file_path)
    file_len = df.shape[0]
    res_download_link = False
    
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

    if session['counter'] >= 1:
        res_download_link = True
    
    return render_template('annotate.html', form = form, text_string = text, row_num = session['counter'], total_rows = file_len, show_link = res_download_link)




@frontend.route('/get_result/', methods = ('GET', 'POST'))
def get_result():
    link = session['res_file_link']
    res_f_name = link.split('/')
    res_f_name = res_f_name[len(res_f_name) - 1]
    return send_file(link, mimetype = 'text/csv', as_attachment = True, attachment_filename = res_f_name)

# Use lru cache to minimise multiple file I/O
@lru_cache(maxsize = 32)
def read_df(filepath):
    return pd.read_csv(filepath)