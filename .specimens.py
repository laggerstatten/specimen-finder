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
from sqlalchemy import or_
from forms import *
from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from config import SECRET_KEY





### START ADDED

AUTH0_CALLBACK_URL='http://localhost:5000/'
AUTH0_CLIENT_ID='6sLabGeB5ngBPni9qr7MqTnYVPm0VOKF'
AUTH0_CLIENT_SECRET='dhEY_R8AoL1Fw41BnfM2_zOrxVsO4omFWQyzfcg0gnBVvmk1MqP3dDcVv2J8YESt'
AUTH0_BASE_URL = os.getenv('AUTH0_BASE_URL')
AUTH0_AUDIENCE='id_specimen_finder'
SECRET_KEY = 'asdhadksjahdakhdas876986^&%&*^%^A%UADSHADSHJASDGHJGAD'

### END ADDED
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
                Animal.specificepithet.ilike(search)
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
        else:
            form = AnimalForm(request.form, meta={'csrf': False})
            genus = form.genus.data
            specificepithet = form.specificepithet.data

        # Validate all fields
        if form.validate():
                animal = Animal(
                    genus = genus, 
                    specificepithet = specificepithet
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

                # If genus found in the request, change the genus
                if genus is not None:
                    animal.genus = genus
            
                # If specificepithet found in the request, change the specificepithet
                if specificepithet is not None:
                    animal.specificepithet = specificepithet

                # If any one of specificepithet or genus found in the request than update
                if genus is not None or specificepithet is not None:
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
                Institution.street.ilike(search)
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
        else:
            form = InstitutionForm(request.form, meta={'csrf': False})
            name=form.name.data
            street=form.street.data

        # Validate all fields
        if form.validate():
                institution = Institution(
                    name = name, 
                    street = street
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

                # If name found in the request, change the name
                if name is not None:
                    institution.name = name
            
                # If street found in the request, change the street
                if street is not None:
                    institution.street = street

                # If any one of street or name found in the request than update
                if street is not None or name is not None:
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
        specimens = Specimen.query.all()

        if request.headers.get('Content-Type') == 'application/json':
            # If so, return a JSON response
            response = []
            for specimen in specimens:
                response.append(specimen.view())

            return jsonify(
                {
                    "specimens": response,
                    "success": True
                }
            ), 200
        else:
            # Otherwise, render an HTML template
            return render_template(
                'pages/specimens.html', 
                specimens=specimens)







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



    return app


app = create_app()


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)