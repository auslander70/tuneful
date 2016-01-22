import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def test_get_empty_songlist(self):
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, [])

    def test_post_song_successful(self):
        file = models.File(filename="Soulful Strut.mp3")
        session.add(file)
        session.commit()
        data = {
            "file": {
                "id": file.id
            }
        }
        
        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.mimetype, "text/html")

    def test_post_update_song_successful(self):
        fileobj1 = models.File(filename="Soulful Strut.mp3")
        fileobj2 = models.File(filename="Baker Street.mp3")
        song = models.Song()
        fileobj1.song_id = song.id
        session.add_all([fileobj1, fileobj2, song])
        session.commit()
        data = {
            "file": {
                "id": fileobj2.id
            }
        }
        
        response = self.client.put("/api/songs/{}".format(song.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

    def test_post_update_song_failure(self):
       
        data = {
            "file": {
                "id": -1
            }
        }
        
        response = self.client.put("/api/songs/-1",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")
        
    def test_post_song_fail(self):
        file_id = -1
        data = {
            "file": {
                "id": file_id
            }
        }
        
        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")
        
    def test_delete_success(self):
        """ Test successful song deletion """
        song = models.Song()
        session.add(song)
        session.commit()
        
        data = {
            "id": song.id
        }
        
        response = self.client.delete("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


