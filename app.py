import json
import datetime
import os

from db import Category
from db import Task
from db import db
from flask import Flask
from db import Event
from flask import request
import requests


# define db filename
db_filename = "events.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


# -- EVENTS ROUTES ------------------------------------------------------

@app.route("/")
@app.route("/events/")
def get_events():
    return success_response(
        {"events": [e.serialize() for e in Event.query.all()]}
    )

@app.route("/events/", methods=["POST"])
def create_event():
    body = json.loads(request.data)
    #date = body.get("date")
    #date = datetime.datetime.strptime(date, "%m/%d/%Y")
    #date1 = date.date()
    new_event = Event(description = body.get("description"), date = body.get("date"), location = body.get("location"), name = body.get("name"), done = body.get("done"))
    if Event.description is None:
        return failure_response("Description not found!", 400)
    if Event.date is None:
        return failure_response("Date not found!", 400)
    if Event.location is None:
        return failure_response("Location not found!", 400)
    if Event.name is None:
        return failure_response("Name not found!", 400)
    if Event.done is None:
        return failure_response("Done not found!", 400)
    db.session.add(new_event)
    db.session.commit()
    return success_response(new_event.serialize(), 201)

@app.route("/events/<int:event_id>/", methods=["POST"])
def update_event(event_id):
    body = json.loads(request.data)
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not Found")
    event.description = body.get("description", event.description)
    event.date = body.get("date", event.date)
    event.location = body.get("location", event.location)
    event.name = body.get("name", event.name)
    event.done = body.get("done", event.done)
    if Event.description is None:
        return failure_response("Description not found!", 400)
    if Event.date is None:
        return failure_response("Date not found!", 400)
    if Event.location is None:
        return failure_response("Location not found!", 400)
    if Event.name is None:
        return failure_response("Name not found!", 400)
    if Event.done is None:
        return failure_response("Done not found!", 400)
    db.session.commit()
    return success_response(event.serialize(), 201)

@app.route("/events/<int:event_id>/", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not Found")
    db.session.delete(event)
    db.session.commit()
    return success_response(event.serialize(), 201)

@app.route("/events/<int:event_id>/")
def get_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not Found")
    return success_response(event.serialize(), 201)

#-- TASK ROUTES
@app.route("/events/<int:event_id>/tasks/", methods=["GET"])
def get_tasks(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not found!")
    task = event.serialize()
    return success_response(task["tasks"])

@app.route("/events/<int:event_id>/tasks/", methods=["POST"])
def create_task(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not found!")
    body = json.loads(request.data)
    new_task = Task(description = body.get('description'),done = body.get('done'), event_id=event_id)
    if Task.description is None:
        return failure_response("Description not found!", 400)
    if Task.done is None:
        return failure_response("Done not found!", 400)
    db.session.add(new_task)
    db.session.commit()
    return success_response(new_task.serialize())

@app.route("/events/<int:event_id>/tasks/<int:task_id>/", methods=["POST"])
def update_task(event_id, task_id):
   task = Task.query.filter_by(id=task_id).first()

   if task is None:
       return failure_response("Task not found!")

   body = json.loads(request.data)
   task.description = body.get('description', task.description)
   task.done = body.get('done', task.done)
   if Task.description is None:
       return failure_response("Description not found!", 400)
   if Task.done is None:
       return failure_response("Done not found!", 400)
   db.session.commit()
   return success_response(task.serialize())

@app.route("/events/<int:event_id>/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(event_id, task_id):
   task = Task.query.filter_by(id=task_id).first()
   if task is None:
       return failure_response("Task not found!")
   db.session.delete(task)
   db.session.commit()
   return success_response(task.serialize())

@app.route("/events/<int:event_id>/category/", methods=["POST"])
def assign_category(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return failure_response("Event not found!")
    body = json.loads(request.data)
    description = body.get("description")
    type = body.get("type")
    if description is None:
       return failure_response("Description not found!", 400)
    if done is None:
       return failure_response("Done not found!", 400)
    category = Category.query.filter_by(description = description).first()
    if(category is None):
        category = Category(description=description,type = type)
    event.categories.append(category)
    db.session.commit()
    return success_response(event.serialize())

# -- JOKE OF THE DAY ROUTE (EXTERNAL API) --------------------------------------
@app.route("/joke/")
def get_jok():
    url =  "https://icanhazdadjoke.com/"
    response = requests.get(url, headers = {"Accept": "application/json"})
    data = response.json()
    return success_response(data["joke"], 201)


if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
