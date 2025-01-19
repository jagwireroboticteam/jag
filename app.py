from flask import Flask, render_template

app = Flask(__name__)

# Data to simulate an alumni database
alumni_data = [
    {"name": "Alice Johnson", "year": 2020, "college": "MIT", "major": "Mechanical Engineering"},
    {"name": "Bob Smith", "year": 2019, "college": "Stanford", "major": "Computer Science"},
    {"name": "Carol Lee", "year": 2021, "college": "University of Michigan", "major": "Robotics Engineering"},
]

@app.route("/")
def home():
    return render_template("alumni.html", alumni=alumni_data)

if __name__ == "__main__":
    app.run(debug=True)
