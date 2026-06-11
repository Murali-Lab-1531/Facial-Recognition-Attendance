import mysql.connector
from datetime import date

conn = mysql.connector.connect(host="localhost",user="root",password="murali1531",database="murali" )
cursor= conn.cursor()
query = "select * from student_details"
cursor.execute(query)
     # Fetch all rows from the result 
records = cursor.fetchall()
Face_Id="100"
Hour=2
# Print row by row
for row in records: 
    if((row[1][-3:])==Face_Id):
        if(Hour==1): 
            sql = "INSERT facial_students_attendance (Face_id, Student_Name, Degree, Date,HR_1,HR_2,HR_3,HR_4 ,HR_5, Student_Regno) VALUES (%s, %s, %s,%s, %s, %s, %s,%s, %s,%s)"
            values = (Face_Id,row[2],row[5],date.today(),"-","AB","AB","AB","AB",row[1])  # Sample values
            cursor.execute(sql, values)
            conn.commit()
        elif(Hour==2):
           sql = "UPDATE facial_students_attendance SET HR_2 = %s WHERE Face_id = %s"
           values = ("-", Face_Id)  # New value and condition
           cursor.execute(sql, values)
           conn.commit()
        elif(Hour==3):
           sql = "UPDATE facial_students_attendance SET HR_3 = %s WHERE Face_id = %s"
           values = ("-", Face_Id)  # New value and condition
           cursor.execute(sql, values)
           conn.commit()
        elif(Hour==4):
           sql = "UPDATE facial_students_attendance SET HR_4 = %s WHERE Face_id = %s"
           values = ("-", Face_Id)  # New value and condition
           cursor.execute(sql, values)
           conn.commit()
        elif(Hour==5):
           sql = "UPDATE facial_students_attendance SET HR_5 = %s WHERE Face_id = %s"
           values = ("-", Face_Id)  # New value and condition
           cursor.execute(sql, values)
           conn.commit()
           
cursor.close()
conn.close()

222222222222222222222222222222222222222222222222222222222222222222222222222222222222222


at