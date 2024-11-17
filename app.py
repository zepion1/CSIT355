import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        # Create the connection to database
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
    
def init_sql(connection, init_file = 'init.sql'): #Initialize init.sql with mock data
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


def list_courses(cursor): #list all available courses
    query = """ SELECT c.course_name, c.description, p.pname, c.capacity
                FROM courses c, professors p
                Where c.professor_id = p.professor_id"""
    cursor.execute(query)
    courses = cursor.fetchall()
    for course in courses:
        print(f"| Course: {course[0]} {course[1]} | Professor: {course[2]} | Seats: {course[3]} |")

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


def withdraw_course(cursor, connection, student_id, course_id):
    query = "DELETE FROM enrollment WHERE StudentID = %s AND CourseID = %s"
    cursor.execute(query, (student_id, course_id))
    connection.commit()
    print("Course withdrawn successfully.")

def search_courses(cursor, substring):    #searh for courses based on criteria
    query = """
        SELECT course_name, description, capacity 
        FROM courses 
        WHERE course_name LIKE CONCAT('%', %s, '%') 
           OR description LIKE CONCAT('%', %s, '%')"""
    cursor.execute(query, (substring, substring))
    courses = cursor.fetchall()
    for c in courses:
        print(f"Course: {c[0]} | {c[1]} | Seats: {c[2]} |")

def list_my_classes(cursor, student_id): 
    query = """
        SELECT c.CourseName, c.MeetingTime, c.MeetingDay, p.FirstName, p.LastName
        FROM Enrollment e
        JOIN Courses c ON e.CourseID = c.CourseID
        JOIN Professors p ON c.ProfessorID = p.ProfessorID
        WHERE e.StudentID = %s"""
    cursor.execute(query, (student_id,))
    classes = cursor.fetchall()
    for c in classes:
        print(c)

def list_teaching_professors(cursor): #list all classes taught by professors
    query = """ SELECT p.pname, p.department, GROUP_CONCAT(c.course_name SEPARATOR ', ') as Teaching
                FROM professors p
                LEFT JOIN courses c on p.professor_id = c.professor_id
                GROUP BY p.professor_id, p.pname, p.department"""
    cursor.execute(query)
    professors = cursor.fetchall()
    for p in professors:
        print(f"Professor: {p[0]} | Deparment: {p[1]} | Course(s): {p[2]} |")

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

def main():
    connection = connect_to_database()
    if not connection:
        return
    cursor = connection.cursor()

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
            withdraw_course(cursor, connection, student_id, course_id)
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

