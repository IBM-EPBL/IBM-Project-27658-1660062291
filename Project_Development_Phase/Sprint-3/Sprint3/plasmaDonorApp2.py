
from flask import Flask, render_template, request, redirect, url_for, session,g
from flask import *
from turtle import st
#from markupsafe import escape
import os
from flask_session import Session

import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31498;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jpj12319;PWD=Y6lfqPCAknS6P6LB",'','')



app = Flask(__name__)
SESSION_TYPE = "filesystem"
PERMANENT_SESSION_LIFETIME = 1800

app.config.update(SECRET_KEY=os.urandom(24))

app.config.from_object(__name__)
Session(app)

if __name__ == "__main__":
    with app.test_request_context("/"):
        session["key"] = "value" 
    app.run(host='0.0.0.0', port=5000, debug=True)    

@app.route('/')
def index():
    return render_template('/signin.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin',methods=['GET', 'POST'])
def signin():
    return render_template('signin.html')












@app.route('/dashboard')
def dashboard():
        email = session['email']
        name=session['user'] 
        bloodgroup=session['bloodgroup'] 
        city=session['city'] 
        role="bene" 
        bene_status="requested"

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        #data=(("Deabcdefr","Abcdefghi","O+","abcde@gmail.com","Bangalore"),("First Name","Last Name","BloodGroup","Email","City"))
        #donor_data=(("Deabcdefr","Abcdefghi","O+","abcde@gmail.com","Bangalore"),)
        #bene_data=(("First Name","Last Name","BloodGroup","Email","City"),("First Name","Last Name","BloodGroup","Email","City"))
      

        userslist = []
        sql = "SELECT NAME,LASTNAME,EMAIL,PHONE,ADDRESS,CITY,AGE,BLOODGROUP FROM SIGNUP_TABLE WHERE role=? AND beneficiary_status=? AND city=? AND bloodgroup=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,role)
        ibm_db.bind_param(stmt,2,bene_status)
        ibm_db.bind_param(stmt,3,city)
        ibm_db.bind_param(stmt,4,bloodgroup)
        #stmt = ibm_db.exec_immediate(conn, sql) 
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)
        if userslist:                       
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=session['user'],email=session['email'],role=session['role'],beneficiary_status=session['beneficiary_status']) 
        
        return render_template('dashboard.html',requesters_list=userslist,headings=headings,role=session['role'],beneficiary_status=session['beneficiary_status'])




@app.route('/all_requests',methods = ['POST', 'GET'])
def all_requests():
    if request.method=="POST":
        email = session['email']
        name=session['user'] 
        bloodgroup=session['bloodgroup'] 
        city=session['city'] 
        role="bene" 
        bene_status="requested"

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        #data=(("Deabcdefr","Abcdefghi","O+","abcde@gmail.com","Bangalore"),("First Name","Last Name","BloodGroup","Email","City"))
        #donor_data=(("Deabcdefr","Abcdefghi","O+","abcde@gmail.com","Bangalore"),)
        #bene_data=(("First Name","Last Name","BloodGroup","Email","City"),("First Name","Last Name","BloodGroup","Email","City"))
      

        userslist = []
        sql = "SELECT NAME,LASTNAME,EMAIL,PHONE,ADDRESS,CITY,AGE,BLOODGROUP FROM SIGNUP_TABLE WHERE role=? AND beneficiary_status=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,role)
        ibm_db.bind_param(stmt,2,bene_status)
        #ibm_db.bind_param(stmt,3,city)
        #ibm_db.bind_param(stmt,4,bloodgroup)
        #stmt = ibm_db.exec_immediate(conn, sql) 
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)
        if userslist:                       
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=session['user'],email=session['email'],role=session['role'],beneficiary_status=session['beneficiary_status']) 
        
        return render_template('dashboard.html',requesters_list=userslist,headings=headings,role=session['role'],beneficiary_status=session['beneficiary_status'])




