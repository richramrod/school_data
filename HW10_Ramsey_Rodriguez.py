'''
Date 3/29/17

This program is a data repository of courses, students, and instructors.
The system will be used to help students track their required courses, 
the courses they have successfully completed, their grades,  GPA, etc.
The system will also be used by faculty advisors to help students to create
study plans.

Currently this program displays:
*summary of student info including Id, Name, and Completed Courses
*summary of instructor info including Id, Name, Department, Course name and # of students in each course 
Author: Ramsey Rodriguez
'''

from collections import defaultdict
import unittest
import prettytable
import sys

class Course:
    def __init__(self, code, number):
        self.code = code
        self.number = number
    
    def __str__(self):
        return str(self.code + ' ' + self.number)

class BaseCW:
    '''
    This base class contains all the basic information on a Stevens professor or student
    '''
    def __init__(self, cwid, last_name, first_initial, area_of_study, information):
        self.cwid = cwid
        self.last_name = last_name
        self.first_initial = first_initial
        self.area_of_study = area_of_study
        self.information = information

    def __str__(self):
        return self.last_name + ', ' + self.first_initial

class Student(BaseCW):
    '''
    params cwid, last_name, first_initial, area_of_study
    This student class has a method that contains the classes and respective grades
    'information' is a dictionary of [Course, letter_grade]
    '''


    def add_grade_information(self, class_name, grade):
        self.information[class_name] = grade
        
    def __str__(self):
        return self.last_name + ', ' + self.first_initial


class Instructor(BaseCW):
    '''
    params cwid, last_name, first_initial, area_of_study
    This student class has a method that contains the classes teaching and number of students
    'information' is a dictionary of [Course, number of students]
    '''


    def add_student_information(self, class_name):
        self.information[class_name] += 1

    def __str__(self):
        return self.last_name + ', ' + self.first_initial


class Repository:
    '''
    This repository class contains a set of students and a set of instructors
    '''
    def __init__(self):
        self.students = dict() #key: CWID value: Student
        self.instructors = dict() #key: CWID value: Instructor
        self.remaining_courses = dict() #key: CWID of student  value: list of Courses remaining

    def get_students(self):
        '''
        returns students as a list
        '''
        return list(self.students.values())

    def get_instructors(self):
        '''
        returns instructors as a list
        '''
        return list(self.instructors.values())

def read_students():
    students = dict()
    try:
        fp = open('students.txt')
    except FileNotFoundError as message:
        print(message)
        print('Student info not in current directory or is not a text file')
    else:
        with fp:

            for line in fp:
                student_info = line.strip().split()
                if(len(student_info) != 4):
                    print('corrupted or invalid formatted students.txt file... ending program')
                    sys.exit()

                student_info[1] = student_info[1][:-1]
                students[student_info[0]] = Student(student_info[0], student_info[1], student_info[2], student_info[3], defaultdict(str))

    return students


def read_instructors():
    instructors = dict()
    try:
        fp = open('instructors.txt')
    except FileNotFoundError as message:
        print(message)
        print('Instructor info not in current directory or is not a text file')
    else:
        with fp:

            for line in fp:
                instructor_info = line.strip().split()
                if(len(instructor_info) != 4):
                    print('corrupted or invalid formatted instructors.txt file... ending program')
                    sys.exit()

                instructor_info[1] = instructor_info[1][:-1]
                instructors[instructor_info[0]] = Instructor(instructor_info[0], instructor_info[1], instructor_info[2], instructor_info[3], defaultdict(int))

    return instructors


def read_grades(students, instructors):

    try:
        fp = open('grades.txt')
    except FileNotFoundError as message:
        print(message)
        print('Grade info not in current directory or is not a text file')
    else:
        with fp:

            for line in fp:
                grade_info = line.strip().split()
                if(len(grade_info) != 5):
                    print('corrupted or invalid formatted grades.txt file... ending program')
                    sys.exit()

                try:
                    students[grade_info[0]]
                except KeyError as message:
                    print(message)
                    print('Student', grade_info[0], 'not found')
                    continue

                student = students[grade_info[0]]
                course = Course(grade_info[1], grade_info[2])
                grade = grade_info[3]

                try:
                    instructors[grade_info[4]]
                except KeyError as message:
                    print(message)
                    print('Instructor', grade_info[4], 'not found')
                    continue

                instructor = instructors[grade_info[4]]
                student.add_grade_information(str(course), grade_info[3])
                instructor.add_student_information(str(course))   

    repository = Repository()
    repository.students = students
    repository.instructors = instructors
    return repository

def read_majors():
    courses = dict() #key: str(Course) value: Area of Study
    try:
        fp = open('majors.txt')
    except FileNotFoundError as message:
        print(message)
        print('Majors info not in current directory or is not a text file')
    else:
        with fp:

            for line in fp:
                major_info = line.strip().split()
                if(len(major_info) != 3):
                    print('corrupted or invalid formatted majors.txt file... ending program')
                    sys.exit()    
                
                course = Course(major_info[1], major_info[2])
                courses[str(course)] = major_info[0]

    return courses

def get_remaining_courses(students, courses, repository):
    remaining_courses = dict() #key: CWID of student  value: list of Courses remaining

    for s in students:
        courses_by_major = [c for c in courses.keys() if s.area_of_study == courses[c]]
        remaining = [si for si in courses_by_major if si not in s.information]
        remaining_courses[s.cwid] = sorted(remaining)

    repository.remaining_courses = remaining_courses
    return repository



def main():
    students = read_students()
    instructors = read_instructors()
    repository = read_grades(students, instructors)

    students_with_info =repository.get_students()
    instructors_with_info = repository.get_instructors()

    courses = read_majors()
    repository = get_remaining_courses(students_with_info, courses, repository)

    table_students = prettytable.PrettyTable()
    table_students.field_names = ["CWID", "Name", "Major","Completed Courses", "Remaining Courses"]
    for s in students_with_info:
        table_students.add_row([s.cwid, str(s), s.area_of_study, [si for si in s.information], repository.remaining_courses[s.cwid]])

    table_instructor = prettytable.PrettyTable()
    table_instructor.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
    for i in instructors_with_info:
        for c in i.information:
            table_instructor.add_row([i.cwid, str(i), i.area_of_study, c, i.information[c]])
        
    print('Student Summary')
    print(table_students)
    print('Instructor Summary')
    print(table_instructor)

    

class StudentTest(unittest.TestCase):
    def test_add_grade_information(self):
        student = Student('1111', 'Rodriguez', 'Ramsey', 'SFEN', defaultdict(str))
        course = Course('SSW', '810')
        course2 = Course('SSW', '540')
        grades = dict()

        student.add_grade_information(str(course), 'A+')
        student.add_grade_information(str(course2), 'A+')  
        grades[str(course)] = 'A+'
        grades[str(course2)] = 'A+'                    

        self.assertTrue(len(dict(student.information)) == 2)
        self.assertEqual(dict(student.information), grades)

class InstructorTest(unittest.TestCase):
    def test_add_student_information(self):
        course = Course('SSW', '810')
        instructor = Instructor('9999', 'Rowland', 'James', 'SFEN', defaultdict(int))
        expected_dict = dict()

        instructor.add_student_information(str(course))
        instructor.add_student_information(str(course))
        instructor.add_student_information(str(course))
        expected_dict[str(course)] = 3

        self.assertEqual(dict(instructor.information), expected_dict)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2) 
    main()