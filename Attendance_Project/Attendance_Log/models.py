from django.db import models
from django.conf import settings
class Student_Details(models.Model):
	User_Name=models.CharField(max_length=100,primary_key=True)
	Regno=models.CharField(max_length=100,unique=True)
	Name=models.CharField(max_length=100)
	DOB=models.DateField()
	Gender=models.CharField(max_length=50)
	Degree=models.CharField(max_length=100)
	Year=models.CharField(max_length=100,default="N/A")
	Department=models.CharField(max_length=100)
	Phone_Number=models.BigIntegerField()
	Mail_ID=models.EmailField(max_length = 254,unique=True)
	class Meta:
		db_table="Student_Details"

class Staff_Details(models.Model):		
	User_Name=models.CharField(max_length=100,primary_key=True)
	Staff_ID=models.CharField(max_length=50,unique=True)
	Name =models.CharField(max_length=100)
	Department =models.CharField(max_length=100)
	Phone_Number=models.BigIntegerField()
	Mail_ID=models.EmailField(max_length = 254,unique=True)
	Photo=models.ImageField(upload_to ='Staff_Images/')	
	class Meta:
		db_table="Staff_Details"

class OTP(models.Model):		
	User_Name=models.CharField(max_length=100,primary_key=True)
	Otp=models.IntegerField(unique=True)
	class Meta:
		db_table="OTP"	

class Sem_Days(models.Model):
	Working_Days= models.IntegerField()
	Date=models.DateField()		
	class Meta:
		db_table="Sem_Days"

class Students_Attendance(models.Model):
	Staff_ID=models.CharField(max_length=100,null = False)
	Student_Regno=models.ForeignKey("Student_Details",to_field="Regno",on_delete=models.CASCADE)
	Student_Name=models.CharField(max_length=100,null = False)
	Degree=models.CharField(max_length=100)
	Date=models.DateField()
	HR_1=models.CharField(max_length=10)
	HR_2=models.CharField(max_length=10)
	HR_3=models.CharField(max_length=10)
	HR_4=models.CharField(max_length=10)
	HR_5=models.CharField(max_length=10)
	class Meta:
		db_table="Students_Attendance"
		
class Facial_Students_Attendance(models.Model):
	Student_Regno=models.CharField(max_length=100,null = False)
	Face_id=models.CharField(max_length=10)
	Student_Name=models.CharField(max_length=100,null = False)
	Degree=models.CharField(max_length=100)
	Date=models.DateField()
	HR_1=models.CharField(max_length=10)
	HR_2=models.CharField(max_length=10)
	HR_3=models.CharField(max_length=10)
	HR_4=models.CharField(max_length=10)
	HR_5=models.CharField(max_length=10)
	class Meta:
		db_table="Facial_Students_Attendance"

class Students_Backup(models.Model):
	Regno=models.CharField(max_length=100,unique=True)
	Name=models.CharField(max_length=100,null=False)
	Phone_Number=models.BigIntegerField(null=False)
	Degree=models.CharField(max_length=100)
	Attendance=models.JSONField(default=dict)
	class Meta:
		db_table="Students_Backup"
# Create your models here. 
