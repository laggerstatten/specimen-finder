import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Institution, Animal

# TODO get tokens

tk_token_sf_admin = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzEyMDAxOTcxLCJleHAiOjE3MTIwODgzNzEsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.BerY2Z75y1PMPQSHXU2H8pVBvexfhcDKvxylhuGQxYxms8SdNIue1NzXvafjb7BIrDcKJlNHE-KR_R07m9Lbqe6ktuczpSZH54EqzHzmiYkxg3KL3UMUsToygg542wqgsthIPXCHwFnkM5B8p-4IFlaNU33LYtqtSiAFwRg5e1xYQAq1mHf3s-em4B32KqnGCFTneY2CDyf_hvpKJ1xGr3eNnS30Ex6ndef7gRolwg-Ri_hUe8jAyC83ylvKysOskJC79LT9lQFYn_xFtr-0H8qzIT0b2IqJGu0cdDhie8Y6I9O6BUpZvTVgjAvmldCU5ehcQqgIy_kTqW-KIPKpTQ'
tk_token_sf_user =   'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzEyMDAxOTcxLCJleHAiOjE3MTIwODgzNzEsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.BerY2Z75y1PMPQSHXU2H8pVBvexfhcDKvxylhuGQxYxms8SdNIue1NzXvafjb7BIrDcKJlNHE-KR_R07m9Lbqe6ktuczpSZH54EqzHzmiYkxg3KL3UMUsToygg542wqgsthIPXCHwFnkM5B8p-4IFlaNU33LYtqtSiAFwRg5e1xYQAq1mHf3s-em4B32KqnGCFTneY2CDyf_hvpKJ1xGr3eNnS30Ex6ndef7gRolwg-Ri_hUe8jAyC83ylvKysOskJC79LT9lQFYn_xFtr-0H8qzIT0b2IqJGu0cdDhie8Y6I9O6BUpZvTVgjAvmldCU5ehcQqgIy_kTqW-KIPKpTQ'
tk_token_sf_editor =   'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzEyMDAxOTcxLCJleHAiOjE3MTIwODgzNzEsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.BerY2Z75y1PMPQSHXU2H8pVBvexfhcDKvxylhuGQxYxms8SdNIue1NzXvafjb7BIrDcKJlNHE-KR_R07m9Lbqe6ktuczpSZH54EqzHzmiYkxg3KL3UMUsToygg542wqgsthIPXCHwFnkM5B8p-4IFlaNU33LYtqtSiAFwRg5e1xYQAq1mHf3s-em4B32KqnGCFTneY2CDyf_hvpKJ1xGr3eNnS30Ex6ndef7gRolwg-Ri_hUe8jAyC83ylvKysOskJC79LT9lQFYn_xFtr-0H8qzIT0b2IqJGu0cdDhie8Y6I9O6BUpZvTVgjAvmldCU5ehcQqgIy_kTqW-KIPKpTQ'


            





class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

        setup_db(self.app)

        self.token_sf_admin = 'Bearer ' + tk_token_sf_admin
        self.token_sf_user = 'Bearer ' + tk_token_sf_user
        self.token_sf_editor = 'Bearer ' + tk_token_sf_editor

        self.headers = {'Content-Type': 'application/json', 'Authorization': self.token_sf_admin}

        self.header_sf_user = {'Content-Type': 'application/json', 'Authorization': self.token_sf_user}

        self.header_sf_editor = {'Content-Type': 'application/json', 'Authorization': self.token_sf_editor}

        self.new_animal = {
            'genus': 'Canis',
            'specificepithet': 'lupus',
            'sciname': 'Canis_lupus',
            'maincommonname': 'Gray Wolf',
            'taxonorder': 'CARNIVORA',
            'biogeographicrealm': 'Nearctic|Palearctic',
            'iucnstatus': 'LC'
        }

        self.new_institution = {
            'name': 'Philadelphia Zoo',
            'street': '3400 W Girard Ave',
            'longitude': -75.194992,
            'latitude': 39.975151,
            'city': 'Philadelphia',
            'state': 'PA'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()



    def tearDown(self):
        """Executed after reach test"""
        pass

#  Animals
#  ----------------------------------------------------------------

## success
    def test_animals(self):
        res = self.client().get(
            '/animals', 
            headers=self.headers
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['animals']))


    def test_animals_sf_user(self):
        res = self.client().get(
            '/animals', 
            headers=self.header_sf_user
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['animals']))


    def test_search_animals(self):
        search_term = 'Equus'

        res = self.client().post(
            '/animals/search',
            headers=self.headers,
            json={'search_term': search_term}
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        response_data = res.get_json()
        self.assertIn('animals', response_data)
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertTrue(any(animal['genus'] == search_term for animal in response_data['animals']['data']))



#  Animals -- Individual Record
#  ----------------------------------------------------------------

    def test_show_animal(self):
        # Create a sample animal for testing
        animal = Animal(
            genus='Canis', 
            specificepithet='lupus',
            sciname= 'Canis_lupus',
            maincommonname= 'Gray Wolf',
            taxonorder= 'CARNIVORA',
            biogeographicrealm= 'Nearctic|Palearctic',
            iucnstatus= 'LC'
            )
                
        animal.insert()
        animal_id = animal.id

        res = self.client().get(
            f'/animals/{animal_id}',
            headers=self.headers
            )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        response_data = res.get_json()
        self.assertIn('animal', response_data)
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['animal']['genus'], animal.genus)
        self.assertEqual(response_data['animal']['specificepithet'], animal.specificepithet)


#  Animals -- Create
#  ----------------------------------------------------------------

## success
    def test_create_animal_form(self):
        res = self.client().get(
            '/animals/create', 
            headers=self.headers
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)


