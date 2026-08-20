from .models import *
from faker import Faker
fake=Faker()
import random
from datetime import datetime, date
from django.db import transaction
import re

import random
import re
from datetime import datetime, date
from django.db import transaction

def sead_db(n=10) -> None:
    
    all_semesters = list(Semester.objects.all())
    for i in range(0, n):
        try:
            random_semester = random.choice(all_semesters)
            
            # Unique ID Generation Loop
            while True:
                std_id = f"STU-{datetime.now().year}-{random.randint(1000, 9999)}"
                if not StudentID.objects.filter(student_id=std_id).exists():
                    break
                    
            name = fake.name()
            f_name = fake.name()
            email = fake.email()
            dob = fake.date_between(start_date='-30y', end_date=date(2009, 12, 31)).strftime('%Y-%m-%d')
            address = fake.address()
            
            raw_phone = re.sub(r'\D', '', fake.phone_number())[:9]
            phone = int(raw_phone) if raw_phone else 3001234567
            
            with transaction.atomic():
                std_id_obj = StudentID.objects.create(student_id=std_id)
                birth = datetime.strptime(dob, "%Y-%m-%d")
                today = datetime.now()
                age = today.year - birth.year
                
                student_obj = Student.objects.create(
                    std_id=std_id_obj,
                    std_name=name, 
                    std_father_name=f_name,
                    std_phone=phone,
                    std_address=address,
                    std_email=email,
                    std_dob=dob,
                    std_age=age,
                    semester=random_semester 
                )
                semester_courses = Courses.objects.filter(semester=random_semester)
                student_obj.enrolled_courses.set(semester_courses)

        except Exception as e:
            print(f"Error at student {i}: {e}")

def fake_courses():
    cs_dept, _ = Department.objects.get_or_create(depart='Computer Science')
    se_dept, _ = Department.objects.get_or_create(depart='Software Engineering')
    
    course_data = {
        'Computer Science': {
            1: [('Programming Fundamentals', 'CS-101', 3), ('Calculus & Analytic Geometry', 'MATH-101', 3)],
            2: [('Object Oriented Programming', 'CS-102', 3), ('Discrete Structures', 'CS-104', 3)],
            3: [('Data Structures & Algorithms', 'CS-201', 3), ('Digital Logic Design', 'CS-202', 3)],
            4: [('Operating Systems', 'CS-204', 3), ('Database Systems', 'CS-206', 3)],
            5: [('Theory of Automata', 'CS-301', 3), ('Computer Networks', 'CS-305', 3)],
            6: [('Artificial Intelligence', 'CS-308', 3), ('Compiler Construction', 'CS-312', 3)],
            7: [('Information Security', 'CS-401', 3), ('Final Year Project I', 'CS-499A', 3)],
            8: [('Data Science', 'CS-405', 3), ('Final Year Project II', 'CS-499B', 3)],
        },
        'Software Engineering': {
            1: [('Introduction to SE', 'SE-101', 3), ('Applied Physics', 'PHY-101', 3)],
            2: [('Object Oriented Programming', 'SE-102', 3), ('Software Requirements Eng', 'SE-104', 3)],
            3: [('Data Structures', 'SE-201', 3), ('Software Architecture & Design', 'SE-202', 3)],
            4: [('Operating Systems', 'SE-204', 3), ('Software Construction', 'SE-206', 3)],
            5: [('Formal Methods in SE', 'SE-301', 3), ('Software Quality Assurance', 'SE-305', 3)],
            6: [('Web Engineering', 'SE-308', 3), ('Human Computer Interaction', 'SE-312', 3)],
            7: [('Software Project Management', 'SE-401', 3), ('Design Project I', 'SE-499A', 3)],
            8: [('Software Re-Engineering', 'SE-405', 3), ('Design Project II', 'SE-499B', 3)],
        }
    }
    
    departments_mapping = {
        'Computer Science': cs_dept,
        'Software Engineering': se_dept
    }
    
    for dept_name, semesters in course_data.items():
        current_dept_obj = departments_mapping[dept_name]
        for sem_num, courses_list in semesters.items():
            semester_obj, created = Semester.objects.get_or_create(
                semester=sem_num,
                department=current_dept_obj
            )
            for title, code, credit in courses_list:
                Courses.objects.get_or_create(
                    semester=semester_obj,
                    course_title=title,
                    course_code=code,
                    course_credit=credit
                )

