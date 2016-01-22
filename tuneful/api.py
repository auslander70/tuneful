import os.path
import json

from flask import request, redirect, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path


@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
  songs = session.query(models.Song)
  
  data = json.dumps([song.as_dictionary() for song in songs])
  return Response(data, 200, mimetype="application/json")
  
@app.route("/api/songs", methods=["POST"])
@decorators.require("application/json")
@decorators.accept("application/json")
def songs_post():
  data = request.json
  file_id = data["file"]["id"]
  file_obj = session.query(models.File).get(file_id)
  if not file_obj:
    message = "Could not find file with id {}".format(file_id)
    data = json.dumps({"message": message})
    return Response(data, 404, mimetype="application/json")
  else:     
    song = models.Song()
    file_obj.song_id = song.id
    session.add_all([song, file_obj])
    session.commit()
    return redirect(url_for("songs_get"))

    