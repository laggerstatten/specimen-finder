# TODO write readme

/c/Users/darwi/AppData/Local/Programs/Python/Python37/python -m venv venv



source venv/Scripts/activate
source setup.sh
FLASK_APP=app.py FLASK_DEBUG=true flask run




export DATABASE_URL='postgresql://postgres:password@localhost:5432/capstone'

psql -U postgres -d capstone -f insert.sql
psql -U postgres -d capstone -f insert.sql -W password






<http://localhost:5000/login>


python test_app.py



## unit testing

psql -U postgres -d capstone -f insert.sql

source venv/Scripts/activate
source setup.sh
python -m unittest -v test_app_ltd.py