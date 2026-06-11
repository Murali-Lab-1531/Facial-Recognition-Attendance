from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.contrib.auth import authenticate,login,logout
from .models import Staff_Details,OTP,Student_Details,Sem_Days,Students_Backup,Students_Attendance,Facial_Students_Attendance
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
import random,datetime
class login_form:
	def login(request):
		username=request.POST.get("usr")
		password=request.POST.get("psd")	
		user = authenticate(username=username, password=password)	
		if user is not None:		
			login(request,user)
			if(user.groups.filter(name='Admin').exists()):		
				return render(request,"Admin_Home_Page.html")
			elif(user.groups.filter(name='Staff_Group').exists()):
				Date=datetime.date.today()
				Staff=Staff_Details.objects.all().filter(User_Name=user)
				context={'Staff_det':Staff,'Date':Date}
				return render(request,"Staff_Home_Page.html",context)
			else:
				Date=datetime.date.today()
				Student=Student_Details.objects.get(User_Name=user)	
				Student_Attendance=Students_Attendance.objects.all().filter(Student_Regno_id=Student.Regno).values()
				Working_Days=Sem_Days.objects.filter(id="1").values()
				Working_Days=Working_Days[0]["Working_Days"]
				if(Student.Regno in str(Student_Attendance)):
					Absent_Days=0
					OD_Days=0
					ML_Days=0
					for j in Student_Attendance:
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_1"]=="AB" or j["HR_2"]=="AB" or j["HR_3"]=="AB")):
							Absent_Days+=0.5
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_4"]=="AB" or j["HR_5"]=="AB")):
							Absent_Days+=0.5
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_1"]=="OD" or j["HR_2"]=="OD" or j["HR_3"]=="OD")):
							OD_Days+=0.5
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_4"]=="OD" or j["HR_5"]=="OD")):
							OD_Days+=0.5
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_1"]=="ML" or j["HR_2"]=="ML" or j["HR_3"]=="ML")):
							ML_Days+=0.5
						if(Student.Regno==j["Student_Regno_id"] and (j["HR_4"]=="ML" or j["HR_5"]=="ML")):
							ML_Days+=0.5
						Attendance=round(((int(Working_Days)-Absent_Days)/int(Working_Days))*100,2)
				else:
					OD_Days=0.0
					ML_Days=0.0
					Absent_Days=0.0
					Attendance=100.0
				context={'Student_det':Student,'Date':Date,'Days':Working_Days,'Attendance':Student_Attendance,
				'Attendance_Average':Attendance,'Absent_Days':Absent_Days,'OD':OD_Days,'ML':ML_Days}
				return render(request,"Students_Home_Page.html",context)
		else:
			context={'title': 'Invalid Username or Password'}
			return render(request, 'index.html',context)
	def forgot_password(request):
		data=request.GET.get("usr_name")  	    		
		try:
			user=User.objects.get(username=data)
			mail_to=[]
			mail_to.append(user.email)
			res = user.email[1:user.email.index('@')]
			if(len(res)<=4):
				res=res[len(res)-3:]
			else:
				res=res[len(res)-4:]
				randomNumber = random.randint(1000,9999)
				subject = 'One Time Password For Your Account'
				message = 'Your OTP Is=>'+str(randomNumber)
				email_from = settings.EMAIL_HOST_USER   		
				send_mail( subject, message, email_from, mail_to)    				
				Otp=OTP(User_Name=data,Otp=randomNumber)
				Otp.save()
				context={'email':res,'user_name':data}
				return render(request,"OTP_Ver.html",context)  	
		except Exception as e:  
			context={'title': ' Username Not Found'}
			return render(request, 'index.html',context)			
	def Ver_Otp(request):
		otp=request.POST.get("otp_no-1")
		otp+=request.POST.get("otp_no-2")
		otp+=request.POST.get("otp_no-3")
		otp+=request.POST.get("otp_no-4")
		user_name=request.POST.get("user_name")
		Otp_tb=OTP.objects.get(User_Name=user_name)		
		if(otp==str(Otp_tb.Otp)):			
			Otp_tb.delete()
			context={'user_name':user_name}
			return render(request,"Password_Change.html",context) 
		else:	
			context={"result":"Invaild OTP",'user_name':user_name}
			return render(request,"OTP_Ver.html",context)			  	 
	def change_password(request):	
		new_password=request.POST.get("password")
		user_name=request.POST.get("user_name")
		user=User.objects.get(username=user_name)
		user.set_password(new_password)
		user.save()
		return render(request,'index.html')
	def Back_to_Admin(request):
		return render(request,"Admin_Home_Page.html") 
	def Back_to_Staff(request):
		Date=datetime.date.today()
		Staff=Staff_Details.objects.all().filter(User_Name=request.user)
		context={'Staff_det':Staff,'Date':Date}
		return render(request,"Staff_Home_Page.html",context)
	def logout(request):
		return render(request,"index.html")			
