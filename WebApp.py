from flask import Flask, request, jsonify, render_template, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'THIS IS MY SECRET KEY FOR ENCRYPTION'

# Database connection
def connect_to_database():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="", # database username
        password="", #database password
        database="CSIT355"
    )

def initialize_database():
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        with open('static/sql/init.db','r') as file:
            statement = file.read()
        for query in statement.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
        print("Database initialized...")
    except FileNotFoundError:
        print(f"Error: File 'init.sql' not found.")
    except mysql.connector.Error as e:
        print(f"Error executing SQL query: {e}")
    finally:
        cursor.close()

@app.after_request
def NoCache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_database()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM students WHERE email = %s"
        cursor.execute(query, (email,))
        student = cursor.fetchone()
        cursor.close()
        connection.close()

        if student and check_password_hash(student['password'], password):
            session['student_id'] = student['student_id']
            session['student_name'] = student['sname']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid Email or Password")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        major = request.form['major']
        year_of_enrollment = request.form['year_of_enrollment']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        connection = connect_to_database()
        cursor = connection.cursor()
        query = """
            INSERT INTO students (sname, email, major, enrollment_year, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (full_name, email, major, year_of_enrollment, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/login')
    return render_template('register_student.html')    

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'student_id' not in session:
        return redirect('/login')
    
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    student_id = session['student_id']

    query = "SELECT student_id, sname FROM students WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    if student:
        return render_template('dashboard.html', student=student)
    else:
        return redirect('/login')

@app.route('/enroll', methods =['POST'])
def enroll():
    if 'student_id' not in session:
        return redirect('/login')
    student_id = session['student_id']
    course_id = request.form['course_id']
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)

    prerequ_query = """ SELECT prerequisite_course_id
                        FROM prerequisites
                        WHERE course_id = %s AND prerequisite_course_id 
                        NOT IN (SELECT course_id
                                FROM enrollments
                                WHERE student_id = %s);"""
    cursor.execute(prerequ_query, (course_id, student_id))
    if cursor.fetchall():
        cursor.close()
        connection.close()
        flash('You do not meet all the prerequisites for this course.', 'error')
        return redirect('/dashboard')

    query = """ SELECT * 
                FROM enrollments
                WHERE student_id = %s AND course_id = %s; """
    cursor.execute(query, (student_id, course_id))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        flash('You are already enrolled in this course.', 'error')
        return redirect('/dashboard')                 
    
    schedule_conf_query = """  SELECT  e.course_id AS conflicting_course_id, s1.meeting_day, s1.start_time, s1.end_time
                                    FROM enrollments e
                                    JOIN schedule s1 ON e.course_id = s1.course_id
                                    JOIN schedule s2 ON s2.course_id = %s
                                    WHERE e.student_id = %s 
                                    AND ((s1.meeting_day = s2.meeting_day) 
                                    AND ((s1.start_time < s2.end_time 
                                    AND s1.end_time > s2.start_time))); """
    cursor.execute(schedule_conf_query, (course_id, student_id))
    if cursor.fetchall():
        cursor.close()
        connection.close()
        flash('This course conflicts with your current schedule.', 'error')
        return redirect('/dashboard')

    query = "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s);"
    cursor.execute(query,(student_id, course_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Enrollment successful!', 'success')
    return redirect('/dashboard')

@app.route('/view_classes', methods=['GET'])
def view_classes():
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    query = """ SELECT c.course_id, CONCAT(c.course_name, "  ", c.description) AS course, p.pname, c.capacity, c.credits
                FROM courses c, professors p
                Where c.course_id and c.professor_id = p.professor_id;"""
    cursor.execute(query)
    classes = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(classes)

@app.route('/schedule', methods=['GET'])
def view_schedule():
    if 'student_id' not in session:
        return redirect('login')
    student_id = session['student_id']

    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    
    query = """ SELECT c.course_id, CONCAT(c.course_name, "  ", c.description) AS course, 
                GROUP_CONCAT(s.meeting_day ORDER BY s.meeting_day SEPARATOR ', ') AS days,
                TIME_FORMAT(s.start_time, '%H:%i') AS start_time,
                TIME_FORMAT(s.end_time, '%H:%i') AS end_time, s.location As location, p.pname AS professor_name, c.credits
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                JOIN schedule s ON c.course_id = s.course_id
                JOIN professors p ON c.professor_id = p.professor_id
                WHERE e.student_id = %s
                GROUP BY c.course_id, c.course_name, s.start_time, s.end_time, p.pname, p.department, s.location; """
    cursor.execute(query,(student_id,))
    schedule = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('schedule.html', schedule=schedule, student=session['student_id'])

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'student_id' not in session:
        return redirect('login')
    student_id = session['student_id']
    course_id = request.form['course_id']

    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    query = "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s;"
    cursor.execute(query,(student_id, course_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash(f"You have successfully dropped course ID {course_id}.", "success")
    return redirect('/schedule')

@app.route('/search', methods=['GET'])
def search():
    if 'student_id' not in session:
        return redirect('login')
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    student_id = session['student_id']

    query = "SELECT student_id, sname FROM students WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()

    search = request.args.get('search')

    seach_query = """SELECT c.course_id, CONCAT(c.course_name, "  ", c.description) AS course, p.pname, c.capacity, c.credits
                    FROM courses c, professors p
                    Where c.course_id and c.professor_id = p.professor_id and 
                    (c.course_id LIKE CONCAT('%', %s,'%') or 
                    c.course_name LIKE CONCAT('%', %s,'%') or 
                    c.description LIKE CONCAT('%', %s,'%') or 
                    p.pname LIKE CONCAT('%', %s,'%'));"""
    
    cursor.execute(seach_query, (search, search, search, search))
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return  render_template ('search_results.html', courses=courses, student=student)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host="127.0.0.1", port=5000, ssl_context="adhoc")
