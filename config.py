import os
SECRET_KEY = 'asdhadksjahdakhdas876986^&%&*^%^A%UADSHADSHJASDGHJGAD'

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

auth0_config = {
    "AUTH0_DOMAIN" : "dev-2bm0ojvr4sfeljpt.us.auth0.com",
    "ALGORITHMS" : ["RS256"],
    "API_AUDIENCE" : "id_specimen_finder"
}

