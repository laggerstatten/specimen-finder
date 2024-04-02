import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Institution, Animal


tk_token_sf_admin = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzExODk0Nzk0LCJleHAiOjE3MTE5ODExOTQsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.UepKuvRTd1qNpMMWfEFgBBGvro8RCRs2lGHbhUzcBVkMYCtRSZRKgULp7QTuCYm4cNLFu5GIvmniypRiOAYv5I6r2ffqSBRbEtZ-pk_0Uvm8yvTXs5qnI25PxNYAhinEde6vRy86451ThjtuswYm6DM5V4xlQlJZkZR2scaLnnlTm_Iy-UulfvcoJkYoUp12skHmu4qZBbEWEdAR_GFodm3FBe2Lwd6-uwDzr3A1XGmtXD5DgPsY0ErN96-eiMpyRLcjfJ376lcVD8dEnWsHkmjWVLSgjH1ctlFaHSWOVOdmVo5KgpfRwGxGkbFdKI_u5j57tesn1wKjrosrPa_syA'
tk_token_sf_user =   'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzExODk0Nzk0LCJleHAiOjE3MTE5ODExOTQsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.UepKuvRTd1qNpMMWfEFgBBGvro8RCRs2lGHbhUzcBVkMYCtRSZRKgULp7QTuCYm4cNLFu5GIvmniypRiOAYv5I6r2ffqSBRbEtZ-pk_0Uvm8yvTXs5qnI25PxNYAhinEde6vRy86451ThjtuswYm6DM5V4xlQlJZkZR2scaLnnlTm_Iy-UulfvcoJkYoUp12skHmu4qZBbEWEdAR_GFodm3FBe2Lwd6-uwDzr3A1XGmtXD5DgPsY0ErN96-eiMpyRLcjfJ376lcVD8dEnWsHkmjWVLSgjH1ctlFaHSWOVOdmVo5KgpfRwGxGkbFdKI_u5j57tesn1wKjrosrPa_syA'
tk_token_sf_editor =   'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBFM3dkeEhCbUJyeF8wbzhZYkpQZCJ9.eyJpc3MiOiJodHRwczovL2Rldi0yYm0wb2p2cjRzZmVsanB0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWZmMzA2NmYyZTg2Njg0MTg3ZmJlODQiLCJhdWQiOlsiaWRfc3BlY2ltZW5fZmluZGVyIiwiaHR0cHM6Ly9kZXYtMmJtMG9qdnI0c2ZlbGpwdC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzExODk0Nzk0LCJleHAiOjE3MTE5ODExOTQsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiI2c0xhYkdlQjVuZ0JQbmk5cXI3TXFUbllWUG0wVk9LRiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphbmltYWxzIiwiY3JlYXRlOmluc3RpdHV0aW9ucyIsImNyZWF0ZTpzcGVjaW1lbnMiLCJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOmFuaW1hbHMiLCJkZWxldGU6aW5zdGl0dXRpb25zIiwiZGVsZXRlOm1vdmllcyIsImRlbGV0ZTpzcGVjaW1lbnMiLCJlZGl0OmFuaW1hbHMiLCJlZGl0Omluc3RpdHV0aW9ucyIsImVkaXQ6c3BlY2ltZW5zIiwiZ2V0OmFjdG9yZm9ybSIsImdldDphY3RvcnMiLCJnZXQ6YW5pbWFscyIsImdldDpjYXN0Zm9ybSIsImdldDppbnN0aXR1dGlvbnMiLCJnZXQ6bW92aWVmb3JtIiwiZ2V0Om1vdmllcyIsImdldDpzcGVjaW1lbnMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6YW5pbWFscyIsInBvc3Q6Y2FzdCIsInBvc3Q6aW5zdGl0dXRpb25zIiwicG9zdDptb3ZpZXMiLCJwb3N0OnNwZWNpbWVucyJdfQ.UepKuvRTd1qNpMMWfEFgBBGvro8RCRs2lGHbhUzcBVkMYCtRSZRKgULp7QTuCYm4cNLFu5GIvmniypRiOAYv5I6r2ffqSBRbEtZ-pk_0Uvm8yvTXs5qnI25PxNYAhinEde6vRy86451ThjtuswYm6DM5V4xlQlJZkZR2scaLnnlTm_Iy-UulfvcoJkYoUp12skHmu4qZBbEWEdAR_GFodm3FBe2Lwd6-uwDzr3A1XGmtXD5DgPsY0ErN96-eiMpyRLcjfJ376lcVD8dEnWsHkmjWVLSgjH1ctlFaHSWOVOdmVo5KgpfRwGxGkbFdKI_u5j57tesn1wKjrosrPa_syA'


            





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



#  Animals -- Individual Record
#  ----------------------------------------------------------------



#  Animals -- Create
#  ----------------------------------------------------------------

    def test_create_animal_submission_422(self):
        bad_animal = {
            'genus': '',
            'specificepithet': ''
        }
        res = self.client().post(
            '/animals/create', 
            headers=self.headers, 
            json=bad_animal
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)




#  Animals -- Update
#  ----------------------------------------------------------------
    def test_edit_animal_submission_404(self):
        updated_data = {
            'genus': 'Updated Genus',
            'specificepithet': 'Updated Species'
        }
        res = self.client().patch(
            f'/animals/100/edit', 
            headers=self.headers, 
            json=updated_data
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_edit_animal_submission_403(self):
        updated_data = {
            'genus': 'Updated Genus',
            'specificepithet': 'Updated Species'
        }
        res = self.client().patch(
            f'/animals/1/edit',             
            headers=self.header_sf_user, 
            json=self.updated_data
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)




#  Animals -- Delete
#  ----------------------------------------------------------------

    def test_delete_animal_404(self):
        res = self.client().delete(
            '/animals/700', 
            headers=self.headers
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "Not Found")


    def test_delete_animal_403(self):
        res = self.client().delete(
            "/animals/1", 
            headers=self.header_sf_editor
        )
        print("Response:", res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)


#  Institutions
#  ----------------------------------------------------------------



#  Institutions -- Individual Record
#  ----------------------------------------------------------------


#  Institutions -- Create
#  ----------------------------------------------------------------



#  Institutions -- Update
#  ----------------------------------------------------------------




#  Institutions -- Delete
#  ----------------------------------------------------------------



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()