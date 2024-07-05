# Specimen Finder App

#### How does it work?

The app has pages which list details for institutions and animals which may be found in these collections. There are also pages to create and update both institution and animal details. There is page to record sightings of animals at these institutions (specimens).

#### How can I access the app?

The casting app has been deployed to Heroku and is currently working at this link:</br>
<strong>[https://specimen-finder-1640d0f0f233.herokuapp.com/](https://specimen-finder-1640d0f0f233.herokuapp.com/)</strong>

To log in, add /login to the url and enter one set of credentials shown below. To log out, just go to /logout.

## Dependencies

- To access the app locally, you need:
  - A database
  - A virtual environment
  - Dependencies installed
  - Environment variables set up
  - An account with Auth0, an authentication service

1. PostgreSQL database: [postgresql.org](https://www.postgresql.org/download/)
2. Auth0 account: [Auth0.com](https://auth0.com/)
3. Virtual environment, dependencies, and environment variables:
```
$ cd project_directory_path/
$ virtualenv env
$ source env/bin/activate
$ source setup.sh
```
4. Local PostgreSQL database:
```
export DATABASE_URL='postgresql://postgres@localhost:XXXX/capstone'
psql -U postgres -d capstone -f insert.sql
```
3. Start the development server:
```
$ export FLASK_APP=app.py 
$ export FLASK_ENV=development
$ flask run --reload
```

## Usage

### Specimen finder roles

There are three roles with different levels of access permissions.

1. <strong>User</strong>: Can retrieve data for animals, institutions, and specimens, and create new records for each

```
Username: user@specimenfinder.com
Password: ?@j)E%Se5MU%75-
```

2. <strong>Editor</strong>: All permissions as User, and can also edit existing records

```
Username: editor@specimenfinder.com
Password: ?@j)E%Se5MU%75-
```

2. <strong>Admin</strong>: All permissions as Editor, and can also delete existing records

```
Username: admin@specimenfinder.com
Password: ?@j)E%Se5MU%75- 
```

### API endpoints

To access this app's API, a user needs to be authenticated. Logging in with approved credentials generates a JWT (JSON Web Token) that grants the user access based on their role's permissions.

The specimen finder app API includes the following endpoints. Below is an overview of their expected behavior.

#### GET /login
- Redirects the user to the Auth0 login page, where the user can log in or sign up
- Sample: ```curl http://127.0.0.1:5000/login```

#### GET /post-login
- Handles the response from the access token endpoint and stores the user's information in a Flask session
- Sample: ```curl http://127.0.0.1:5000/post-login```

#### GET /logout
- Clears the user's session and logs them out
- Sample: ```curl http://127.0.0.1:5000/logout```

#### GET /animals
- Returns a list of all the animals in the database
- Sample: ```curl http://127.0.0.1:5000/animals```

#### GET /animals/{animal_id}
- Returns details about an animal in the database
- Sample: ```curl http://127.0.0.1:5000/animals/1```

#### GET /animals/create
- Returns the form to list an animal
- Sample: ```curl http://127.0.0.1:5000/animals/create```

#### POST /animals/create
- Adds a new animal to the database, including the animal's genus, specific epithet, scientific name, common name, order, biogeographic realm, and IUCN status
- Sample: ```curl http://127.0.0.1:5000/animals/create -X POST -H "Content-Type: application/json" -d '{  'genus': 'Canis', 'specificepithet': 'lupus','sciname': 'Canis_lupus', 'maincommonname': 'Gray Wolf','taxonorder': 'CARNIVORA', 'biogeographicrealm': 'Nearctic|Palearctic', 'iucnstatus': 'LC'}'```

#### GET /animals/{animal_id}/edit
- Returns the form to update an animal
- Sample: ```curl http://127.0.0.1:5000/animals/1/edit```

#### GET /animals/{animal_id}/edit
- Updates an existing animal, with revised details
- Sample: ```curl http://127.0.0.1:5000/animals/1/edit -X POST -H "Content-Type: application/json" '{  'genus': 'Canis', 'specificepithet': 'lupus','sciname': 'Canis_lupus', 'maincommonname': 'Gray Wolf','taxonorder': 'CARNIVORA', 'biogeographicrealm': 'Nearctic|Palearctic', 'iucnstatus': 'LC'}'```

#### DELETE /animals/{animal_id}
- Deletes an animal from the database
- Sample: ```curl http://127.0.0.1:5000/animals/1  -X DELETE```

#### GET /institutions
- Returns a list of all the institutions in the database
- Sample: ```curl http://127.0.0.1:5000/institutions```

#### GET /institutions/{institution_id}
- Returns details about an institution listed in the database
- Sample: ```curl http://127.0.0.1:5000/institutions/1```

#### GET /institutions/create
- Returns the form to list an institution
- Sample: ```curl http://127.0.0.1:5000/institutions/create```

#### POST /institutions/create
- Adds a new institution to the database, including the institution's name, address, city, state, lat, and lon
- Sample: ```curl http://127.0.0.1:5000/institutions -X POST -H "Content-Type: application/json" -d '{ 'name': 'Philadelphia Zoo', 'street': '3400 W Girard Ave', 'longitude': -75.194992,'latitude': 39.975151, 'city': 'Philadelphia', 'state': 'PA'}'```

#### GET /institutions/{institution_id}/edit
- Returns the form to update an institution profile
- Sample: ```curl http://127.0.0.1:5000/institutions/1/edit```

#### GET /institutions/{institution_id}/edit
- Updates an existing institution, with revised details
- Sample: ```curl http://127.0.0.1:5000/institutions/1 -X POST -H "Content-Type: application/json" -d '{ 'name': 'Philadelphia Zoo', 'street': '3400 W Girard Ave', 'longitude': -75.194992,'latitude': 39.975151, 'city': 'Philadelphia', 'state': 'PA'}'```

#### DELETE /institutions/{institution_id}
- Deletes an institution from the database
- Sample: ```curl http://127.0.0.1:5000/institutions/1  -X DELETE```

#### GET /specimens
- Returns a list of all the specimens in the database
- Sample: ```curl http://127.0.0.1:5000/specimens```

#### GET /specimens/create
- Returns the form to record a specimen in the database
- Sample: ```curl http://127.0.0.1:5000/specimens/create```
