import mysql.connector
from mysql.connector import Error

#Create the connection to database
def connect_to_database():
    try:  
        connection = mysql.connector.connect(
            host='127.0.0.1',  #ip for the database, if local: 'localhost' or '127.0.0.1'
            user='',     #database user
            password='', #database password
            database='CSIT355'
            )
        cursor = connection.cursor(buffered=True)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
    
#Initialize init.sql with data   
def init_sql(connection, init_file = 'init.sql'): 
    try:
        cursor = connection.cursor()
        with open(init_file,'r') as file:
            statement = file.read()
        for query in statement.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
        print("Database initialized...")
    except FileNotFoundError:
        print(f"Error: File '{init_file}' not found.")
    except mysql.connector.Error as e:
        print(f"Error executing SQL query: {e}")
    finally:
        cursor.close()

#Enroll students to courses
def enroll_student(cursor, student_id, connection):
    if not connection.is_connected():
        connection.reconnect()
    # 1. Check prerequisites
    course_id = input("Enter course ID to enroll in: ")
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
        for prereq in unmet_prereqs:
            print(f"- Prerequisite Course ID: {prereq[0]}")
        return False

    # 2. Check schedule conflicts
    query_schedule_conflicts = """  SELECT  e.course_id AS conflicting_course_id, s1.meeting_day, s1.start_time, s1.end_time
                                    FROM enrollments e
                                    JOIN schedule s1 ON e.course_id = s1.course_id
                                    JOIN schedule s2 ON s2.course_id = %s
                                    WHERE e.student_id = %s 
                                    AND ((s1.meeting_day = s2.meeting_day) 
                                    AND ((s1.start_time < s2.end_time 
                                    AND s1.end_time > s2.start_time))); """
    cursor.execute(query_schedule_conflicts, (course_id, student_id))
    schedule_conflict = cursor.fetchall()
    
    if schedule_conflict:
        print("This course conflicts with your current schedule.")
        for conflict in schedule_conflict:
            print(f"- Conflict with Course ID: {conflict[0]} on {conflict[1]} from {conflict[2]} to {conflict[3]}")
            return False

    # 3. Check for duplicate enrollment
    query_duplicate = """SELECT 1
                        FROM enrollments
                        WHERE student_id = %s AND course_id = %s; """
    cursor.execute(query_duplicate, (student_id, course_id))
    duplicate = cursor.fetchone()

    if duplicate:
        print("You are already enrolled in this course.")
        return False

    # 4. Enroll in the course
    query_enroll = "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s);"
    cursor.execute(query_enroll, (student_id, course_id))
    print(f"Enrollment successful!")
    print(f"Student ID {student_id} successfully enrolled in Course ID {course_id}.")
    return False

#List classes from student
def list_my_classes(cursor, student_id): 
    query = """ SELECT c.course_name, 
                GROUP_CONCAT(s.meeting_day ORDER BY s.meeting_day SEPARATOR ', ') AS days,
                TIME_FORMAT(s.start_time, '%H:%i') AS start_time,
                TIME_FORMAT(s.end_time, '%H:%i') AS end_time, s.location As location, p.pname AS professor_name, c.credits
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                JOIN schedule s ON c.course_id = s.course_id
                JOIN professors p ON c.professor_id = p.professor_id
                WHERE e.student_id = %s
                GROUP BY c.course_id, c.course_name, s.start_time, s.end_time, p.pname, p.department, s.location; """
    cursor.execute(query, (student_id,))
    classes = cursor.fetchall()
    if not classes:
        print("You are not register in any course!")
        return
    for c in classes:
        print(f"| Course Name: {c[0]} | Day(s): {c[1]} | Start Time: {c[2]} | End Time: {c[3]} | Location: {c[4]} | Professor: {c[5]} | Credits: {c[6]} |")    

#list all available courses
def list_courses(cursor): 
    query = """ SELECT c.course_name, c.description, p.pname, c.capacity, c.credits
                FROM courses c, professors p
                Where c.professor_id = p.professor_id;"""
    cursor.execute(query)
    courses = cursor.fetchall()
    for course in courses:
        print(f"| Course: {course[0]} {course[1]} | Professor: {course[2]} | Seats: {course[3]} | Credits: {course[4]} |")

#Search for courses based on criteria
def search_courses(cursor, substring):    
    query = """
        SELECT course_name, description, capacity, credits 
        FROM courses 
        WHERE course_name LIKE CONCAT('%', %s, '%') 
        OR description LIKE CONCAT('%', %s, '%');"""
    cursor.execute(query, (substring, substring))
    courses = cursor.fetchall()
    for c in courses:
        print(f"Course: {c[0]} | {c[1]} | Seats: {c[2]} | Credits: {c[3]} |")