@app.route('/saved_requests',methods = ['POST', 'GET'])
def saved_requests():
    if request.method=="POST":
        email = session['email']
        name=session['user'] 
        bloodgroup=session['bloodgroup'] 
        city=session['city'] 
        role="bene" 
        bene_status="requested"

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        
      

        userslist = []
        sql = "SELECT S.NAME,S.LASTNAME,S.EMAIL,S.PHONE,S.ADDRESS,S.CITY,S.AGE,S.BLOODGROUP FROM SIGNUP_TABLE AS S  INNER JOIN BENEFICIARY_REQUEST_TABLE AS B ON B.BENEFICIARY_EMAIL=S.EMAIL AND B.DONOR_EMAIL=? "
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,email)
        #ibm_db.bind_param(stmt,2,bene_status)
        #ibm_db.bind_param(stmt,3,city)
        #ibm_db.bind_param(stmt,4,bloodgroup)
        #stmt = ibm_db.exec_immediate(conn, sql) 
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)
        if userslist:                       
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=session['user'],email=session['email'],role=session['role'],beneficiary_status=session['beneficiary_status']) 
        
        return render_template('dashboard.html',requesters_list=userslist,headings=headings,role=session['role'],beneficiary_status=session['beneficiary_status'])







@app.route('/save_button', methods = ['POST', 'GET'])
def save_button():  


    if request.method == 'POST':

        email = session['email']
        name=session['user'] 
        bloodgroup=session['bloodgroup'] 
        city=session['city'] 
        role="bene" 
        bene_status="requested"
        donor=session['email'] 
        bene_name= request.form['bene_name']
        bene_email= request.form['bene_email']

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        
      

        userslist = []
        sql = "SELECT NAME,LASTNAME,EMAIL,PHONE,ADDRESS,CITY,AGE,BLOODGROUP FROM SIGNUP_TABLE WHERE role=? AND beneficiary_status=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,role)
        ibm_db.bind_param(stmt,2,bene_status)
        #ibm_db.bind_param(stmt,3,city)
        #ibm_db.bind_param(stmt,4,bloodgroup)
        #stmt = ibm_db.exec_immediate(conn, sql) 
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)      


        sql2 = "SELECT * FROM BENEFICIARY_REQUEST_TABLE WHERE BENEFICIARY_EMAIL=? AND DONOR_EMAIL=?"
        stmt2 = ibm_db.prepare(conn, sql2)
        ibm_db.bind_param(stmt2,1,bene_email)
        ibm_db.bind_param(stmt2,2,donor)
        ibm_db.execute(stmt2)
        account = ibm_db.fetch_assoc(stmt2)

        if account and userslist:
            #flash("User already exists,please sign in directly..")
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=session['user'],email=session['email'],role=session['role'],beneficiary_status=session['beneficiary_status'])
            return render_template('dashboard.html',user=session['user'],email=session['email'],role=session['role'])
            
        
        #enter dashboard if new user registers for first time

        else:
         
            insert_sql = "INSERT INTO BENEFICIARY_REQUEST_TABLE(BENEFICIARY_EMAIL,DONOR_EMAIL) VALUES (?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, bene_email)
            ibm_db.bind_param(prep_stmt, 2, donor) 
            ibm_db.execute(prep_stmt) 
           
        #return render_template('dashboard.html', user=session['user'],email=session['email'],role=session['role']) 
        return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=session['user'],email=session['email'],role=session['role'],beneficiary_status=session['beneficiary_status'])
       




@app.route('/contact',methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/profile',methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')

