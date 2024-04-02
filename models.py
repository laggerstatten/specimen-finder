import os
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Boolean, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from sqlalchemy.orm import relationship, sessionmaker
import json, sys
from datetime import datetime

# need to export databse url first
database_path = os.getenv('DATABASE_URL')

db = SQLAlchemy()

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()



class Specimen(db.Model):
    __tablename__ = 'Specimen'
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer,db.ForeignKey('Animal.id'), nullable=False)
    institution_id = db.Column(db.Integer,db.ForeignKey('Institution.id') ,nullable=False)
    sightingdate = db.Column(db.DateTime)

    '''animal = db.relationship('Animal', backref='specimens')'''
    '''institution = db.relationship('Institution', backref='specimens')'''

    def view(self):
        return{
            'id': self.id,
            'animal_id': self.animal_id,
            'institution_id': self.institution_id,
            'sightingdate': self.sightingdate
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()


    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(Specimen.view(self))





class Animal(db.Model):
    __tablename__ = 'Animal'
    id = db.Column(db.Integer, primary_key=True)
    genus = db.Column(db.String(255))
    specificepithet = db.Column(db.String(255))
    sciname = db.Column(db.String(255))
    maincommonname = db.Column(db.String(255))
    taxonorder = db.Column(db.String(255))
    biogeographicrealm = db.Column(db.String(255))
    iucnstatus = db.Column(db.String(255))
    
    specimens = db.relationship('Specimen', backref='animal', lazy=True)

    def view(self):
        return{
            'id': self.id,
            'genus': self.genus,
            'specificepithet': self.specificepithet,
            'sciname': self.sciname,
            'maincommonname': self.maincommonname,
            'taxonorder': self.taxonorder,
            'biogeographicrealm': self.biogeographicrealm,
            'iucnstatus': self.iucnstatus
        }

    '''
    insert()
        inserts a new model into a database
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(Animal.view(self))


class Institution(db.Model):
    __tablename__ = 'Institution'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    street = db.Column(db.String(120))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    city = db.Column(db.String(120))
    state = db.Column(db.String(2))    
    specimens = db.relationship('Specimen', backref='institution', lazy=True)

    def view(self):
        return{
            'id': self.id,
            'name': self.name,
            'street': self.street,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'city': self.city,
            'state': self.state
        }

    '''
    insert()
        inserts a new model into a database
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(Institution.view(self))
    
    
