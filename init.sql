-- Drop tables if they exist
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS prerequisites;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS grades;

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
); ALTER TABLE professors AUTO_INCREMENT = 1001;

-- Create students table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    sname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    major VARCHAR(50),
    enrollment_year INT,
    gpa FLOAT
); ALTER TABLE students AUTO_INCREMENT = 10001;

-- Create courses table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    capacity INT CHECK (capacity > 0),
    professor_id INT,
    credits INT,
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id)
); ALTER TABLE courses AUTO_INCREMENT = 101;

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
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
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
('Marc Labib','labibm@montclair.edu','Computer Science','2022'),
('Alexis Rivas','rivasa@montclair.edu','Computer Science','2023'),
('Samuel Cordova','cordovas@montclair.edu','Computer Science','2022');

INSERT INTO courses(course_name, description, capacity, professor_id, credits) VALUES
('CSIT 104','Python Programming I','30',1009,3),
('CSIT 111','Fundamentals of Java Programming','40',1008,3),
('CSIT 112','Fundamentals of Programming II','30',1007,3),
('CSIT 170','Discrete Mathematics','60',1006,3),
('CSIT 212','Data Structures and Algorithms','30',1005,3),
('CSIT 230','Computer Systems','30',1004,3),
('CSIT 231','Systems Programming','30',1003,3),
('CSIT 313','Fundamentals of Programming Languages','30',1002,3),
('CSIT 315','Software Engineering I','30',1001,3),
('CSIT 336','Game Development','30',1010,3),
('CSIT 337','InternetComputing','45',1014,3),
('CSIT 340','Computer Networks','45',1012,3),
('CSIT 345','Operating Systems','30',1013,3),
('CSIT 355','Database Systems','30',1012,3),
('CSIT 357','Artificial Intelligence','60',1015,3),
('CSIT 359','Data Visualization','30',1012,3),
('CSIT 379','Computer Science Theory','30',1017,3),
('CSIT 415','Software Engineering II','30',1018,3),
('CSIT 416','IT Project Management','40',1019,3),
('CSIT 431','Introduction to Robotics','25',1020,3),
('CSIT 432','Systems Administration','40',1012,3),
('CSIT 440','Principles of Data Mining','25',1016,3),
('CSIT 451','MobileComputing','25',1001,3),
('CSIT 455','Machine Learning','40',1002,3),
('CSIT 460','Computer Security','40',1003,3),
('CSIT 491','Co-op CS and IT','25',1004,3),
('CSIT 495','Special Topics in Undergraduate CS','25',1005,3);

INSERT INTO prerequisites(course_id, prerequisite_course_id) VALUES
(103,102),
(104,101),
(105,102),
(106,105),
(107,106),
(108,103),
(109,107),
(110,105),
(111,107),
(112,106),
(113,112),
(114,112),
(115,113),
(116,114),
(117,104),
(118,109),
(119,112),
(120,112),
(121,119),
(122,114),
(123,114),
(124,115),
(125,113),
(126,112),
(127,117);

INSERT INTO schedule (course_id, meeting_day, start_time, end_time, location) VALUES
(101,'Monday','09:00:00','10:30:00','Room 101'),
(101,'Thursday','09:00:00','10:30:00','Room 101'),
(102,'Monday','13:00:00','14:30:00','Room 201'),
(102,'Thursday','13:00:00','14:30:00','Room 201'),
(103,'Tuesday','10:00:00','11:30:00','Room 202'),
(103,'Friday','10:00:00','11:30:00','Room 202'),
(104,'Tuesday','12:00:00','13:30:00','Room 103'),
(104,'Friday','12:00:00','13:30:00','Room 103');

INSERT INTO enrollments(student_id, course_id) VALUES
(10001,101),
(10002,101),
(10001,102),
(10002,102);