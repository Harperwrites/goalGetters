from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------
# App Setup chatGPT help and tutoring
# --------------------------
app = Flask(__name__)
app.secret_key = "knowledgeisthekey"  # Needed for sessions

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kidsDash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------
# Models
# --------------------------
class User(db.Model):
    __tablename__ = "users"
    child_id = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    goals = db.relationship("Goal", backref="user", lazy=True)
    children = db.relationship("Child", backref="user", lazy=True)

class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    frequency = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    earned_stars = db.Column(db.Integer, default=0)
    child_id = db.Column(db.String(50), db.ForeignKey("users.child_id"))

class Child(db.Model):
    __tablename__ = "child"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    child_id = db.Column(db.String(50), db.ForeignKey("users.child_id"))

# --------------------------
# Create all tables
# --------------------------
with app.app_context():
    db.create_all()

# --------------------------
# Routes
# --------------------------
@app.route("/")
def index():
    if "child_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        child_id = request.form["child_id"]
        password = request.form["password"]

        user = User.query.filter_by(child_id=child_id).first()
        if user and check_password_hash(user.password_hash, password):
            session["child_id"] = user.child_id
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        child_id = request.form["child_id"]
        password = request.form["password"]
        hashed = generate_password_hash(password)

        if User.query.filter_by(child_id=child_id).first():
            return "Username already exists!"

        new_user = User(child_id=child_id, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "child_id" not in session:
        return redirect(url_for("login"))

    child_id = session["child_id"]

    incomplete_goals = Goal.query.filter_by(child_id=child_id, completed=False).order_by(Goal.due_date).all()
    all_goals = Goal.query.filter_by(child_id=child_id).order_by(Goal.due_date).all()
    total_stars = sum(goal.earned_stars for goal in all_goals)

    return render_template(
        "dashboard.html",
        goals=incomplete_goals,
        all_goals=all_goals,
        points_earned=total_stars
    )

@app.route("/new_goal", methods=["POST"])
def new_goal():
    if "child_id" not in session:
        return redirect(url_for("login"))

    child_id = session["child_id"]
    title = request.form.get("title")
    frequency = request.form.get("frequency") or "one-time"
    due_date_str = request.form.get("due_date")
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None

    goal = Goal(
        title=title,
        frequency=frequency,
        due_date=due_date,
        completed=False,
        child_id=child_id
    )
    db.session.add(goal)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/complete_goal/<int:goal_id>", methods=["POST"])
def complete_goal(goal_id):
    if "child_id" not in session:
        return redirect(url_for("login"))

    goal = Goal.query.get_or_404(goal_id)

    # Ensure the goal belongs to the logged-in child
    if goal.child_id != session["child_id"]:
        return "Unauthorized", 403

    goal.completed = True
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("child_id", None)  # remove user session
    return redirect(url_for("login"))



# --------------------------
# Run app
# --------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
