# Simple Text Annotator App in Flask

This flask app is a simple personal project that is meant to make it easier to label or annotate textual data. It is deliberately written in Python only and can be used on local machines in the SOE environment.

Based on a flask-bootstrap template by Mark Brinkmann (https://pythonhosted.org/Flask-Bootstrap/)

### Cloning the project

In a suitable directory, 
```
git clone http://analytics.swg.tech.gov.sg/gitlab/DSD-ANDREW1/Text-Annotator-Flask.git
```

### Installing Dependences

Follow instructions at (https://analytics.swg.tech.gov.sg/gitlab/snippets/5) to set up your PYTHONPATH variable (and also learn about how to install python packages from SWG repo).

Install dependences from requirements.txt to a folder on your *PYTHONPATH*

If you currently do not have flask, install it as well based on the instructions above.

### Running

From main folder directory, you can run the app on port 5000 with:

```python main.py```

Some mock data is found in the ```/data``` folder for you to test out.

### Key Features

- Allows user to upload .csv files and view samples of the data
- Users can select a column to annotate and create labels for this column
- A separate CSV file is created in the ```/data``` folder with the results of the labelling. This file is written to each time you label one row
- A new file is created for each kind of label, and the filename is based on the username.
- If you close the program and start labelling again later, ensure that the data file and username are identical to before, and you should be able to continue from where you last stopped


### Known Issues

In some cases, there are issues with reading csv files that have the wrong encoding. It expects files to be 'UTF-8' encoded.

Your session may also end if you do not use the program for a while, and you'll need to upload the file again.

### Note

Please feel free to contribute to this project, and let me know if there are bugs or feature requests.