from flask import Flask
import os

# this file causes this folder to act as a package, making imports easier

app = Flask(__name__)

# DO NOT MOVE THIS IMPORT, OTHERWISE YOU GET A CIRCULAR IMPORT ERROR

from encrypt import routes