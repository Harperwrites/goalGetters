from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Child(db.Model):
    __tablename__ = "child"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Relationship (child → goals)
    goals = db.relationship("Goal", backref="child", lazy=True)


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    frequency = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    earned_stars = db.Column(db.Integer, default=0)

    child_id = db.Column(db.Integer, db.ForeignKey("child.id"))
