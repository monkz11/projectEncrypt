from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# this file causes this folder to act as a package, making imports easier
app = Flask(__name__)
app.app_context().push() # Needed to create db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# This class defines the columns for a user in our database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    mrz_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.email},{self.password},{self.mrz_hash}'')"



# DO NOT MOVE THIS IMPORT, OTHERWISE YOU GET A CIRCULAR IMPORT ERROR

from encrypt import routes