@app.route('/home',methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/fromsignup', methods = ['POST', 'GET'])
def fromsignup():  


    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password'] 
        isdonor=request.form['role']
        #print(isdonor)
       # pin = request.form['pin']

        sql = "SELECT * FROM SIGNUP_TABLE WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        #enter sign in page from the sign-up page if user already exist--check by email address only
        

        if account:
            #flash("User already exists,please sign in directly..")
            return render_template('signin.html', msg="You are already a member, please login using your details")
        
        #enter dashboard if new user registers for first time

        else:
            insert_sql = "INSERT INTO SIGNUP_TABLE(NAME,EMAIL,PASSWORD,ROLE) VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, isdonor)
            #ibm_db.bind_param(prep_stmt, 4, isdonor)
            #ibm_db.bind_param(prep_stmt, 4, pin)
            ibm_db.execute(prep_stmt) 
            
        #flash("Registration successful..")    
        return render_template('signin.html', msg="Register success..Please login ito app now..")

@app.route('/fromsignin', methods = ['POST', 'GET'])
  
def fromsignin():

    if request.method == 'POST':

        session.pop('user',None)
        #name and confirm password are not in sign in page form
        #name = request.form['name']
        email = request.form['email']
        password = request.form['password']
       # pin = request.form['pin']

        userslist = []
        sql = "SELECT * FROM SIGNUP_TABLE WHERE email=? AND password=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        #stmt = ibm_db.exec_immediate(conn, sql) 
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            userslist.append(dictionary)
            #fetched_name=dictionary[0] ...table colums-- name,email,password
            session['user']=dictionary[0] 
            session['email']=dictionary[1] 
            session['password']=dictionary[2] 
            session['role']=dictionary[3]
            session['lastname']=dictionary[4]
            session['phone']=dictionary[5]
            session['address']=dictionary[6]
            session['city']=dictionary[7]
            session['bio']=dictionary[8]
            session['height']=dictionary[9]
            session['weight']=dictionary[10]
            session['age']=dictionary[11]
            session['bloodgroup']=dictionary[12]
            session['beneficiary_status']=dictionary[13] 
            


            dictionary = ibm_db.fetch_both(stmt)
        if userslist:            
            #if g.user:   
                #flash("Login successful..")            
            return render_template('profile.html', user=session['user'],email=session['email'],password=session['password'],role=session['role'],msg="Login successful..") 
            
        else:
            sql2 = "SELECT * FROM SIGNUP_TABLE WHERE email =?"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.bind_param(stmt2,1,email)        
            ibm_db.execute(stmt2)
            account2 = ibm_db.fetch_assoc(stmt2) 
            if account2: 
                #flash("Re-enter password correctly..")                          
                return render_template('signin.html', msg="Wrong Password!!Reneter") 
        #flash("Register before signing in..")    
        return render_template('signup.html', msg="Register now!And then sign in..") 

    else:
        return render_template('signin.html')


@app.route('/change_password',methods = ['POST', 'GET']) 
  
def change_password(): 
    if request.method == 'POST':

        newpassword = request.form['newpass']
      
        sql = "UPDATE SIGNUP_TABLE SET password=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newpassword) 
        ibm_db.bind_param(stmt,2,session['email'])
        
        ibm_db.execute(stmt)
        
        session['password']=newpassword 
        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=session['user'],email=session['email'],password=session['password'],msg="Password updated successfully") 
            

@app.route('/change_to_requested_status',methods = ['POST', 'GET']) 
  
def change_to_requested_status(): 
    if request.method == 'POST':

        newstatus = "requested"
      
        sql = "UPDATE SIGNUP_TABLE SET BENEFICIARY_STATUS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newstatus) 
        ibm_db.bind_param(stmt,2,session['email'])
        
        ibm_db.execute(stmt)
        
        session['beneficiary_status']=newstatus
        #flash("Password updated successfully!!")    

    
    return render_template('dashboard.html', user=session['user'],email=session['email'],password=session['password'],msg="",beneficiary_status="requested") 
            

@app.route('/change_to_none_status',methods = ['POST', 'GET']) 
  
