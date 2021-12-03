from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# implement database model classes
association_table = db.Table("association", db.Model.metadata,
   db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
   db.Column("category_id", db.Integer, db.ForeignKey("category.id"))
)


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String, nullable = False)
    date = db.Column(db.String, nullable = False)
    location = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    done = db.Column(db.Boolean, nullable = False)
    tasks = db.relationship("Task", cascade = "delete")
    categories = db.relationship("Category", secondary=association_table, back_populates="events")

    def __init__(self, **kwargs):
        self.description = kwargs.get('description')
        self.date = (kwargs.get('date'))
        self.location = kwargs.get('location')
        self.name = kwargs.get('name')
        self.done = kwargs.get('done')

    def serialize(self):
        return {
            "id": self.id,
            "description" : self.description,
            "date" : self.date,
            "location" : self.location,
            "name" : self.name,
            "done" : self.done,
            "tasks" : [t.serialize() for t in self.tasks],
            "categories": [c.sub_serialize() for c in self.categories]
        }

    def sub_serialize(self):
        return{
            "id": self.id,
            "description": self.description,
            "date" : self.date,
            "location" : self.location,
            "name" : self.name,
            "done": self.done,
            #"tasks": [s.serialize() for s in self.tasks],
        }

class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String, nullable = False)
    done = db.Column(db.Boolean, nullable = False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable = False)

    def __init__(self, **kwargs):
        self.description = kwargs.get("description")
        self.done = kwargs.get("done")
        self.event_id = kwargs.get("event_id")

    def serialize(self):
        return {
            "id": self.id,
            "description" : self.description,
            "done" : self.done,
            "event_id" : self.event_id,
        }

class Category(db.Model):
   __tablename__ = "category"
   id = db.Column(db.Integer, primary_key=True)
   description = db.Column(db.String, nullable=False)
   type = db.Column(db.String, nullable=False)
   events = db.relationship("Event", secondary=association_table, back_populates='categories')

   def serialize(self):
       return {
           "id": self.id,
           "description": self.description,
           "type": self.type,
       }

   def sub_serialize(self):
       return {
           "type": self.type
       }
