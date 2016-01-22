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

@app.route("/api/songs/<int:song_id>", methods=["PUT"])
@decorators.accept("application/json")
def song_update(song_id):
    """ Update Song """ 
    data = request.json
    # Get the song from the database
    song = session.query(models.Song).get(song_id)

    if not song:
        message = "Could not find song with id {}".format(song_id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    else:
        data["id"] = song_id
        song.id = data["id"]
        file = session.query(models.File).get(data["file"]["id"])
        song.file = file
        session.commit()
        headers = {"Location": url_for("songs_get")}
        return Response(data, 201, headers=headers,
                    mimetype="application/json")   
                    
@app.route("/api/songs", methods=["DELETE"])
@decorators.accept("application/json")
def delete_song():
  data = request.json
  song_id = data["id"]
  song = session.query(models.Song).get(song_id)
  if not song:
    message = "Could not find song with id {}".format(song_id)
    data = json.dumps({"message": message})
    return Response(data, 404, mimetype="application/json")
  else:     
    session.delete(song)
    session.commit()
    return redirect(url_for("songs_get"))

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

"""
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
    
"""