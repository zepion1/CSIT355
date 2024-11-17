-- Drop tables if they exist
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS prerequisites;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- Create professors table
CREATE TABLE professors (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    pname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50)
);

-- Create students table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    sname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    major VARCHAR(50),
    enrollment_year INT,
    gpa DOUBLE NULL
);

-- Create courses table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    capacity INT CHECK (capacity > 0),
    professor_id INT,
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id)
);

-- Create prerequisites table
CREATE TABLE prerequisites (
    course_id INT NOT NULL,
    prerequisite_course_id INT NOT NULL,
    PRIMARY KEY (course_id, prerequisite_course_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (prerequisite_course_id) REFERENCES courses(course_id)
);

-- Create schedule table
CREATE TABLE schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    meeting_day ENUM('Monday','Tuesday','Wednesday','Thursday','Friday'),
    start_time TIME NOT NULL CHECK (start_time >='08:00:00'),
    end_time TIME NOT NULL CHECK (end_time <='22:00:00'),
    location VARCHAR(100),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Create enrollments table
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    UNIQUE (student_id, course_id)
);

INSERT INTO departments(department_name) VALUES
('Computing'),
('Science'),
('Mathematics'),
('Business'),
('Art');

INSERT INTO professors (pname, email, department) VALUES
('Constantine Coutras',' coutrasc@montclair.edu','Computing'),
('George Antoniou','antonioug@mail.montclair.edu','Computing' ),
('Boxiang Dong',' dongb@montclair.edu','Computing'),
('Chao Huang',' huangch@montclair.edu','Computing'),
('Elliot Hu-Au',' huaue@montclair.edu','Computing'),
('John Jenq',' jenqj@montclair.edu','Computing'),
('Hubert Johnson',' johnsonh@montclair.edu','Computing'),
('Jesse Parron','parronj@montclair.edu','Computing'),
('Daeyoung Kim',' kimda@montclair.edu','Computing'),
('Yan Kong',' kongy@montclair.edu','Computing'),
('Christopher Leberknight',' leberknightc@montclair.edu','Computing'),
('Hao Liu',' liuha@montclair.edu','Computing'),
('Rui Li',' liru@montclair.edu','Computing'),
('Jing Peng',' pengj@montclair.edu','Computing'),
('Stefan Robila',' robilas@montclair.edu','Computing'),
('Raina Samuel',' samuelr@montclair.edu','Computing'),
('Dajin Wang',' wangd@montclair.edu','Computing'),
('Jiayin Wang',' wangji@montclair.edu','Computing'),
('Weitian Wang',' wangw@montclair.edu','Computing'),
('Michelle Zhu',' zhumi@montclair.edu','Computing');

INSERT INTO students(sname, email, major, enrollment_year) VALUES
('Oscar Ordonez','ordonezc@montclair.edu','Computer Science','2022'),
('Marc Labib','labibm@montclair.edu','Computer Science','2023'),
('Alexis Rivas','rivasa@montclair.edu','Computer Science','2023'),
('Samuel Cordova','cordovas@montclair.edu','Computer Science','2022');

INSERT INTO courses(course_name, description, capacity, professor_id) VALUES
('CSIT 104','Python Programming I','30','9'),
('CSIT 111','Fundamentals of Java Programming','40','8'),
('CSIT 112','Fundamentals of Programming II','30','7'),
('CSIT 170','Discrete Mathematics','60','6'),
('CSIT 212','Data Structures and Algorithms','30','5'),
('CSIT 230','Computer Systems','30','4'),
('CSIT 231','Systems Programming','30','3'),
('CSIT 313','Fundamentals of Programming Languages','30','2'),
('CSIT 315','Software Engineering I','30','1'),
('CSIT 336','Game Development','30','10'),
('CSIT 337','InternetComputing','45','14'),
('CSIT 340','Computer Networks','45','12'),
('CSIT 345','Operating Systems','30','13'),
('CSIT 355','Database Systems','30','12'),
('CSIT 357','Artificial Intelligence','60','15'),
('CSIT 359','Data Visualization','30','12'),
('CSIT 379','Computer Science Theory','30','17'),
('CSIT 415','Software Engineering II','30','18'),
('CSIT 416','IT Project Management','40','19'),
('CSIT 431','Introduction to Robotics','25','20'),
('CSIT 432','Systems Administration','40','12'),
('CSIT 440','Principles of Data Mining','25','16'),
('CSIT 451','MobileComputing','25','1'),
('CSIT 455','Machine Learning','40','2'),
('CSIT 460','Computer Security','40','3'),
('CSIT 491','Co-op CS and IT','25','4'),
('CSIT 495','Special Topics in Undergraduate CS','25','5');

INSERT INTO prerequisites(course_id, prerequisite_course_id) VALUES
(3,2),
(4,1),
(5,2),
(6,5),
(7,6),
(8,3),
(9,7),
(10,5),
(11,7),
(12,6),
(13,12),
(14,12),
(15,13),
(16,14),
(17,4),
(18,9),
(19,12),
(20,12),
(21,19),
(22,14),
(23,14),
(24,15),
(25,13),
(26,12),
(27,17);

INSERT INTO schedule (course_id, meeting_day, start_time, end_time, location) VALUES
(1,'Monday','09:00:00','10:30:00','Room 101'),
(1,'Thursday','09:00:00','10:30:00','Room 101'),
(2,'Monday','13:00:00','14:30:00','Room 201'),
(2,'Thursday','13:00:00','14:30:00','Room 201');

INSERT INTO enrollments(student_id, course_id) VALUES
(1,1),
(2,1),
(1,2),
(2,2);