from django.shortcuts import render, redirect
from studentportal.models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, login as auth_login
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime
from django.db.models import Q, Sum,  Count
from django.core.paginator import Paginator
# Create your views here.
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def student_portal(request):
    department=Department.objects.all()
    student=Student.objects.all()
    totalstudent=student.count()
    totaldepartment=department.count()
    context={
        'department_db':department,
        'count':totalstudent,
        'dcount':totaldepartment
    }
    if request.GET.get('searchdepart'):
            search=request.GET.get('searchdepart')
            queryset= Department.objects.filter(depart__icontains= search
            )
            context={
                    'department_db':queryset
                }
    if request.GET.get('search'):
        search=request.GET.get('search')
        queryset= Student.objects.filter(
            Q(std_name__icontains=search)|
            Q(std_id__student_id__icontains=search)
        )
        context={
                'queryset':queryset
            }
    
    return render(request,'frontend/studentportal.html', context)
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def semesters(request,id):
    semester =Semester.objects.filter(department__id=id)
    department=Department.objects.get(id=id)
    context = {
        'id':id,
        'semesters':semester,
        'department':department
        
        }
    return render(request, 'frontend/semester.html',context)
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def students(request,id):
    queryset=Student.objects.filter(semester__id=id)
    department=Semester.objects.get(id=id)
    totalstudent= queryset.count()
    if request.GET.get('search'):
        search=request.GET.get('search')
        queryset=Student.objects.filter(
            Q(std_id__student_id__icontains=search)|
            Q(std_name__icontains=search)
        )
        context={'queryset':queryset}
    # pagiation
    paginator=Paginator(queryset,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    context={
        'queryset':page_obj,
        'id':id,
        'dept':department,
        'totalstudent':totalstudent
    }
    return render(request,'frontend/students.html', context)
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def studentcard(request, id):
    queryset= Student.objects.get(id=id)
    semester=queryset.semester
    course= CourseMarks.objects.filter(student__id=id)
    marks=0
    for crs in course:
        marks+=crs.course_marks
    semesterhistory=SemesterHistory.objects.filter(student=queryset)
    context={
        'student':queryset,
        'course':course,
        'totalmarks':marks,
        'semesterhistory':semesterhistory
    }
    return render(request, 'frontend/studentcard.html', context)

# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def add_student(request):
    department_obj= Department.objects.all()
    if request.method == "POST":
        data = request.POST
        department=data.get('department')
        name = data.get('stdname')
        f_name = data.get('stdfathername')
        phone = data.get('stdphone')
        address = data.get('stdaddress')
        dob = data.get('stddob')
        email = data.get('stdemail')
        image = request.FILES.get('stdimage')
        semesters = Semester.objects.filter(department__id=department)
        semester_obj = semesters[0]
        while True:
            std_id = f"ST-{datetime.now().year}-{random.randint(100,999)}"
            if not StudentID.objects.filter(student_id=std_id).exists():
                break 
        std_id_obj = StudentID.objects.create(student_id=std_id)
        birth = datetime.strptime(dob,"%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year
        student_obj=Student.objects.create(
        std_id=std_id_obj,
        semester=semester_obj,
        std_name=name, 
        std_father_name=f_name,
        std_phone=phone,
        std_address=address,
        std_email=email,
        std_dob=dob,
        std_age=age,
        std_image=image)
        semester_courses = Courses.objects.filter(semester=semester_obj)
        student_obj.enrolled_courses.set(semester_courses)   
        return redirect(f'/std_portal/')
    return render(request,'frontend/addstudent.html', {'queryset': department_obj})
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def update_student(request, id):
    queryset = Student.objects.get(id=id)
    department = Student.objects.filter(id=id)
    if request.method=="POST":
        data = request.POST
        name = data.get('stdname')
        f_name = data.get('stdfathername')
        phone = data.get('stdphone')
        address = data.get('stdaddress')
        dob = data.get('stddob')
        email = data.get('stdemail')
        image = request.FILES.get('stdimage')
        birth = datetime.strptime(dob,"%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year
        queryset.std_name=name
        queryset.std_father_name=f_name
        queryset.std_phone=phone
        queryset.std_address=address
        queryset.std_dob = dob
        queryset.std_age = age
        queryset.std_email = email
        if image:
            queryset.std_image=image
        queryset.save()
        return redirect(f'/studentcard/{id}')
    context={
        'data':queryset,
        "department":department
    } 
    return render(request,'frontend/update_student.html',context)
# ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def delete_student(request,id):
    queryset= Student.objects.get(id=id)
    semester=queryset.semester.id
    queryset.delete()
    return redirect(f'/students/{semester}')
# ---------------------------------------------------------------------------------------------------------
def register(request):
    if request.method == "POST":
        data=request.POST
        firstname = data.get('first_name')
        lastname= data.get('last_name')
        username = data.get('username')
        password = data.get('password')

        user= User.objects.filter(username=username)
        if user.exists():
            messages.info(request,'Username already taken.')
            return redirect('/register/')

        user = User.objects.create(
            first_name=firstname,
            last_name = lastname,
            username=username
        )
        user.set_password(password)
        user.save()
        messages.info(request,'Account created successfully')
        login(request,user)
        return redirect('/std_portal/')
    return render(request, 'frontend/register.html')
# ---------------------------------------------------------------------------------------------------------
def login_page(request):
    if request.method=="POST":
        data = request.POST
        username= data.get('username')
        password = data.get('password')

        if not User.objects.filter(username=username):
            messages.info(request,'Invalid Username.')
            return redirect('/login/')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.info(request, 'Wrong Password.')
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/std_portal/')

    return render(request,"frontend/login.html")
# ---------------------------------------------------------------------------------------------------------
def logout_page(request):
    logout(request)
    return redirect('/login/')
# ---------------------------------------------------------------------------------------------------------
def menu_page(request):
    queryset=Student.objects.all()
    query=queryset.count()
    return render(request,'frontend/menu.html',{'count':query})
# ---------------------------------------------------------------------------------------------------------
def add_result(request,id):
    queryset=Student.objects.filter(semester__id=id)
    department=Semester.objects.get(id=id)
    course=Courses.objects.filter(semester__id=id)
    # course_list = CourseMarks.objects.filter(student__id=pk)
    if request.method=="POST":
        data=request.POST
        student=data.get('studentid')
        courseid=data.getlist('coursetitle')
        obtainmarks=data.getlist('obtainmarks')
        student_obj=Student.objects.get(id=student)
        for c_id, marks in zip(courseid, obtainmarks ):
            course_obj =Courses.objects.get(id=c_id)
            CourseMarks.objects.create(
                student=student_obj,
                course=course_obj,
                course_marks=marks
            )
        coursemarks=CourseMarks.objects.filter(student=student_obj)
        total_qp = 0.0
        total_ch = 0.0
        for course in coursemarks:
            if course.course_total_marks >0:
                obtain_marks=course.course_marks
                total_marks= course.course_total_marks
                age=round((obtain_marks/total_marks)*100,2)
                if age>=90 and age<=100 :
                    grade = 'A+'
                    gp=4.00
                elif age>=85 and age<=89 :
                    grade = 'A'
                    gp=3.67
                elif age>=80 and age<=84 :
                    grade = 'A-'
                    gp=3.33
                elif age>=75 and age<=79 :
                    grade = 'B+'
                    gp=3.00          
                elif age>=70 and age<=74 :
                    grade = 'B'
                    gp=2.70
                elif age>=65 and age<=69 :
                    grade = 'B-'
                    gp=2.50
                elif age>=60 and age<=64 :
                    grade = 'C+'
                    gp=2.00
                elif age>=55 and age<=59 :
                    grade = 'C'
                    gp=1.70  
                elif age>=50 and age<=54 :
                    grade = 'D'
                    gp=1.00  
                else:
                    grade = 'F'
                    gp=0.00  
                ch = course.course.course_credit
                qp = gp*ch 
                total_qp +=qp
                total_ch +=ch
                course.course_grade=grade
                course.course_qp=qp
                course.course_percentage=age
                course.save()
            continue    
        gpa = round(total_qp/total_ch,2)
        semester_obj=Semester.objects.get(id=id)
        if gpa<=2.00:
            status=False
        else:
            status=True 
        if gpa >= 4.00:
            semester_grade = 'A+'
        elif gpa >= 3.67 and gpa < 4.00:
            semester_grade = 'A'
        elif gpa >= 3.33 and gpa < 3.67:
            semester_grade = 'A-'
        elif gpa >= 3.00 and gpa < 3.33:
            semester_grade = 'B+'
        elif gpa >= 2.70 and gpa < 3.00:
            semester_grade = 'B'
        elif gpa >= 2.50 and gpa < 2.70:
            semester_grade = 'B-'
        elif gpa >= 2.30 and gpa < 2.50:
            semester_grade = 'C+'
        elif gpa >= 2.00 and gpa < 2.30:
            semester_grade = 'C'
        elif gpa >= 1.70 and gpa < 2.00:
            semester_grade = 'C-'
        elif gpa >= 1.00 and gpa < 1.70:
            semester_grade = 'D'
        else:
            semester_grade = 'F'
        semester_age=round((gpa/4.0)*100,1)
        SemesterHistory.objects.create(
            student=student_obj,
            semester=semester_obj,
            sgpa=gpa,
            status=status,
            grade=semester_grade,
            percentage=semester_age
        )
        if status==True:
            next_semesters=Semester.objects.filter(id__gt=id).order_by('id')
            new_semester=next_semesters.first()
            if new_semester:
                student_obj.semester=new_semester
                course=Courses.objects.filter(semester=new_semester)
                student_obj.enrolled_courses.set(course)
                student_obj.save()
        studenthistory=SemesterHistory.objects.filter(student=student_obj)
        all_sem_qp=0.0
        total_c_h=0
        for history in studenthistory:
            sgpa=history.sgpa
            c_h=0
            for crs in history.semester.semestercourses.all():
                c_h+= crs.course_credit
            sem_qp=round(sgpa*c_h,2)
            total_c_h+=c_h
            all_sem_qp+=sem_qp
        if total_c_h>0:
            totalcgpa=round(all_sem_qp/total_c_h,2)
            student_obj.cgpa=totalcgpa
            student_obj.save()
        return redirect(f'/students/{id}/')    
    context={
        'queryset':queryset,
        'department':department,
        'course':course
    }
    return render(request, 'frontend/addresult.html',context)
def assign_course(request,id):
    semester=Semester.objects.get(id=id)
    semester_id=semester.id
    if request.method=="POST":
        data=request.POST
        coursetitle=data.get('coursetitle')
        coursecode=data.get('coursecode')
        coursecredit=data.get('coursecredit')
        Courses.objects.create(
            semester=semester,
            course_title=coursetitle,
            course_code=coursecode,
            course_credit=coursecredit
        )
        messages.info(request,f'Course {coursetitle} Added Successfully in {semester} Semester of {semester.department}')
        return redirect('view_courses',id=semester_id)
    return render(request,'frontend/assign_course.html',{'semester':semester})
def view_courses(request,id):
    pk=Semester.objects.get(id=id)
    queryset=Courses.objects.filter(semester__id=id)
    csum=queryset.count()
    return render(request, 'frontend/view_courses.html',{'courses':queryset,'pk':pk,'csum':csum})
def delete_course(request,id):
    course=Courses.objects.get(id=id)
    semester_id= course.semester.id
    course.delete()
    return redirect('view_courses',id=semester_id)
def add_department(request):
    if request.method=="POST":
        department=request.POST.get('department')
        Department.objects.create(depart=department)
        return redirect('/std_portal/')
    return render(request, 'frontend/add_department.html')
def display_result(request):
    return render(request,'frontend/studentcard.html')