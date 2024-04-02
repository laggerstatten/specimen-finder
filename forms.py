from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL, Email

class SpecimenForm(Form):
    animal_id = IntegerField(
        'Animal ID', validators=[DataRequired()]
    )
    institution_id = IntegerField(
        'Institution ID', validators=[DataRequired()]
    )
    sightingdate = DateTimeField(
        'Sighting Date',
        validators=[DataRequired()],
        default=datetime.today()
    )


class AnimalForm(Form):
    genus = StringField(
        'Genus', validators=[DataRequired()]
    )
    specificepithet = StringField(
        'Species', validators=[DataRequired()]
    )
    sciname = StringField(
        'Sci Name'
    )
    maincommonname = StringField(
        'Common Name'
    )
    taxonorder = StringField(
        'Order'
    )
    biogeographicrealm = StringField(
        'Biogeographic Realm'
    )
    iucnstatus = StringField(
        'IUCN Status'
    )






class InstitutionForm(Form):
    name = StringField(
        'Name', validators=[DataRequired()]
    )
    street = StringField(
        'Address', validators=[DataRequired()]
    )
    longitude = StringField(
        'Longitude'
    )
    latitude = StringField(
        'Latitude'
    )
    city = StringField(
        'City'
    )
    state = StringField(
        'State'
    )