class Staff_All:
	def Display_Staff(request):
		Staff=Staff_Details.objects.all().values()
		#template=loader.get_template("Table_print.html")
		context={"Staff_det":Staff}
		#return HttpResponse(template.render(context)) 
		return render(request,"Display_Staff_Info.html",context)
	def Add_Staff(request): 
		all_users=User.objects.all().values('username')
		all_users=list(all_users)
		user=[]
		for i in range (len(all_users)):
			user.append(all_users[i]["username"])
		context={'title':user}		
		if request.method == 'POST' and request.FILES['upload']:
			upload = request.FILES['upload']
			fss = FileSystemStorage()
			file = fss.save('images/Staff_Images/'+upload.name, upload)
			file_url = fss.url(file)
			User_Name=request.POST.get("User_Name")
			User_password=request.POST.get("User_Password")
			staff_id=request.POST.get("Staff ID")
			staff_name=request.POST.get("Staff Name")
			staff_dep=request.POST.get("Staff Department")
			staff_Mail=request.POST.get("Staff Mail_ID")
			staff_Phone=request.POST.get("Staff Phone_No")			
			staff=Staff_Details(User_Name=User_Name,
			Staff_ID=staff_id,Name=staff_name,
			Department=staff_dep,Mail_ID=staff_Mail,
			Photo='images/Staff_Images/'+upload.name,Phone_Number=staff_Phone)
			user=User.objects.create_user(username=User_Name,
			first_name=staff_name,email=staff_Mail,
			password=User_password)
			Grouped = Group.objects.get(name="Staff_Group") 
			user.groups.add(Grouped)
			staff.save()
			user.save()	
			return render(request, 'Staff_Info.html',context)
		return render(request, 'Staff_Info.html',context)
	def Update_Staff(request):
		ID=request.POST.get("tsid")
		user_name=request.POST.get("usr_name")
		user=User.objects.get(username=user_name)
		user.first_name=request.POST.get("tsname")
		user.email=request.POST.get("tsmail")
		user.save()		
		staff = Staff_Details.objects.get(Staff_ID =ID)
		staff.Name=request.POST.get("tsname")
		staff.Department=request.POST.get("tsdep")
		staff.Mail_ID=request.POST.get("tsmail")
		staff.Phone_Number=request.POST.get("tsphone")	
		staff.save()
		return HttpResponse("Row Edited")
	def Remove_Staff(request):
		usr_name=request.POST.get("usr_name")
		staff = Staff_Details.objects.get(User_Name=usr_name)
		staff.delete()
		ID=User.objects.get(username=usr_name).pk
		Grouped = Group.objects.get(name="Staff_Group")
		Grouped.user_set.remove(ID)
		user = User.objects.filter(username=usr_name)
		user.delete()
		return HttpResponse("Row Deleted")
	def Staff_Mark_Attendance(request):
		Date=datetime.date.today()
		Sem=Sem_Days.objects.get(id="1")
		choice="Mark"
		if(Sem.Date!=Date):
			Sem.Working_Days=Sem.Working_Days+1
			Sem.Date=Date
			Sem.save()
		Date=request.POST.get("Date")
		Degree=request.POST.get("Degree")
		Year=request.POST.get("Year")
		department=request.POST.get("Department")
		Hour=request.POST.get("Hour")
		Check_Hour=Hour+"__contains"
		print(Date,Degree,Year,department,Hour,sep="-")
		Student=Student_Details.objects.filter(Year=Year,Degree=Degree,Department=department).values()		
		for i in range(len(Student)):
			Student_Att=Facial_Students_Attendance.objects.filter(Date=Date,Student_Regno=Student[i]["Regno"],**{Check_Hour:"AB"}).values()		
			if len(Student_Att)!=0:
				Student[i]["Edit_Att"]="AB"
				choice="Edit"
			else:
				Student[i]["Edit_Att"]="-"
		context={"Student_det":Student,"Date":Date,"Degree":Degree,"Year":Year,"department":department,"Hour":Hour,"Choice":choice}
		return render(request,"Student_Mark_Attendance.html",context)
	def Staff_Save_Attendance(request):
		Absent_Student=[]
		Regno=""
		count=0
		Date=request.POST.get("Date")
		Degree=request.POST.get("Degree")
		Year=request.POST.get("Year")
		department=request.POST.get("Department")
		Hour=request.POST.get("Hour")
		Choice=request.POST.get("Choice")		
		Absent_list=request.POST.get("Absent_Student")
		Staff=Staff_Details.objects.filter(User_Name=request.user).values("Staff_ID")
		print(Date,Degree,Year,department,Hour,Absent_list,Choice,sep="-")
		for i in list(Absent_list):
			Regno+=i
			count+=1
			if(count==8):
				Absent_Student.append(Regno)
				count=0
				Regno=""
		if Choice=="Mark":
			for x in Absent_Student:
				if(len(list(Students_Attendance.objects.filter(Date=Date,Student_Regno_id=x).values()))==0):
					if Hour=="HR_1":				
						Student=Student_Details.objects.filter(Regno=x).values("Name")
						Student_Attendance=Students_Attendance(Staff_ID=str(Staff[0]["Staff_ID"]),
						Student_Name=str(Student[0]["Name"]),Date=Date,Student_Regno_id=x,HR_1="AB",HR_2="-",HR_3="-",HR_4="-",HR_5="-",Degree=Degree)
						Student_Attendance.save()
					elif Hour=="HR_2":				
						Student=Student_Details.objects.filter(Regno=x).values("Name")
						Student_Attendance=Students_Attendance(Staff_ID=str(Staff[0]["Staff_ID"]),
						Student_Name=str(Student[0]["Name"]),Date=Date,Student_Regno_id=x,HR_2="AB",HR_1="-",HR_3="-",HR_4="-",HR_5="-",Degree=Degree)
						Student_Attendance.save()
					elif Hour=="HR_3":				
						Student=Student_Details.objects.filter(Regno=x).values("Name")
						Student_Attendance=Students_Attendance(Staff_ID=str(Staff[0]["Staff_ID"]),
						Student_Name=str(Student[0]["Name"]),Date=Date,Student_Regno_id=x,HR_3="AB",HR_2="-",HR_1="-",HR_4="-",HR_5="-",Degree=Degree)
						Student_Attendance.save()
					elif Hour=="HR_4":				
						Student=Student_Details.objects.filter(Regno=x).values("Name")
						Student_Attendance=Students_Attendance(Staff_ID=str(Staff[0]["Staff_ID"]),
						Student_Name=str(Student[0]["Name"]),Date=Date,Student_Regno_id=x,HR_4="AB",HR_2="-",HR_3="-",HR_1="-",HR_5="-",Degree=Degree)
						Student_Attendance.save()
					else:				
						Student=Student_Details.objects.filter(Regno=x).values("Name")
						Student_Attendance=Students_Attendance(Staff_ID=str(Staff[0]["Staff_ID"]),
						Student_Name=str(Student[0]["Name"]),Date=Date,Student_Regno_id=x,HR_5="AB",HR_2="-",HR_3="-",HR_4="-",HR_1="-",Degree=Degree)
						Student_Attendance.save()
				elif Hour=="HR_1":	
						Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_1="AB"
						Student_Attendance.save()
				elif Hour=="HR_2":				
						Student_Attendance = Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_2="AB"
						Student_Attendance.save()
				elif Hour=="HR_3":				
						Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_3="AB"
						Student_Attendance.save()
				elif Hour=="HR_4":				
						Student_Attendance = Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_4="AB"
						Student_Attendance.save()
				else:				
						Student_Attendance = Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_5="AB"
						Student_Attendance.save()
		else:
			for x in Absent_Student:
				if Hour=="HR_1":
					Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
					if(Student_Attendance.HR_1=="AB"):	
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_1="-"
						Student_Attendance.save()
					else:
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_1="AB"
						Student_Attendance.save()
				elif Hour=="HR_2":				
					Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
					if(Student_Attendance.HR_2=="AB"):	
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_2="-"
						Student_Attendance.save()
					else:
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_2="AB"
						Student_Attendance.save()
				elif Hour=="HR_3":				
					Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
					if(Student_Attendance.HR_3=="AB"):	
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_3="-"
						Student_Attendance.save()
					else:
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_3="AB"
						Student_Attendance.save()
				elif Hour=="HR_4":				
					Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
					if(Student_Attendance.HR_4=="AB"):	
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_4="-"
						Student_Attendance.save()
					else:
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_4="AB"
						Student_Attendance.save()
				else:				
					Student_Attendance =Students_Attendance.objects.get(Date=Date,Student_Regno_id=x)			
					if(Student_Attendance.HR_5=="AB"):	
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_5="-"
						Student_Attendance.save()
					else:
						Student_Attendance.Staff_ID=str(Staff[0]["Staff_ID"])
						Student_Attendance.HR_5="AB"
						Student_Attendance.save()
		Staff=Staff_Details.objects.all().filter(User_Name=request.user)
		context={'Staff_det':Staff,'Date':datetime.date.today()}
		return render(request,"Staff_Home_Page.html",context)		
