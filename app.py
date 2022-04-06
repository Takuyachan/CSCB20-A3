from unittest import result
from flask import Flask, render_template, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unidata.db'
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'Person'
    username = db.Column(db.String(20), primary_key = True, nullable = False, unique = False)
    firstname = db.Column(db.String(20), nullable = False)
    lastname = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    role = db.Column(db.String(15), nullable = False)
    #role is either Student or Instructor

    def __repr__(self):
        return "{self.firstname} {self.lastname}"

class Courses(db.Model):
    __tablename__ = 'Courses'
    username = db.Column(db.String(20), db.ForeignKey(Person.username), nullable = False, primary_key = True)
    course = db.Column(db.String(10), nullable = False, primary_key = True)


class Grades(db.Model):
    __tablename__ = 'Grades'
    username = db.Column(db.Integer, db.ForeignKey(Person.username), nullable = False, primary_key = True)
    course = db.Column(db.String(10), nullable = False, primary_key = True)
    assignment = db.Column(db.String(50), nullable = False, unique = True, primary_key = True)
    grade = db.Column(db.Float, nullable = False)
    outof = db.Column(db.Integer, nullable = False)


class Feedback(db.Model):
    __tablename__ = 'Feedback'
    instructorname = db.Column(db.String(30), nullable = False, primary_key = True)
    coursecode = db.Column(db.String(10), nullable = False, primary_key = True)
    time = db.Column(db.String(20), nullable = False, default = datetime.utcnow)
    feedback_a = db.Column(db.String(500), nullable = False, primary_key = True)
    feedback_b = db.Column(db.String(500), nullable = False)
    feedback_c = db.Column(db.String(500), nullable = False)
    feedback_d = db.Column(db.String(500), nullable = False)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/piazza')
def piazza():
    return render_template("Piazza.html")

@app.route('/markus')
def markus():
    return render_template("Markus.html")

@app.route('/assignments')
def assignments():
    return render_template("Assignments.html")

@app.route('/grades')
def grades():
    return render_template("Grades.html")

@app.route('/anonfeedback', methods = ['GET', 'POST'])
def anonfeedback():
    if(session['role'] == "Student"):
        if (request.method == "POST"):
            feedbacks = (
                request.form['instructorname'],
                request.form['coursecode'],
                request.form['feedback_a'],
                request.form['feedback_b'],
                request.form['feedback_c'],
                request.form['feedback_d']
            )

            query_course_result = db.session.query(Courses.course).filter(Courses.username == feedbacks[0])
            for result in query_course_result:
                if (feedbacks[1] == result[0]):
                    enteredfeedback = Feedback(instructorname = feedbacks[0], coursecode = feedbacks[1], feedback_a = feedbacks[2], 
                    feedback_b = feedbacks[3], feedback_c = feedbacks[3], feedback_d = feedbacks[4])
                    db.session.add(enteredfeedback)
                    db.session.commit()

                    query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
                    instructors = {}
                    for row in query_instructor_result:
                        instructors[row[0]] = row[1] + " " + row[2]
                    flash('Feedback sent!')
                    return render_template("AnonFeedback.html", instructors = instructors)

            query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
            instructors = {}
            for row in query_instructor_result:
                instructors[row[0]] = row[1] + " " + row[2]
            flash('The instructor does not teach the course you have entered. Please check again and submit.')
            return render_template("AnonFeedback.html", instructors = instructors)
        
        else:
            query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
            instructors = {}
            for row in query_instructor_result:
                instructors[row[0]] = row[1] + " " + row[2]
            return render_template("AnonFeedback.html", instructors = instructors)
    
    else:
        query_course_result = db.session.query(Courses.course).filter(Courses.username == session['name'])
        query_feedback_result = db.session.query(Feedback.coursecode, Feedback.time, Feedback.feedback_a, Feedback.feedback_b,
        Feedback.feedback_c, Feedback.feedback_d)
        courselist = []
        for one in query_course_result:
            courselist.append(one[0])
        resultfeedback = []
        for a_feedback in query_feedback_result:
            if(a_feedback[0] in courselist):
                chosenfeedback = []
                chosenfeedback.append(a_feedback[0])
                chosenfeedback.append(a_feedback[1])
                chosenfeedback.append(a_feedback[2])
                chosenfeedback.append(a_feedback[3])
                chosenfeedback.append(a_feedback[4])
                chosenfeedback.append(a_feedback[5])
                resultfeedback.append(chosenfeedback)
        return render_template("AnonFeedbackInstructor.html", resultfeedback = resultfeedback)


# @app.route('/anonfeedback_instructor')
# def anonfeedback_instructor():
#     query_course_result = db.session.query(Courses.course).filter(Courses.username == "Prof1")
#     query_feedback_result = db.session.query(Feedback.coursecode, Feedback.time, Feedback.feedback_a, Feedback.feedback_b,
#     Feedback.feedback_c, Feedback.feedback_d)
#     courselist = []
#     for one in query_course_result:
#         courselist.append(one[0])
#     resultfeedback = []
#     for a_feedback in query_feedback_result:
#         if(a_feedback[0] in courselist):
#             chosenfeedback = []
#             chosenfeedback.append(a_feedback[0])
#             chosenfeedback.append(a_feedback[1])
#             chosenfeedback.append(a_feedback[2])
#             chosenfeedback.append(a_feedback[3])
#             chosenfeedback.append(a_feedback[4])
#             chosenfeedback.append(a_feedback[5])
#             resultfeedback.append(chosenfeedback)
#     return render_template("AnonFeedbackInstructor.html", resultfeedback = resultfeedback)


# @app.route('/viewregraderequest')
# def viewregraderequest():
#     query_regrade_result = db.session.query(Grades.course, Grades.assignment, Grades.username, Grades.regradecomment).filter(Grades.regrade != NULL)
#     name_and_regrade = []
#     for onerequest in query_regrade_result:
#         studentnames = db.session.query(Person.firstname, Person.lastname).filter(Person.username == onerequest[2])
#         for student in studentnames:
#             singlename_regrade = []
#             fullname = student[0] + " " + student[1]
#             singlename_regrade.append(onerequest[0])
#             singlename_regrade.append(onerequest[1])
#             singlename_regrade.append(fullname)
#             singlename_regrade.append(onerequest[3])
#             name_and_regrade.append(singlename_regrade)
#     return render_template("ViewRegrade.html", name_and_regrade = name_and_regrade)

@app.route('/syllabus')
def syllabus():
    return render_template("Syllabus.html")


@app.route('/lectures')
def lectures():
    return render_template("Lectures.html")

@app.route('/labs')
def labs():
    return render_template("Labs.html")

@app.route('/resources')
def resources():
    return render_template("Resources.html")

@app.route('/courseteam')
def courseteam():
    return render_template("CourseTeam.html")



if __name__ == "__main__":
    app.run(debug=True)

