from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from frontend import frontend
from nav import nav

app = Flask('__name__')

# The below line is a placeholder as there is currently no config file
# AppConfig(app) 

Bootstrap(app)

app.register_blueprint(frontend)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SECRET_KEY'] = 'devkey'

nav.init_app(app)

if __name__ == "__main__":
	app.run()