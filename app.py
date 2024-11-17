import mysql.connector
from mysql.connector import Error

#Create the connection to database
def connect_to_database():
    try:  
        connection = mysql.connector.connect(
            host='127.0.0.1',         
            user='zepion1',     
            password='password1', 
            database='CSIT355'
            )
        cursor = connection.cursor(buffered=True)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
    
#Initialize init.sql with mock data   
def init_sql(connection, init_file = 'init.sql'): 
    try:
        cursor = connection.cursor()
        with open(init_file,'r') as file:
            statement = file.read()
        for query in statement.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
        print("Databse initialized!")
    except FileNotFoundError:
        print(f"Error: File '{init_file}' not found.")
    except mysql.connector.Error as e:
        print(f"Error executing SQL query: {e}")
    finally:
        cursor.close()


def withdraw_course(cursor, student_id, course_id):
    query = "DELETE FROM enrollment WHERE StudentID = %s AND CourseID = %s"
    cursor.execute(query, (student_id, course_id))
    connection.commit()
    print("Course withdrawn successfully.")

def list_my_classes(cursor, student_id): 
    query = """ SELECT c.course_name, 
                GROUP_CONCAT(s.meeting_day ORDER BY s.meeting_day SEPARATOR ', ') AS days,
                TIME_FORMAT(s.start_time, '%H:%i') AS start_time,
                TIME_FORMAT(s.end_time, '%H:%i') AS end_time, s.location As location, p.pname AS professor_name
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                JOIN schedule s ON c.course_id = s.course_id
                JOIN professors p ON c.professor_id = p.professor_id
                WHERE e.student_id = %s
                GROUP BY c.course_id, c.course_name, s.start_time, s.end_time, p.pname, p.department, s.location; """
    cursor.execute(query, (student_id,))
    classes = cursor.fetchall()
    for c in classes:
        print(f"| Course Name: {c[0]} | Day(s): {c[1]} | Start Time: {c[2]} | End Time: {c[3]} | Location: {c[4]} | Professor: {c[5]} |")

#Enroll students to courses
def enroll_student(cursor, student_id, course_id):
    # 1. Check prerequisites
    query_prereqs = """ SELECT prerequisite_course_id
                        FROM prerequisites
                        WHERE course_id = %s AND prerequisite_course_id 
                        NOT IN (SELECT course_id
                                FROM enrollments
                                WHERE student_id = %s);"""
    cursor.execute(query_prereqs, (course_id, student_id))
    unmet_prereqs = cursor.fetchall()
    if unmet_prereqs:
        print("You do not meet all the prerequisites for this course.")
        return

    # 2. Check schedule conflicts
    query_schedule_conflicts = """  SELECT 1
                                    FROM enrollments e
                                    JOIN schedule s1 ON e.course_id = s1.course_id
                                    JOIN schedule s2 ON s2.course_id = %s
                                    WHERE e.student_id = %s 
                                    AND ((s1.meeting_day = s2.meeting_day) 
                                    AND ((s1.start_time < s2.end_time 
                                    AND s1.end_time > s2.start_time))); """
    cursor.execute(query_schedule_conflicts, (course_id, student_id))
    schedule_conflict = cursor.fetchone()
    if schedule_conflict:
        print("This course conflicts with your current schedule.")
        return

    # 3. Check for duplicate enrollment
    query_duplicate = """SELECT 1
                         FROM enrollments
                        WHERE student_id = %s AND course_id = %s; """
    cursor.execute(query_duplicate, (student_id, course_id))
    duplicate = cursor.fetchone()
    if duplicate:
        print("You are already enrolled in this course.")
        return

    # 4. Enroll in the course
    query_enroll = "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s);"
    cursor.execute(query_enroll, (student_id, course_id))
    print("Enrollment successful!")

#list all available courses
def list_courses(cursor): 
    query = """ SELECT c.course_name, c.description, p.pname, c.capacity
                FROM courses c, professors p
                Where c.professor_id = p.professor_id"""
    cursor.execute(query)
    courses = cursor.fetchall()
    for course in courses:
        print(f"| Course: {course[0]} {course[1]} | Professor: {course[2]} | Seats: {course[3]} |")

