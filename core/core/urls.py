"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from core import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from studentportal.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',student_portal, name='student_portal'),
    path('std_portal/',student_portal, name='student_portal'),
    path('add_std/',add_student, name="add_student"),
    path('delete/<int:id>',delete_student, name='delete_student'),
    path('update/<int:id>',update_student, name='update_student'),
    path('login/',login_page,name='login_page'),
    path('logout/',logout_page, name='logout_page'),
    path('register/',register,name='reqister'),
    path('semesters/<int:id>',semesters,name='semesters'),
    path('students/<int:id>/',students,name='students'),
    path('studentcard/<int:id>',studentcard,name='studentcard'),
    path('add_result/<id>/',add_result, name="add_result"),
    path('assign_course/<id>/',assign_course, name='assign_course'),
    path('menu_page/',menu_page, name='menu_page'),
    path('view_courses/<id>/',view_courses,name='view_courses'),
    path('delete_course/<id>/',delete_course,name='delete_course'),
    path('add_department/',add_department, name='add_department')
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    
urlpatterns += staticfiles_urlpatterns()