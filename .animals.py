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



    return app


app = create_app()


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)