#Searh for courses based on criteria
def search_courses(cursor, substring):    
    query = """
        SELECT course_name, description, capacity 
        FROM courses 
        WHERE course_name LIKE CONCAT('%', %s, '%') 
           OR description LIKE CONCAT('%', %s, '%')"""
    cursor.execute(query, (substring, substring))
    courses = cursor.fetchall()
    for c in courses:
        print(f"Course: {c[0]} | {c[1]} | Seats: {c[2]} |")

#list all classes taught by professors
def list_teaching_professors(cursor): 
    query = """ SELECT p.pname, p.department, GROUP_CONCAT(c.course_name SEPARATOR ', ') as Teaching
                FROM professors p
                LEFT JOIN courses c on p.professor_id = c.professor_id
                GROUP BY p.professor_id, p.pname, p.department"""
    cursor.execute(query)
    professors = cursor.fetchall()
    for p in professors:
        print(f"Professor: {p[0]} | Deparment: {p[1]} | Course(s): {p[2]} |")

#Show prerequisites for selected class
def show_prerequisites(cursor, course_id):
    query = """ SELECT c1.course_name AS course_name, c2.course_name AS prerequisite_name
                FROM prerequisites p
                JOIN courses c1 ON p.course_id = c1.course_id
                JOIN courses c2 ON p.prerequisite_course_id = c2.course_id
                WHERE c1.course_id = %s"""
    cursor.execute(query,(course_id,))
    prereq = cursor.fetchall()
    for req in prereq:
        print(f"Course: {req[0]} requires {req[1]}")

# Adds new student to database
def add_student(cursor, connection):
    sname = input("Enter Full name: ").strip()
    email = input("Enter Email: ").strip()
    major = input("Enter Major: ").strip()
    year = input("Enter enrollment year: ").strip()
    if not sname or not email or not major or not year:
        print("Invalid Input. Please Try Again!")
        return 
    query = """INSERT INTO students (sname, email, major, enrollment_year) VALUES
        (%s, %s, %s, %s);"""
    try:
        cursor.execute(query, (sname, email, major, year))
        connection.commit()
        print(f"Student: {sname} has been added to the database!")
        return
    except Exception as e:
        print(f"Error adding Student: {e}")
        connection.rollback()

#Check if Student exist in database
def check_student(cursor, sid):
    query = """SELECT student_id, sname, email, major, enrollment_year FROM students WHERE student_id = %s;"""
    cursor.execute(query, (sid,))
    check = cursor.fetchone()
    if check:
        print(f"Welcome Back {check[1]}! ")
    else:
        print(f"Student with ID: {sid} does not exits.")

def main():
    connection = connect_to_database()
    if not connection:
        return
    cursor = connection.cursor()

    sid = int(input("Enter Student ID or -1 to sign up: ").strip())
    if(sid == -1):
        add_student(cursor, connection)
    else:
        check_student(cursor, sid)

    while True:
        print("\nMenu:")
        print("L - List Courses")
        print("E - Enroll in a Course")
        print("W - Withdraw from a Course")
        print("S - Search Courses")
        print("M - My Classes")
        print("P - Prerequisites")
        print("T - Teaching Professors")
        print("X - Exit")
        choice = input("Select an option: ").upper()
        if choice == 'L':
            list_courses(cursor)
        elif choice == 'E':
            student_id = int(input("Enter your student ID: "))
            course_id = int(input("Enter course ID to enroll in: "))
            enroll_student(cursor, student_id, course_id)
        elif choice == 'W':
            student_id = int(input("Enter your student ID: "))
            course_id = int(input("Enter course ID to withdraw from: "))
            withdraw_course(cursor, student_id, course_id)
        elif choice == 'S':
            substring = input("\nEnter course name substring: ")
            search_courses(cursor, substring)
        elif choice == 'M':
            student_id = int(input("\nEnter your student ID: "))
            list_my_classes(cursor, student_id)
        elif choice == 'P':
            course_id = int(input("\nEnter course ID to view prerequisites: "))
            show_prerequisites(cursor, course_id)
        elif choice == 'T':
            list_teaching_professors(cursor)
        elif choice == 'X':
            print("Exiting System...")
            break
        else:
            print("Invalid option.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    connection = connect_to_database()
    if connection:
        init_sql(connection)
        connection.close()
    main()

