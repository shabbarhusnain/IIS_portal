from django.shortcuts import render, redirect
from studentportal.models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.db import transaction
import random
from datetime import datetime
from django.db.models import Q
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
    course = CourseMarks.objects.filter(student__id=id)
    context={
        'student':queryset,
        'course':course
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
    queryset.delete()
    return redirect(f'/studentcard/{id}')
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
    if request.method=="POST":
        data=request.POST
        coursecredit=data.get('coursecredit')
        obtainmarks=data.get('obtainmarks')
        CourseMarks.objects.create(
            course_marks=obtainmarks,
            course_credit=coursecredit
        )
    context={
        'queryset':queryset,
        'department':department,
        'course':course
    }
    return render(request, 'frontend/addresult.html',context)