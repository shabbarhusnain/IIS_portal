from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
class StudentID(models.Model):
    student_id = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.student_id    
    class Meta:
        ordering = ['student_id']
        
class Department(models.Model):
    depart=models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.depart
    def save(self, *args, **kwargs):
        is_new= self.pk is None
        super().save(*args, **kwargs) 
        if is_new:
            for i in range(1,9):
                Semester.objects.create(
                    semester=i,
                    department=self
                )
    class Meta:
        ordering = ['depart']
class Semester(models.Model):
    semester=models.IntegerField(default=1,  validators=[MinValueValidator(1), MaxValueValidator(8)])
    department=models.ForeignKey(Department,related_name='semesterdepartment', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self) -> str:
        return f' {self.semester} Semester'
    class Meta:
        unique_together=['semester','department']

class Courses(models.Model):
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE, related_name='semestercourses', null=True, blank=True)
    course_title = models.CharField(max_length=100)
    course_code = models.CharField(max_length=100)
    course_credit=models.IntegerField(null=True)
    def __str__(self) -> str:
        return self.course_title
    @property
    def course_total_marks(self):
        if self.course_credit:
            return self.course_credit * 20
        return 0
    class Meta:
        ordering = ['course_title']

class Student(models.Model):
    std_id=models.OneToOneField(StudentID, related_name='studentid',on_delete=models.CASCADE,  null=True, blank=True)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE, related_name='studentsemester', null=True, blank=True)
    std_name = models.CharField(max_length=100)
    std_father_name = models.CharField(max_length=100)
    std_phone = models.IntegerField()
    std_email = models.EmailField(null=True, blank=True)
    std_dob=models.DateField(null=True, blank=True)
    std_age=models.IntegerField(null=True, blank=True)
    std_address = models.TextField()
    std_image = models.ImageField(upload_to='Student_img')
    cgpa=models.FloatField(default=0.0)
    enrolled_courses = models.ManyToManyField(Courses, related_name='enrolled_students', blank=True)
    def __str__(self) -> str:
        return self.std_name
    class Meta:
        ordering = ['std_name']

class CourseMarks(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE, related_name='coursestudent', null=True, blank=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='coursename', null=True, blank=True)
    course_marks = models.IntegerField(null=True, blank=True)
    course_grade=models.CharField(max_length=10, null=True)
    course_qp=models.FloatField(default=0.0)
    course_percentage=models.FloatField(default=0.0)
    def __str__(self) -> str:
        return str(self.course_marks)
    @property
    def course_total_marks(self):
        if self.course:
            return self.course.course_total_marks
    
    
class SemesterHistory(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE, related_name='semesterstudent', null=True, blank=True)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE, related_name='allsemester', null=True, blank=True)
    sgpa=models.FloatField(default=0.0)
    status=models.BooleanField(default=True)
    grade=models.CharField(max_length=10,null=True)
    percentage=models.FloatField(default=0)
    def __str__(self) -> str:
        return str(self.sgpa)
    