def change_to_none_status(): 
    if request.method == 'POST':

        newstatus = ""
      
        sql = "UPDATE SIGNUP_TABLE SET BENEFICIARY_STATUS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newstatus) 
        ibm_db.bind_param(stmt,2,session['email'])
        
        ibm_db.execute(stmt)
        
        session['beneficiary_status']=newstatus 
        #flash("Password updated successfully!!")    

    
    return render_template('dashboard.html', user=session['user'],email=session['email'],password=session['password'],msg="",beneficiary_status="") 
            

@app.route('/update_account_settings',methods = ['POST', 'GET'])
def update_account_settings(): 
    if request.method == 'POST':

        newlastname = request.form['lastname']
        newphone = request.form['phone']
        newaddress = request.form['address']
        newcity = request.form['city']
        newbio = request.form['bio']
        
      
        sql = "UPDATE SIGNUP_TABLE SET LASTNAME=?,PHONE=?,ADDRESS=?,CITY=?,BIO=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newlastname) 
        ibm_db.bind_param(stmt,2,newphone)
        ibm_db.bind_param(stmt,3,newaddress)
        ibm_db.bind_param(stmt,4,newcity)
        ibm_db.bind_param(stmt,5,newbio)
        ibm_db.bind_param(stmt,6,session['email'])
        
        ibm_db.execute(stmt)
        
        
        session['lastname']=newlastname 
        session['phone']=newphone
        session['address']=newaddress
        session['city']=newcity
        session['bio']=newbio 

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=session['user'],email=session['email'],password=session['password'],msg="Account Settings updated successfully") 
            

@app.route('/change_bene_details',methods = ['POST', 'GET'])
def change_bene_details(): 
    if request.method == 'POST':

        newheight = request.form['b-height']
        newweight = request.form['b-weight']
        newbloodgroup = request.form['b-bloodgroup']
        newage = request.form['b-age']
        
        
      
        sql = "UPDATE SIGNUP_TABLE SET HEIGHT=?,WEIGHT=?,BLOODGROUP=?,AGE=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newheight) 
        ibm_db.bind_param(stmt,2,newweight)
        ibm_db.bind_param(stmt,3,newbloodgroup)
        ibm_db.bind_param(stmt,4,newage)
        ibm_db.bind_param(stmt,5,session['email'])
        
        ibm_db.execute(stmt)
        
        
        session['height']=newheight
        session['weight']=newweight
        session['bloodgroup']=newbloodgroup
        session['age']=newage
         

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=session['user'],email=session['email'],password=session['password'],msg="Your Details have been updated successfully") 
            

@app.route('/change_donor_details',methods = ['POST', 'GET'])
def change_donor_details(): 
    if request.method == 'POST':

        newheight = request.form['d-height']
        newweight = request.form['d-weight']
        newbloodgroup = request.form['d-bloodgroup']
        newage = request.form['d-age']
        newillnessdetails=request.form['illness']
        
        
      
        sql = "UPDATE SIGNUP_TABLE SET HEIGHT=?,WEIGHT=?,BLOODGROUP=?,AGE=?,ILLNESSDETAILS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newheight) 
        ibm_db.bind_param(stmt,2,newweight)
        ibm_db.bind_param(stmt,3,newbloodgroup)
        ibm_db.bind_param(stmt,4,newage)
        ibm_db.bind_param(stmt,5,newillnessdetails)
        ibm_db.bind_param(stmt,6,session['email'])
        
        ibm_db.execute(stmt)
        
        
        session['height']=newheight
        session['weight']=newweight
        session['bloodgroup']=newbloodgroup
        session['age']=newage 
        session['illnessdetails']=newillnessdetails
         

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=session['user'],email=session['email'],password=session['password'],msg="Your Details have been updated successfully") 
            




@app.before_request 
def before_request():
    g.user=None 

    if 'user' in session:
        g.user=session['user'] 

@app.route('/dropsession') 
def dropsession():
    session.pop('user',None) 
    return render_template('signin.html')


