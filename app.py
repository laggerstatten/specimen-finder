# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import os
import sys
import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    abort,
    session,
    flash)
from models import setup_db, Animal, Institution, Specimen
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from forms import *
from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
#from config import SECRET_KEY



AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_BASE_URL = os.getenv('AUTH0_BASE_URL')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('API_AUDIENCE')
SECRET_KEY = os.getenv('SECRET_KEY')


# ----------------------------------------------------------------------------#
# Initialize App
# ----------------------------------------------------------------------------#


def create_app(test_config=None):
    app = Flask(__name__)

    app.secret_key = SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    setup_db(app)
    CORS(app)


    # ----------------------------------------------------------------------------#
    # Controllers.
    # ----------------------------------------------------------------------------#
    # auth0 info
    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        # TODO replace with variable
        access_token_url='https://dev-2bm0ojvr4sfeljpt.us.auth0.com' + '/oauth/token',
        authorize_url='https://dev-2bm0ojvr4sfeljpt.us.auth0.com' + '/authorize',
       
        client_kwargs={
            'scope': 'openid profile email'
        }
    )


    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS'
        )
        return response

    # route handler for home page when anonymous user visits


    @app.route('/')
    @cross_origin()
    def index():
        return render_template('pages/home.html')

    # route handler to log in


    @app.route('/login', methods=['GET'])
    @cross_origin()
    def login():
        print('Audience: {}'.format(API_AUDIENCE))
        return auth0.authorize_redirect(
            redirect_uri='%s/post-login' % AUTH0_CALLBACK_URL,
            audience=API_AUDIENCE
        )

    # route handler for home page once logged in


    @app.route('/post-login', methods=['GET'])
    @cross_origin()
    def post_login():
        token = auth0.authorize_access_token()
        session['token'] = token['access_token']
        print(session['token'])
        return render_template('pages/home.html')

    # route handler to log out


    @app.route('/logout')
    def log_out():
        # clear the session
        session.clear()
        # redirect user to logout endpoint
        params = {'returnTo': url_for(
            'index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        # TODO replace with variable
        return redirect('dev-2bm0ojvr4sfeljpt.us.auth0.com' + '/v2/logout?' + urlencode(params))
        #return redirect(AUTH0_DOMAIN + '/v2/logout?' + urlencode(params))



    #  Animals
    #  ----------------------------------------------------------------
    @app.route('/animals', methods=['GET'])
    @requires_auth('get:animals')
    def animals(payload):
        animals = Animal.query.all()

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = []
            for animal in animals:
                response.append(animal.view())

            return jsonify(
                {
                    "animals": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/animals.html', 
                animals=animals)


    #  Animals -- Search
    #  ----------------------------------------------------------------
    @app.route('/animals/search', methods=['POST'])
    @requires_auth('get:animals')
    def search_animals(payload):

        if request.headers.get('Content-Type') == 'application/json':
            body = request.get_json()
            search_term = body.get('search_term')
        else:
            search_term = request.form.get('search_term', '')

        search = "%{}%".format(search_term)
        animals = Animal.query.filter(
            or_(
                Animal.genus.ilike(search),
                Animal.specificepithet.ilike(search),
                Animal.sciname.ilike(search),
                Animal.maincommonname.ilike(search),
                Animal.taxonorder.ilike(search),
                Animal.biogeographicrealm.ilike(search),
                Animal.iucnstatus.ilike(search)
            )
        ).all()

        matched_animals = []
        for animal in animals:
            matched_animals.append(animal.view())

        response = {
            "count": len(animals),
            "data": matched_animals
        }

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            return jsonify(
                {
                    "animals": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/search_animals.html',
                results=response,
                search_term=request.form.get('search_term', ''))


    #  Animals -- Individual Record
    #  ----------------------------------------------------------------
    @app.route('/animals/<int:animal_id>', methods=['GET'])
    @requires_auth('get:animals')
    def show_animal(payload, animal_id):
        show_animal = Animal.query.get_or_404(animal_id)

        data = vars(show_animal)

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = show_animal.view()
            return jsonify(
                {
                    "animal": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/show_animal.html',
                animal=data)


    #  Animals -- Create
    #  ----------------------------------------------------------------
    @app.route('/animals/create', methods=['GET'])
    @requires_auth('post:animals')
    def create_animal_form(payload):

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            return jsonify(
                {
                    "message": "OK",
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'forms/new_animal.html',
                form=AnimalForm())


    @app.route('/animals/create', methods=['POST'])
    @requires_auth('post:animals')
    def create_animal_submission(payload):
        if request.headers.get('Content-Type') == 'application/json':
            body = request.get_json()
            form = AnimalForm(data=body, meta={'csrf': False})
            genus = body.get("genus")
            specificepithet = body.get("specificepithet")
            sciname = body.get("sciname")
            maincommonname = body.get("maincommonname")
            taxonorder = body.get("taxonorder")
            biogeographicrealm = body.get("biogeographicrealm")
            iucnstatus = body.get("iucnstatus")
            
        else:
            form = AnimalForm(request.form, meta={'csrf': False})
            genus = form.genus.data
            specificepithet = form.specificepithet.data
            sciname = form.sciname.data
            maincommonname = form.maincommonname.data
            taxonorder = form.taxonorder.data
            biogeographicrealm = form.biogeographicrealm.data
            iucnstatus = form.iucnstatus.data

        # Validate all fields
        if form.validate():
                animal = Animal(
                    genus = genus, 
                    specificepithet = specificepithet,
                    sciname = sciname,
                    maincommonname = maincommonname,
                    taxonorder = taxonorder,
                    biogeographicrealm = biogeographicrealm,
                    iucnstatus = iucnstatus
                )
                animal.insert()

                if request.headers.get('Content-Type') == 'application/json':
                    # If so, return a JSON response
                    return jsonify(
                        {
                            "animals": animal.view(),
                            "success": True
                        }
                    ), 200
                else:
                    # Otherwise, render an HTML template
                    return render_template(
                        'pages/home.html')

        else:
            message = []
            for field, errors in form.errors.items():
                for error in errors:
                    message.append(f"{field}: {error}")
            flash('Please fix the following errors: ' + ', '.join(message))
            form = AnimalForm()
            return render_template(
                'forms/new_animal.html',
                form=form)


    #  Animals -- Update
    #  ----------------------------------------------------------------
    @app.route('/animals/<int:animal_id>/edit', methods=['GET'])
    @requires_auth('edit:animals')
    def edit_animal(payload, animal_id):

        animal_found = Animal.query.get_or_404(animal_id)

        data = vars(animal_found)

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = animal_found.view()
            return jsonify(
                {
                    "animal": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'forms/edit_animal.html',
                form=AnimalForm(),
                animal=data)


    @app.route('/animals/<int:animal_id>/edit', methods=['POST', 'PATCH'])
    @requires_auth('post:animals')
    def edit_animal_submission(payload, animal_id):
        animal = Animal.query.filter(Animal.id == animal_id).one_or_none()
        # check if exists
        if not animal:
            return render_template('errors/404.html')

        try:
            if request.headers.get('Content-Type') == 'application/json':
                body = request.get_json()
                genus = body.get("genus", None)
                specificepithet = body.get("specificepithet", None)
                sciname = body.get("sciname", None)
                maincommonname = body.get("maincommonname", None)
                taxonorder = body.get("taxonorder", None)
                biogeographicrealm = body.get("biogeographicrealm", None)
                iucnstatus = body.get("iucnstatus", None)
                
                # If genus found in the request, change the genus
                if genus is not None:
                    animal.genus = genus
            
                # If specificepithet found in the request, change the specificepithet
                if specificepithet is not None:
                    animal.specificepithet = specificepithet

                # If sciname found in the request, change the sciname
                if sciname is not None:
                    animal.sciname = sciname

                # If maincommonname found in the request, change the maincommonname
                if maincommonname is not None:
                    animal.maincommonname = maincommonname

                # If taxonorder found in the request, change the taxonorder
                if taxonorder is not None:
                    animal.taxonorder = taxonorder

                # If biogeographicrealm found in the request, change the biogeographicrealm
                if biogeographicrealm is not None:
                    animal.biogeographicrealm = biogeographicrealm

                # If iucnstatus found in the request, change the iucnstatus
                if iucnstatus is not None:
                    animal.iucnstatus = iucnstatus

                # If any one of specificepithet or genus found in the request than update
                if genus is not None or specificepithet is not None or sciname is not None or maincommonname is not None or taxonorder is not None or biogeographicrealm is not None or iucnstatus is not None:
                    animal.update()

                return jsonify(
                    {
                        "animals": animal.view(),
                        "success": True
                    }
                ), 200

            elif request.method == 'POST':
                if request.args.get('_method', '').upper() == 'PATCH':
                    animal.genus = request.form['genus']
                    animal.specificepithet = request.form['specificepithet']
                    animal.sciname = request.form['sciname']
                    animal.maincommonname = request.form['maincommonname']
                    animal.taxonorder = request.form['taxonorder']
                    animal.biogeographicrealm = request.form['biogeographicrealm']
                    animal.iucnstatus = request.form['iucnstatus']
                    
                    animal.update()

                    return redirect(url_for(
                        'show_animal',
                        animal_id=animal_id))

        except:
            # If any error abort
            abort(422)


    #  Animals -- Delete
    #  ----------------------------------------------------------------
    @app.route('/animals/<int:animal_id>', methods=['DELETE'])
    @requires_auth('delete:animals')
    def delete_animal(payload, animal_id):
        deleted_animal = Animal.query.filter(Animal.id == animal_id).one_or_none()
        # FIXME does not delete if there is a specimen
        
        #If the animal is not found, return 404
        if deleted_animal is None:
            abort(404)

        deleted_animal.delete()

        #Return the response object
        return jsonify(
            {
                "delete": animal_id,
                "success": True
            }
        ), 200


    #  Institutions
    #  ----------------------------------------------------------------
    @app.route('/institutions', methods=['GET'])
    @requires_auth('get:institutions')
    def institutions(payload):
        institutions = Institution.query.all()

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = []
            for institution in institutions:
                response.append(institution.view())

            return jsonify(
                {
                    "institutions": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/institutions.html',
                institutions=institutions)


    #  Institutions -- Search
    #  ----------------------------------------------------------------
    @app.route('/institutions/search', methods=['POST'])
    @requires_auth('get:institutions')
    def search_institutions(payload):

        if request.headers.get('Content-Type') == 'application/json':
            body = request.get_json()
            search_term = body.get('search_term')
        else:
            search_term = request.form.get('search_term', '')

        search = "%{}%".format(search_term)
        institutions = Institution.query.filter(
            or_(
                Institution.name.ilike(search),
                Institution.street.ilike(search),
                Institution.longitude.ilike(search),
                Institution.latitude.ilike(search),
                Institution.city.ilike(search),
                Institution.state.ilike(search)
            )
        ).all()

        matched_institutions = []
        for institution in institutions:
            matched_institutions.append(institution.view())

        response = {
            "count": len(institutions),
            "data": matched_institutions
        }

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            return jsonify(
                {
                    "institutions": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/search_institutions.html',
                results=response,
                search_term=request.form.get('search_term', ''))


    #  Institutions -- Individual Record
    #  ----------------------------------------------------------------
    @app.route('/institutions/<int:institution_id>', methods=['GET'])
    @requires_auth('get:institutions')
    def show_institution(payload, institution_id):
        show_institution = Institution.query.get_or_404(institution_id)

        data = vars(show_institution)

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = show_institution.view()
            return jsonify(
                {
                    "institution": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/show_institution.html',
                institution=data)


    #  Institutions -- Create
    #  ----------------------------------------------------------------
    @app.route('/institutions/create', methods=['GET'])
    @requires_auth('post:institutions')
    def create_institution_form(payload):

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            return jsonify(
                {
                    "message": "OK",
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'forms/new_institution.html',
                form=InstitutionForm())


    @app.route('/institutions/create', methods=['POST'])
    @requires_auth('post:institutions')
    def create_institution_submission(payload):
        if request.headers.get('Content-Type') == 'application/json':
            body = request.get_json()
            form = InstitutionForm(data=body, meta={'csrf': False})
            name = body.get("name")
            street = body.get("street")
            longitude = body.get("longitude")
            latitude = body.get("latitude")
            city = body.get("city")
            state = body.get("state")
            
        else:
            form = InstitutionForm(request.form, meta={'csrf': False})
            name=form.name.data
            street=form.street.data
            longitude=form.longitude.data
            latitude=form.latitude.data
            city=form.city.data
            state=form.state.data

        # Validate all fields
        if form.validate():
                institution = Institution(
                    name = name, 
                    street = street,
                    longitude = longitude, 
                    latitude = latitude,
                    city = city, 
                    state = state
                )
                institution.insert()

                if request.headers.get('Content-Type') == 'application/json':
                    # If so, return a JSON response
                    return jsonify(
                        {
                            "institutions": institution.view(),
                            "success": True
                        }
                    ), 200
                else:
                    # Otherwise, render an HTML template
                    return render_template(
                        'pages/home.html')

        else:
            message = []
            for field, errors in form.errors.items():
                for error in errors:
                    message.append(f"{field}: {error}")
            flash('Please fix the following errors: ' + ', '.join(message))
            form = InstitutionForm()
            return render_template(
                'forms/new_institution.html', 
                form=form)


    #  Institutions -- Update
    #  ----------------------------------------------------------------
    @app.route('/institutions/<int:institution_id>/edit', methods=['GET'])
    @requires_auth('edit:institutions')
    def edit_institution(payload, institution_id):

        institution_found = Institution.query.get_or_404(institution_id)

        data = vars(institution_found)

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = institution_found.view()
            return jsonify(
                {
                    "institution": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'forms/edit_institution.html',
                form=InstitutionForm(),
                institution=data)


    @app.route('/institutions/<int:institution_id>/edit', methods=['POST', 'PATCH'])
    @requires_auth('post:institutions')
    def edit_institution_submission(payload, institution_id):
        institution = Institution.query.filter(Institution.id == institution_id).one_or_none()
        # check if exists
        if not institution:
            return render_template('errors/404.html')

        try:
            if request.headers.get('Content-Type') == 'application/json':
                body = request.get_json()
                name = body.get("name", None)
                street = body.get("street", None)
                longitude = body.get("longitude", None)
                latitude = body.get("latitude", None)
                city = body.get("city", None)
                state = body.get("state", None)

                # If name found in the request, change the name
                if name is not None:
                    institution.name = name
            
                # If street found in the request, change the street
                if street is not None:
                    institution.street = street

                # If longitude found in the request, change the longitude
                if longitude is not None:
                    institution.longitude = longitude

                # If latitude found in the request, change the latitude
                if latitude is not None:
                    institution.latitude = latitude

                # If city found in the request, change the city
                if city is not None:
                    institution.city = city

                # If state found in the request, change the state
                if state is not None:
                    institution.state = state

                # If any one of street or name found in the request than update
                if street is not None or name is not None or longitude is not None or latitude is not None or city is not None or state is not None:
                    institution.update()

                return jsonify(
                    {
                        "institutions": institution.view(),
                        "success": True
                    }
                ), 200

            elif request.method == 'POST':
                if request.args.get('_method', '').upper() == 'PATCH':
                    institution.name = request.form['name']
                    institution.street = request.form['street']
                    institution.longitude = request.form['longitude']
                    institution.latitude = request.form['latitude']
                    institution.city = request.form['city']
                    institution.state = request.form['state']
                    
                    institution.update()

                    return redirect(url_for(
                        'show_institution',
                        institution_id=institution_id))

        except:
            # If any error abort
            abort(422)


    #  Institutions -- Delete
    #  ----------------------------------------------------------------
    @app.route('/institutions/<int:institution_id>', methods=['DELETE'])
    @requires_auth('delete:institutions')
    def delete_institution(payload, institution_id):
        deleted_institution = Institution.query.filter(Institution.id == institution_id).one_or_none()        
        # FIXME does not delete if there is a specimen

        #If the institution is not found, return 404
        if deleted_institution is None:
            abort(404)

        deleted_institution.delete()

        #Return the response object
        return jsonify(
            {
                "delete": institution_id,
                "success": True
            }
        ), 200


    #  Specimens
    #  ----------------------------------------------------------------
    @app.route('/specimens', methods=['GET'])
    @requires_auth('get:specimens')
    def specimens(payload):
        specimens = SQLAlchemy().session.query(Specimen).\
            options(joinedload(Specimen.animal),
                    joinedload(Specimen.institution)).all()

        '''specimens = Specimen.query().all()'''

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = []
            for specimen in specimens:
                response.append({
                    "specimen_id": specimen.id,
                    "institution_id": specimen.institution.id,
                    "institution_name": specimen.institution.name,
                    "animal_id": specimen.animal.id,
                    "animal_maincommonname": specimen.animal.maincommonname,
                    "sightingdate": specimen.sightingdate.strftime('%Y-%m-%d %H:%M:%S')
                })
        
            return jsonify(
                {
                    "specimens": response,
                    "success": True
                }
            ), 200
        else:
            response = []
            for specimen in specimens:
                response.append({
                    "specimen_id": specimen.id,
                    "institution_id": specimen.institution.id,
                    "institution_name": specimen.institution.name,
                    "animal_id": specimen.animal.id,
                    "animal_maincommonname": specimen.animal.maincommonname,
                    "sightingdate": specimen.sightingdate.strftime('%Y-%m-%d %H:%M:%S')
                })
            # Otherwise, render an HTML template
            return render_template(
                'pages/specimens.html', 
                specimens=response)


    #  Specimens -- Create
    #  ----------------------------------------------------------------
    @app.route('/specimens/create', methods=['GET'])
    @requires_auth('post:specimens')
    def create_specimen_form(payload):
        animals = Animal.query.all()
        institutions = Institution.query.all()

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            return jsonify(
                {
                    "message": "OK",
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'forms/new_specimen.html',
                animals=animals,
                institutions=institutions,
                form=SpecimenForm())


    @app.route('/specimens/create', methods=['POST'])
    @requires_auth('post:specimens')
    def create_specimen_submission(payload):
        if request.headers.get('Content-Type') == 'application/json':
            body = request.get_json()
            form = SpecimenForm(data=body, meta={'csrf': False})
            institution_id = body.get("institution_id")
            animal_id = body.get("animal_id")
            sightingdate = body.get("sightingdate")
        else:
            form = SpecimenForm(request.form, meta={'csrf': False})
            institution_id = form.institution_id.data
            animal_id = form.animal_id.data
            sightingdate = form.sightingdate.data

        # Validate all fields
        if form.validate():
                specimen = Specimen(
                    institution_id = institution_id,
                    animal_id = animal_id,
                    sightingdate = sightingdate
                )
                specimen.insert()

                if request.headers.get('Content-Type') == 'application/json':
                    # If so, return a JSON response
                    return jsonify(
                        {
                            "specimens": specimen.view(),
                            "success": True
                        }
                    ), 200
                else:
                    # Otherwise, render an HTML template
                    return render_template(
                        'pages/home.html')

        else:
            message = []
            for field, errors in form.errors.items():
                for error in errors:
                    message.append(f"{field}: {error}")
            flash('Please fix the following errors: ' + ', '.join(message))
            form = SpecimenForm()
            return render_template(
                'forms/new_specimen.html',
                form=form)


    # ----------------------------------------------------------------------------#
    # Error Handling
    # ----------------------------------------------------------------------------#


    @app.errorhandler(401)
    def unauthorized(ex):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "unauthorized"
        }), 401


    @app.errorhandler(403)
    def auth_403(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": 'You dont have access for this action'
        }), 403


    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404


    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    @app.errorhandler(AuthError)
    def auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        
        return response

    return app


app = create_app()


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)