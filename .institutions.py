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



    return app


app = create_app()


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)