#list all classes taught by professors
def list_teaching_professors(cursor): 
    query = """ SELECT p.pname, p.department, GROUP_CONCAT(c.course_name SEPARATOR ', ') as Teaching
                FROM professors p
                LEFT JOIN courses c on p.professor_id = c.professor_id
                GROUP BY p.professor_id, p.pname, p.department;"""
    cursor.execute(query)
    professors = cursor.fetchall()
    for p in professors:
        print(f"Professor: {p[0]} | Department: {p[1]} | Course(s): {p[2]} |")

#Show prerequisites for selected class
def show_prerequisites(cursor, course_id):
    query = """ SELECT c1.course_name AS course_name, c2.course_name AS prerequisite_name
                FROM prerequisites p
                JOIN courses c1 ON p.course_id = c1.course_id
                JOIN courses c2 ON p.prerequisite_course_id = c2.course_id
                WHERE c1.course_id = %s;"""
    cursor.execute(query,(course_id,))
    prereq = cursor.fetchall()
    
    if not prereq:
        print(f"Course: {course_id} does not have any prerequisites.")
        return
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
        student_id = cursor.lastrowid
        connection.commit()
        print(f"Student: {sname} has been added to the database, Assigned Student ID: {student_id}!")
        EnterStudentID(cursor, connection)
        return student_id
    except Exception as e:
        print(f"Error adding Student: {e}")
        connection.rollback()
        EnterStudentID(cursor, connection)

#Check if Student exist in database
def check_student(cursor, sid):
    query = """SELECT student_id, sname, email, major, enrollment_year FROM students WHERE student_id = %s;"""
    cursor.execute(query, (sid,))
    check = cursor.fetchone()
    if check:
        print(f"Welcome Back {check[1]}! ")
        optionsMenu(cursor, connection)
        return sid
    else:
        print(f"Student with ID: {sid} does not exits.")
        EnterStudentID(cursor, connection)


def withdraw_course(cursor, connection, student_id, course_id):
    query = "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s;"
    try:
        if not connection.is_connected():
            connection.reconnect()
        cursor.execute("SELECT student_id From students WHERE student_id = %s;",(student_id,))
        if not cursor.fetchone():
            print(f"Error: Student ID {student_id} does not exist.")
            return
        cursor.execute("SELECT course_id From courses WHERE course_id = %s;",(course_id,))
        if not cursor.fetchone():
            print(f"Error: Course ID: {course_id} does not exist.")
            return
        cursor.execute("SELECT * FROM enrollments WHERE student_id = %s AND course_id = %s;",(student_id, course_id))
        if not cursor.fetchone():
            print(f"Error: Student ID {student_id} is not enrolled in Course ID {course_id}")
            return
        cursor.execute(query,(student_id, course_id))
        connection.commit()
        print(f"Student ID: {student_id} successfully withdrew from Course ID {course_id}.")
    except Exception as e:
        print(f"Error: An error occurred withdrawing from the course: {e}")
        connection.rollback()

#option Menu
def optionsMenu(cursor, connection):
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
                student_id = int(input("Re-enter your student ID: "))
                #course_id = int(input("Enter course ID to enroll in: ").split())
                enroll_student(cursor, student_id, connection)
            elif choice == 'W':
                student_id = int(input("Re-enter your student ID: ").strip())
                course_id = int(input("Enter course ID to withdraw from: ").strip())
                withdraw_course(cursor, connection, student_id, course_id)
            elif choice == 'S':
                substring = input("\nEnter course name substring: ")
                search_courses(cursor, substring)
            elif choice == 'M':
                student_id = int(input("\nRe-enter your student ID: "))
                list_my_classes(cursor, student_id)
            elif choice == 'P':
                course_id = int(input("\nEnter course ID to view prerequisites: "))
                show_prerequisites(cursor, course_id)
            elif choice == 'T':
                list_teaching_professors(cursor)
            elif choice == 'X':
                print("\nExiting System...")
                break
            else:
                print("\nInvalid option.")


def EnterStudentID(cursor, connection):
    try:
        sid = int(input("\nEnter Student ID or -1 to sign up: ").strip())
        if(sid == -1):
            add_student(cursor, connection)
        elif(sid > 0):
            check_student(cursor, sid)
    except ValueError:
        print("\nPlease Enter a Valid ID.")
        EnterStudentID(cursor, connection)
    

def main():
    connection = connect_to_database()
    if not connection:
        return
    cursor = connection.cursor()
    EnterStudentID(cursor, connection)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    connection = connect_to_database()
    if connection:
        init_sql(connection)
        connection.close()
    main()