## success
    def test_create_animal_submission(self):
        new_animal = {
            'genus': 'Canis',
            'specificepithet': 'lupus',
            'sciname': 'Canis_lupus',
            'maincommonname': 'Gray Wolf',
            'taxonorder': 'CARNIVORA',
            'biogeographicrealm': 'Nearctic|Palearctic',
            'iucnstatus': 'LC'
        }        
        
        res = self.client().post(
            '/animals/create', 
            headers=self.headers, 
            json=new_animal
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)




#  Animals -- Update
#  ----------------------------------------------------------------

## success
    def test_edit_animal_(self):
        # Create a new animal for testing
        new_animal = Animal(
            genus='Canis', 
            specificepithet='lupus',
            sciname= 'Canis_lupus',
            maincommonname= 'Gray Wolf',
            taxonorder= 'CARNIVORA',
            biogeographicrealm= 'Nearctic|Palearctic',
            iucnstatus= 'LC'
            )
    
        new_animal.insert()
        animal_id = new_animal.id

        res = self.client().get(
            f'/animals/{new_animal.id}/edit', 
            headers=self.headers
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        response_data = res.get_json()
        self.assertIn('animal', response_data)
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['animal']['genus'], new_animal.genus)
        self.assertEqual(response_data['animal']['specificepithet'], new_animal.specificepithet)


## success
    def test_edit_animal_submission(self):
        # Create a new animal for testing
        new_animal = Animal(
            genus='Canis', 
            specificepithet='lupus',
            sciname= 'Canis_lupus',
            maincommonname= 'Gray Wolf',
            taxonorder= 'CARNIVORA',
            biogeographicrealm= 'Nearctic|Palearctic',
            iucnstatus= 'LC'
            )        
        
        new_animal.insert()

        updated_data = {
            'genus': 'Kanis',
            'specificepithet': 'loopus'
        }
        res = self.client().patch(
            f'/animals/{new_animal.id}/edit', 
            headers=self.headers, 
            json=updated_data
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        updated_animal = Animal.query.get(new_animal.id)
        self.assertEqual(updated_animal.genus, updated_data['genus'])
        self.assertEqual(updated_animal.specificepithet, updated_data['specificepithet'])
        self.assertIn('animals', res.json)
        self.assertIn('success', res.json)
        self.assertTrue(res.json['success'])




#  Animals -- Delete
#  ----------------------------------------------------------------

## success
    def test_delete_animal(self):
        res = self.client().delete(
            '/animals/7', 
            headers=self.headers
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


#  Institutions
#  ----------------------------------------------------------------

## success
    def test_institutions(self):
        res = self.client().get(
            '/institutions',
            headers=self.headers
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['institutions']))
        
        
    def test_institutions_sf_user(self):
        res = self.client().get(
            '/institutions', 
            headers=self.header_sf_user
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['institutions']))


#  Institutions -- Individual Record
#  ----------------------------------------------------------------

## success
    def test_show_institution(self):
        # Create a sample institution for testing
        institution = Institution(
            name='Philadelphia Zoo', 
            street='3400 W Girard Ave',
            longitude=-75.194992,
            latitude=39.975151,            
            city='Philadelphia',
            state='PA'
            )
        institution.insert()
        institution_id = institution.id

        res = self.client().get(
            f'/institutions/{institution_id}',
            headers=self.headers
            )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        response_data = res.get_json()
        self.assertIn('institution', response_data)
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['institution']['name'], institution.name)
        self.assertEqual(response_data['institution']['street'], institution.street)


#  Institutions -- Create
#  ----------------------------------------------------------------

## success
    def test_create_institution_form(self):
        res = self.client().get(
            '/institutions/create', 
            headers=self.headers
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)


## success
    def test_create_institution_submission(self):
        res = self.client().post(
            '/institutions/create', 
            headers=self.headers, 
            json=self.new_institution
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


#  Institutions -- Update
#  ----------------------------------------------------------------

## success
    def test_edit_institution_(self):
        # Create a new institution for testing
        new_institution = Institution(
            name='Philadelphia Zoo', 
            street='3400 W Girard Ave',
            longitude=-75.194992,
            latitude=39.975151,            
            city='Philadelphia',
            state='PA'
            )
        new_institution.insert()
        institution_id = new_institution.id

        res = self.client().get(
            f'/institutions/{new_institution.id}/edit', 
            headers=self.headers
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        response_data = res.get_json()
        self.assertIn('institution', response_data)
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['institution']['name'], new_institution.name)
        self.assertEqual(response_data['institution']['street'], new_institution.street)
        

## success
    def test_edit_institution_submission(self):
        # Create a new institution for testing
        new_institution = Institution(
            name='Philadelphia Zoo', 
            street='3400 W Girard Ave',
            longitude=-75.194992,
            latitude=39.975151,            
            city='Philadelphia',
            state='PA'
        )
        new_institution.insert()

        updated_data = {
            'name': 'Philly Zoo',
            'street': '3400 W Girard Ave #1'
        }
        
        res = self.client().patch(
            f'/institutions/{new_institution.id}/edit', 
            headers=self.headers, 
            json=updated_data
        )
        print("Response:", res.data)
        self.assertEqual(res.status_code, 200)
        updated_institution = Institution.query.get(new_institution.id)
        self.assertEqual(updated_institution.name, updated_data['name'])
        self.assertEqual(updated_institution.street, updated_data['street'])
        self.assertIn('institutions', res.json)
        self.assertIn('success', res.json)
        self.assertTrue(res.json['success'])


#  Institutions -- Delete
#  ----------------------------------------------------------------

## success
    def test_delete_institution(self):
        res = self.client().delete(
            '/institutions/7', 
            headers=self.headers
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()