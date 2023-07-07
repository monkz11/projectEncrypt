from encrypt import app, User, db, database
from flask_bcrypt import Bcrypt

# runs the app. 
# NOTE: You might get an error when running this. I had to fix a lot of stuff for it to finally run.
# To actually see the website open google and type localhost:5000
if __name__ == '__main__':
    app.run(debug=True) # shows bugs on website if they occur and updates page when changes made in code 
    # user_exists = database.mrz_exists('10')
    # print(user_exists)