class Student_All:
	def Student(request):
		Working_Days=Sem_Days.objects.filter(id="1").values()
		Working_Days=Working_Days[0]["Working_Days"]
		context={"Working_Days":Working_Days}
		return render(request,"Student.html",context)
	def Display_Student(request):
		grad=request.POST.get("Grad")
		year=request.POST.get("Year")
		dep=request.POST.get("Dep")
		Grad=request.GET.get("degree")
		Year=request.GET.get("year")
		Dep=request.GET.get("dep")
		if grad:
			if(year=="First Year(I)"):
				year="I"
			elif(year=="Second Year(II)"):
				year="II"
			else:
				year="III"
			if(grad=="Under Graduate(UG)"):
				grad="UG"				
			else:
				grad="PG"
			Student=Student_Details.objects.filter(Year=year,Department=dep,Degree=grad).values()
			context={"Student_det":Student,"Grad":grad,"Year":year,"Dep":dep}
		else:
			Student=Student_Details.objects.filter(Year=year,Department=dep,Degree=Grad).values()
			context={"Student_det":Student,"Grad":Grad,"Year":Year,"Dep":Dep}
		return render(request,"Display_Student_Info.html",context)
	def Add_Student(request): 
		all_users=User.objects.all().values('username')
		all_users=list(all_users)
		user=[]		
		for i in range (len(all_users)):
			user.append(all_users[i]["username"])
		context={'title':user}			
		if request.method == 'POST':
			grad=request.POST.get("degree")
			year=request.POST.get("year")
			dep=request.POST.get("dep")
			User_Name=request.POST.get("User_Name")
			User_password=request.POST.get("User_Password")
			reg_no=request.POST.get("Student Reg")
			name=request.POST.get("Student Name")
			DOB=request.POST.get("Student DOB")
			gender=request.POST.get("Gender")
			degree=request.POST.get("Degree")
			year=request.POST.get("year")
			dep=request.POST.get("Student Department")
			Mail=request.POST.get("Student Mail_ID")
			Phone=request.POST.get("Student Phone_No")
			context={'title':user,'Grad':grad,'Year':year,'Dep':dep}			
			student=Student_Details(User_Name=User_Name,Regno=reg_no,Name=name,DOB=DOB,Gender=gender,
			Degree=degree,Year=year,Department=dep,Phone_Number=Phone,Mail_ID=Mail)
			student.save()
			Student_Backup=Students_Backup(Name=name,Phone_Number=Phone,Regno=reg_no,Degree=degree)
			Student_Backup.save()
			user=User.objects.create_user(username=User_Name,
			first_name=name,email=Mail,
			password=User_password)
			Grouped = Group.objects.get(name="Student_Group") 
			user.groups.add(Grouped)
			user.save()
			return render(request,'Student_Info.html',context)
		return render(request,'Student_Info.html',context)
	def Update_Student(request):
		regno=request.POST.get("streg")
		Grad=request.POST.get("Grad")
		user_name=request.POST.get("usr_name")
		user=User.objects.get(username=user_name)
		user.first_name=request.POST.get("stname")
		user.email=request.POST.get("stmail")
		user.save()
		student=Student_Details.objects.get(Regno=regno)		
		student.Name=request.POST.get("stname")
		student.DOB=request.POST.get("stDOB")
		student.Gender=request.POST.get("stgen")
		student.Mail_ID=request.POST.get("stmail")
		student.Phone_Number=request.POST.get("stphone")	
		student.save()			
		return HttpResponse("Row Edited")
	def Remove_Student(request):
		usr_name=request.POST.get("usr_name")
		Degree=request.POST.get("degree")
		regno=request.POST.get("Regno")
		student =Student_Details.objects.get(User_Name=usr_name)
		student.delete()
		Student_Backup =Students_Backup.objects.get(Regno=regno)
		Student_Backup.delete()
		ID=User.objects.get(username=usr_name).pk
		Grouped = Group.objects.get(name="Student_Group")
		Grouped.user_set.remove(ID)
		user = User.objects.filter(username=usr_name)
		user.delete()
		return HttpResponse("Row Deleted")
	def Admin_Edit_Attendance(request):
		grad=request.GET.get("degree")
		year=request.GET.get("year")
		dep=request.GET.get("dep")
		context={"Grad":grad,"Year":year,"Dep":dep}
		if request.method == 'POST':
			grad=request.POST.get("grad")
			year=request.POST.get("year")
			dep=request.POST.get("dep")
			date=request.POST.get("date")
			regno=request.POST.get("Regno")
			Student=Students_Attendance.objects.filter(Date=date,Degree=grad,Student_Regno_id=regno).values()
			context={"Student_det":list(Student)}
			return JsonResponse(context)
		return render(request,"Student_Edit_Attendance.html",context)
	def Admin_Edited_Mark_Attendance(request):
		def check(Table,Date,Regno,HR_1,HR_2,HR_3,HR_4,HR_5):
			Attendance=Table.objects.get(Date=Date,Student_Regno_id=Regno)		
			if(HR_1=="Present"):				
				Attendance.HR_1="-"
				Attendance.save()
			elif(HR_1=="Absent"):		
				Attendance.HR_1="AB"
				Attendance.save()
			elif(HR_1=="ML"):		
				Attendance.HR_1="ML"
				Attendance.save()
			else:		
				Attendance.HR_1="OD"
				Attendance.save()
			if(HR_2=="Present"):				
				Attendance.HR_2="-"
				Attendance.save()
			elif(HR_2=="Absent"):							
				Attendance.HR_2="AB"
				Attendance.save()
			elif(HR_2=="ML"):		
				Attendance.HR_2="ML"
				Attendance.save()
			else:							
				Attendance.HR_2="OD"
				Attendance.save()
			if(HR_3=="Present"):					
				Attendance.HR_3="-"
				Attendance.save()
			elif(HR_3=="Absent"):						
				Attendance.HR_3="AB"
				Attendance.save()
			elif(HR_3=="ML"):		
				Attendance.HR_3="ML"
				Attendance.save()
			else:							
				Attendance.HR_3="OD"
				Attendance.save()
			if(HR_4=="Present"):					
				Attendance.HR_4="-"
				Attendance.save()
			elif(HR_4=="Absent"):							
				Attendance.HR_4="AB"
				Attendance.save()
			elif(HR_4=="ML"):		
				Attendance.HR_4="ML"
				Attendance.save()
			else:							
				Attendance.HR_4="OD"
				Attendance.save()
			if(HR_5=="Present"):							
				Attendance.HR_5="-"
				Attendance.save()
			elif(HR_5=="Absent"):		
				Attendance.HR_5="AB"
				Attendance.save()
			elif(HR_5=="ML"):		
				Attendance.HR_5="ML"
				Attendance.save()
			else:		
				Attendance.HR_5="OD"
				Attendance.save()			
		HR_1=request.POST.get("Hour_1")
		HR_2=request.POST.get("Hour_2")
		HR_3=request.POST.get("Hour_3")
		HR_4=request.POST.get("Hour_4")
		HR_5=request.POST.get("Hour_5")
		grad=request.POST.get("grad")
		year=request.POST.get("year")
		dep=request.POST.get("dep")
		regno=request.POST.get("Regno")
		date=request.POST.get("Date")
		context={"Grad":grad,"Year":year,"Dep":dep}
		print(HR_1,HR_2,HR_3,HR_4,HR_5,grad,year,dep,regno,date)
		check(Students_Attendance,date,regno,HR_1,HR_2,HR_3,HR_4,HR_5)
		return render(request,"Student_Edit_Attendance.html",context)
	def Attendance_Average(request):
		Degree=request.POST.get("Avg_Degree")
		Days=request.POST.get("Avg_Days")
		Student=Student_Details.objects.filter(Degree=Degree).values()	
		Student_Attendance=Students_Attendance.objects.filter(Degree=Degree).values()			
		for i in Student:							
				if(i["Regno"] in str(Student_Attendance)):
					count=0
					for j in Student_Attendance:
						if(i["Regno"]==j["Student_Regno_id"] and (j["HR_1"]=="AB" or j["HR_2"]=="AB" or j["HR_3"]=="AB")):
							count+=0.5
						if(i["Regno"]==j["Student_Regno_id"] and (j["HR_4"]=="AB" or j["HR_5"]=="AB")):
							count+=0.5
					Attendance=round(((int(Days)-count)/int(Days))*100,2)
					i["Attendance"]=Attendance
				else:
					Attendance=100.0
					i["Attendance"]=Attendance
		context={"Student_det":Student,"Degree":Degree}	
		return render(request,"Attendance_Average.html",context)
	def Caution_Mail(request):
		Mail_list=[]
		Regno=""
		count=0
		for i in (request.POST.get("Avg_list")):
			Regno+=i
			count+=1
			if(count==8):
				Mail_list.append(Regno)
				count=0
				Regno=""
		print(Mail_list)
		for x in  Mail_list:
			Student=Student_Details.objects.get(Regno=x)
			mail_to=[]
			mail_to.append(Student.Mail_ID) 		    		
			subject = 'Attendance Caution Mail !'
			message = "Dear Student, We are writing this letter to inform you about your short attendance in classes, and we are afraid to inform you that if your attendance is less than 60%, you will not be allowed to give your final examination. It is an alarming, and serious situation for you."
			email_from = settings.EMAIL_HOST_USER   		    			
			send_mail( subject, message, email_from, mail_to)			
		return HttpResponse("Mail Sended")
	def Backup_Student_Data(request):
		def Backup(deg,year,sem):
			Student=Student_Details.objects.filter(Degree=deg,Year=year).values()	
			Student_Attendance=Students_Attendance.objects.filter(Degree=deg).values()
			for i in Student:	
				Student_Backup=Students_Backup.objects.get(Regno=i["Regno"])									
				if(i["Regno"] in str(Student_Attendance)):
					count=0						
					for j in Student_Attendance:
						if(i["Regno"]==j["Student_Regno_id"] and (j["HR_1"]=="AB" or j["HR_2"]=="AB" or j["HR_3"]=="AB")):
							count+=0.5
						if(i["Regno"]==j["Student_Regno_id"] and (j["HR_4"]=="AB" or j["HR_5"]=="AB")):
							count+=0.5
						Attendance=round(((int(Working_Days)-count)/int(Working_Days))*100,2)		
				else:
					Attendance=100.0
				Student_Backup.Attendance[sem]=Attendance
				Student_Backup.save()
				Attendance=Students_Attendance.objects.filter(Student_Regno_id=i["Regno"])
				Attendance.delete()
		Year=request.POST.get("year")
		Sem=request.POST.get("sem") 
		Degree=request.POST.get("Degree")
		Working_Days=Sem_Days.objects.filter(id="1").values()
		Working_Days=Working_Days[0]["Working_Days"]
		print(Year,Degree,Working_Days,Sem,sep="#")
		if(Degree=="UG"):
			if(Year=="III"):
				if(Sem=="Sem_5"):
					Backup(Degree,Year,Sem)
				else:
					Backup(Degree,Year,Sem)
					Delete_Student=Student_Details.objects.filter(Degree=Degree,Year=Year)
					for x in Delete_Student:
						ID=User.objects.get(username=x.User_Name).pk
						Grouped = Group.objects.get(name="Student_Group")
						Grouped.user_set.remove(ID)
						user = User.objects.filter(username=x.User_Name)
						user.delete()
					Delete_Student.delete()
			elif(Year=="II"):
				if(Sem=="Sem_3"):
					Backup(Degree,Year,Sem)
				else:
					Backup(Degree,Year,Sem)
					Student=Student_Details.objects.filter(Degree=Degree,Year=Year).values()	
					for i in Student:	
						Student_Upgrade=Student_Details.objects.get(Regno=i["Regno"])
						Student_Upgrade.Year="III"
						Student_Upgrade.save()
			elif(Year=="I"):
				if(Sem=="Sem_1"):
					Backup(Degree,Year,Sem)
				else:
					Backup(Degree,Year,Sem)
					Student=Student_Details.objects.filter(Degree=Degree,Year=Year).values()	
					for i in Student:	
						Student_Upgrade=Student_Details.objects.get(Regno=i["Regno"])
						Student_Upgrade.Year="II"
						Student_Upgrade.save()
		else:
			if(Year=="II"):
				if(Sem=="Sem_3"):
					Backup(Degree,Year,Sem)
				else:
					Backup(Degree,Year,Sem)
					Delete_Student=Student_Details.objects.filter(Degree=Degree,Year=Year)
					for x in Delete_Student:
						ID=User.objects.get(username=x.User_Name).pk
						Grouped = Group.objects.get(name="Student_Group")
						Grouped.user_set.remove(ID)
						user = User.objects.filter(username=x.User_Name)
						user.delete()
					Delete_Student.delete()
			elif(Year=="I"):
				if(Sem=="Sem_1"):
					Backup(Degree,Year,Sem)
				else:
					Backup(Degree,Year,Sem)	
					Student=Student_Details.objects.filter(Degree=Degree,Year=Year).values()	
					for i in Student:	
						Student_Upgrade=Student_Details.objects.get(Regno=i["Regno"])
						Student_Upgrade.Year="II"
						Student_Upgrade.save()								
		return HttpResponse("Data Backuped")
	def Display_Backup(request):
		Degree=request.POST.get("Backup_Display_Degree")
		Backup_Details=Students_Backup.objects.filter(Degree=Degree).values()
		context={"Backup_Details":Backup_Details,"Degree":Degree}
		return render(request,"Display_Backup.html",context)
# Create your viwes here.conte    



    
