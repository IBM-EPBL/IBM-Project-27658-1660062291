from flask import Flask, render_template, request, redirect, url_for, session,g,flash
from flask import *
from turtle import st
#from markupsafe import escape
import os
from flask_mail import Mail, Message
from flask_session import Session
from werkzeug.utils import secure_filename 

import ibm_boto3
from ibm_botocore.client import Config, ClientError 

import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qgg04661;PWD=qEkHZ0qIWgXpfBGF",'','')


COS_ENDPOINT="https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID="TW8n5tqjJaXs7dT2ri5TQg3DTBDBDhHMuhjsZFxXAoNo"
COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/d8d7bf47ea3c4175adb1c62d138fca79:ee3767d7-338e-4333-aafa-c43d9f532609::"

# Create resource https://s3.ap.cloud-object-storage.appdomain.cloud
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)



app = Flask(__name__)
SESSION_TYPE = "filesystem"
PERMANENT_SESSION_LIFETIME = 1200

#app.config.update(SECRET_KEY=os.urandom(24))

app.config.from_object(__name__)
Session(app) 
app.config['SECRET_KEY']=os.urandom(24) 
app.config['SESSION_COOKIE_NAME']="my_session"
#for files upload
app.config["UPLOAD_FOLDER"] = "static/images/"
#end for files upload 

#for mailing
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = "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"
app.config['MAIL_DEFAULT_SENDER'] = "anan19110.cs@rmkec.ac.in"
mail = Mail(app) 
#end for mailing




def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()

        print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))


def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names = []
        for file in files:
            files_names.append(file.key)
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
        return files_names
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))





def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )


        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
 

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

@app.route('/contact',methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/profile')
def profile():
    role=session.get('role')
    CERTIFICATE_UPLOADED=session.get('certificate_uploaded')

    return render_template('profile.html',role=role,CERTIFICATE_UPLOADED=CERTIFICATE_UPLOADED) 

@app.route('/home',methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
        email = session.get('email')
        name=session.get('user')
        bloodgroup=session.get('bloodgroup')
        city=session.get('city')
        role="bene" 
        bene_status="requested"
        beneficiary_status=session.get('beneficiary_status')
        curr_role=session.get('role')
        

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP","Covid-Certificate-uploaded")
        

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

        saveduserslist = []
        sql2 = "SELECT BENEFICIARY_EMAIL FROM BENEFICIARY_REQUEST_TABLE WHERE DONOR_EMAIL=?"
        stmt2=ibm_db.prepare(conn,sql2) 
        ibm_db.bind_param(stmt2,1,email)
        
        ibm_db.execute(stmt2) 
        dictionary2 = ibm_db.fetch_both(stmt2)
        while dictionary2 != False: 
            saveduserslist.append(dictionary2)            

            dictionary2 = ibm_db.fetch_both(stmt2)
        if userslist:                       
            return render_template('dashboard.html', saved_list=saveduserslist,requesters_list=userslist,headings=headings,user=name,email=email,role=curr_role,beneficiary_status=beneficiary_status) 
        
        return render_template('dashboard.html',saved_list=saveduserslist,requesters_list=userslist,headings=headings,role=curr_role,beneficiary_status=beneficiary_status)


@app.route('/all_requests',methods = ['POST', 'GET'])
def all_requests():
    if request.method=="POST":
        email = session.get('email')
        name=session.get('user') 
        bloodgroup=session.get('bloodgroup') 
        city=session.get('city')
        role="bene" 
        bene_status="requested"
        curr_role=session.get('role')
        beneficiary_status=session.get('beneficiary_status')

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        
        userslist = []
        sql = "SELECT NAME,LASTNAME,EMAIL,PHONE,ADDRESS,CITY,AGE,BLOODGROUP FROM SIGNUP_TABLE WHERE role=? AND beneficiary_status=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,role)
        ibm_db.bind_param(stmt,2,bene_status)       
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)
        if userslist:                       
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=name,email=email,role=curr_role,beneficiary_status=beneficiary_status) 
        
        return render_template('dashboard.html',requesters_list=userslist,headings=headings,role=curr_role,beneficiary_status=beneficiary_status)


@app.route('/saved_requests',methods = ['POST', 'GET'])
def saved_requests():
    if request.method=="POST":
        email = session.get('email')
        name=session.get('user')
        bloodgroup=session.get('bloodgroup') 
        city=session.get('city') 
        role="bene" 
        bene_status="requested"
        curr_role=session.get('role')
        beneficiary_status=session.get('beneficiary_status')

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        
      

        userslist = []
        sql = "SELECT S.NAME,S.LASTNAME,S.EMAIL,S.PHONE,S.ADDRESS,S.CITY,S.AGE,S.BLOODGROUP FROM SIGNUP_TABLE AS S  INNER JOIN BENEFICIARY_REQUEST_TABLE AS B ON B.BENEFICIARY_EMAIL=S.EMAIL AND B.DONOR_EMAIL=? "
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,email)
       
        ibm_db.execute(stmt) 
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            userslist.append(dictionary)            

            dictionary = ibm_db.fetch_both(stmt)
        if userslist:                       
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=name,email=email,role=curr_role,beneficiary_status=beneficiary_status) 
        
        return render_template('dashboard.html',requesters_list=userslist,headings=headings,role=curr_role,beneficiary_status=beneficiary_status)


@app.route('/save_button', methods = ['POST', 'GET'])
def save_button():  


    if request.method == 'POST':

        email = session.get('email')
        name=session.get('user') 
        bloodgroup=session.get('bloodgroup') 
        city=session.get('city') 
        role="bene" 
        bene_status="requested"
        donor=session.get('email') 
        bene_name= request.form['bene_name']
        bene_email= request.form['bene_email']
        curr_role=session.get('role')
        beneficiary_status=session.get('beneficiary_status')

        headings=("First Name","Last Name","EMAIL","PHONE","ADDRESS","CITY","AGE","BLOODGROUP")
        
      

        userslist = []
        sql = "SELECT NAME,LASTNAME,EMAIL,PHONE,ADDRESS,CITY,AGE,BLOODGROUP FROM SIGNUP_TABLE WHERE role=? AND beneficiary_status=?"
        stmt=ibm_db.prepare(conn,sql) 
        ibm_db.bind_param(stmt,1,role)
        ibm_db.bind_param(stmt,2,bene_status)        
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
            return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=name,email=email,role=curr_role,beneficiary_status=beneficiary_status)
            return render_template('dashboard.html',user=name,email=email,role=curr_role)
            
        
        #enter dashboard if new user registers for first time

        else:
         
            insert_sql = "INSERT INTO BENEFICIARY_REQUEST_TABLE(BENEFICIARY_EMAIL,DONOR_EMAIL) VALUES (?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, bene_email)
            ibm_db.bind_param(prep_stmt, 2, donor) 
            ibm_db.execute(prep_stmt) 
           
        #return render_template('dashboard.html', user=session['user'],email=session['email'],role=session['role']) 
        return render_template('dashboard.html', requesters_list=userslist,headings=headings,user=name,email=email,role=curr_role,bene_status=beneficiary_status)
       
@app.route('/change_to_requested_status',methods = ['POST', 'GET']) 
  
def change_to_requested_status(): 
    if request.method == 'POST':

        newstatus = "requested"
        role_donor="donor"
        email=session.get('email')
        city=session.get('city')
        bloodgroup=session.get('bloodgroup')
        user=session.get('user')
        curr_role=session.get('role')
        password=session.get('password')

        sql = "UPDATE SIGNUP_TABLE SET BENEFICIARY_STATUS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newstatus) 
        ibm_db.bind_param(stmt,2,email)
        
        ibm_db.execute(stmt)
        
        session['beneficiary_status']=newstatus
        

        #When a request is made,notify relevant donors by mail.        


        donorslist = []
        sql2 = "SELECT EMAIL FROM SIGNUP_TABLE WHERE ROLE=? AND CITY=? AND BLOODGROUP=?"
        stmt2=ibm_db.prepare(conn,sql2) 
        ibm_db.bind_param(stmt2,1,role_donor)
        ibm_db.bind_param(stmt2,2,city) 
        ibm_db.bind_param(stmt2,3,bloodgroup) 
        
        
        ibm_db.execute(stmt2) 
        dictionary = ibm_db.fetch_both(stmt2)
        while dictionary != False: 
            donorslist.append(dictionary)    

            recipient = dictionary['EMAIL']
            msg = Message('Donor Needed!', recipients=[recipient])
            msg.body = ('Important! A request for plasma matches your blood group and is in your city!'
                        'Donors alert')
            msg.html = ('<h1>Request Alert</h1>'
                        '<p>Important! A request for plasma matches your blood group and is in your city! '
                        '<b>Donors alert</b>!</p>')
            mail.send(msg)    


            dictionary = ibm_db.fetch_both(stmt2)

        
        #end of notifying donors with mail. 

    
    return render_template('dashboard.html', user=user,role=curr_role,email=email,password=password,msg="",beneficiary_status="requested") 
            
@app.route('/change_to_none_status',methods = ['POST', 'GET']) 
  
def change_to_none_status(): 
    if request.method == 'POST':

        newstatus = ""
        role=session.get('role')
        user=session.get('user')
        email=session.get('email')
        password=session.get('password')
      
        sql = "UPDATE SIGNUP_TABLE SET BENEFICIARY_STATUS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newstatus) 
        ibm_db.bind_param(stmt,2,email)
        
        ibm_db.execute(stmt)
        
        session['beneficiary_status']=newstatus 
        #flash("Password updated successfully!!")    

    
    return render_template('dashboard.html', role=role,user=user,email=email,password=password,msg="",beneficiary_status="")


@app.route('/fromsignup', methods = ['POST', 'GET'])
def fromsignup():  


    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password') 
        isdonor=request.form.get('role')
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
            ibm_db.execute(prep_stmt) 
            
        #flash("Registration successful..")    
        return render_template('signin.html', msg="Register success..Please login ito app now..")

@app.route('/fromsignin', methods = ['POST', 'GET'])
  
def fromsignin():

    if request.method == 'POST':

        session.pop('user',None)        
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
            session['certificate_uploaded']=dictionary[14] 
            session['illness_details']=dictionary[15]
            


            dictionary = ibm_db.fetch_both(stmt)
        if userslist:      
            user=session.get('user')
            email=session.get('email')
            password=session.get('password')
            role=session.get('role')     
                       
            return render_template('profile.html', user=user,email=email,password=password,role=role,msg="Login successful..") 
            
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

#starting cloud storage methods



@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST': 
       user=session.get('user')
       email=session.get('email') 
       password=session.get('password')
       role=session.get('role')
    

       f = request.files['file']
       filename = secure_filename(f.filename)

       f.save(app.config['UPLOAD_FOLDER'] + filename) 
    

       bucket="pdabucketone" 
       name_file=session['email']+".pdf"      
       multi_part_upload(bucket,name_file,app.config["UPLOAD_FOLDER"]+f.filename) 

       #update the success in database         
      
       sql = "UPDATE SIGNUP_TABLE SET certificate_uploaded=? WHERE email=? "
       stmt=ibm_db.prepare(conn,sql)
       ibm_db.bind_param(stmt,1,"yes")       
       ibm_db.bind_param(stmt,2,email)        
       ibm_db.execute(stmt) 
  
       return render_template('profile.html', user=user,email=email,CERTIFICATE_UPLOADED="yes",password=password,role=role,msg="Your data has been saved successfully..")
       
    
   if request.method == 'GET':
       return render_template('profile.html', user=user,email=email,CERTIFICATE_UPLOADED="no",password=password,role=role,msg="")

#ending cloud storage methods

@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        recipient = request.form['recipient']
        msg = Message('Twilio SendGrid Test Email', recipients=[recipient])
        msg.body = ('Congratulations! You have sent a test email with '
                    'Twilio SendGrid!')
        msg.html = ('<h1>Twilio SendGrid Test Email</h1>'
                    '<p>Congratulations! You have sent a test email with '
                    '<b>Twilio SendGrid</b>!</p>')
        mail.send(msg)
        flash(f'A test message was sent to {recipient}.')
        
        #return redirect(url_for('index'))
    return render_template('signup.html') 



@app.route('/change_password',methods = ['POST', 'GET']) 
  
def change_password(): 
    if request.method == 'POST':

        newpassword = request.form['newpass']
        email=session.get('email')
        user=session.get('user')
        role=session.get('role')
        password=session.get('password')
      
        sql = "UPDATE SIGNUP_TABLE SET password=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newpassword) 
        ibm_db.bind_param(stmt,2,email)
        
        ibm_db.execute(stmt)
        
        session['password']=newpassword 

        #When a password change is made,notify by mail. 


        donorslist = []
        sql2 = "SELECT EMAIL FROM SIGNUP_TABLE WHERE EMAIL=?"
        stmt2=ibm_db.prepare(conn,sql2) 
        ibm_db.bind_param(stmt2,1,email)
        
        
        
        ibm_db.execute(stmt2) 
        dictionary = ibm_db.fetch_both(stmt2)
        while dictionary != False: 
            donorslist.append(dictionary)    

            recipient = dictionary['EMAIL']
            msg = Message('Account Password Change detected!', recipients=[recipient])
            msg.body = ('Your password has been changed recently.'
                        'Password Changed')
            msg.html = ('<h1>Password change</h1>'
                        '<p>Your password has been changed recently. '
                        '<b>Password Changed</b>!</p>')
            mail.send(msg)    


            dictionary = ibm_db.fetch_both(stmt2)

        
        #end of notifying with mail. 
        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=user,role=role,email=email,password=password,msg="Password updated successfully") 
            

@app.route('/send_feedback',methods = ['POST', 'GET']) 
  
def send_feedback(): 
    if request.method == 'POST':
        user=session.get('user')
        email=session.get('email')
        city=session.get('city')
        role=session.get('role')
        subject=request.form['subject']
        insert_sql = "INSERT INTO FEEDBACK_TABLE(NAME,EMAIL,CITY,ROLE,SUBJECT) VALUES (?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, user)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, city)
        ibm_db.bind_param(prep_stmt, 4, role)
        ibm_db.bind_param(prep_stmt, 5, subject)
        ibm_db.execute(prep_stmt) 
        
            
        #flash("Registration successful..")    
        return render_template('contact.html', msg="Thanks for your feedback!")




 
            

@app.route('/update_account_settings',methods = ['POST', 'GET'])
def update_account_settings(): 
    if request.method == 'POST':

        newlastname = request.form['lastname']
        newphone = request.form['phone']
        newaddress = request.form['address']
        newcity = request.form['city']
        newbio = request.form['bio']
        email=session.get('email')
        password=session.get('password')
        role=session.get('role')
        user=session.get('user')
        
      
        sql = "UPDATE SIGNUP_TABLE SET LASTNAME=?,PHONE=?,ADDRESS=?,CITY=?,BIO=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newlastname) 
        ibm_db.bind_param(stmt,2,newphone)
        ibm_db.bind_param(stmt,3,newaddress)
        ibm_db.bind_param(stmt,4,newcity)
        ibm_db.bind_param(stmt,5,newbio)
        ibm_db.bind_param(stmt,6,email)
        
        ibm_db.execute(stmt)
        
        
        session['lastname']=newlastname 
        session['phone']=newphone
        session['address']=newaddress
        session['city']=newcity
        session['bio']=newbio 
        

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html',user=user,email=email,password=password,msg="Account Settings updated successfully",role=role) 
            

@app.route('/change_bene_details',methods = ['POST', 'GET'])
def change_bene_details(): 
    if request.method == 'POST':

        newheight = request.form['b-height']
        newweight = request.form['b-weight']
        newbloodgroup = request.form['b-bloodgroup']
        newage = request.form['b-age']
        user=session.get('user')
        email=session.get('email')
        password=session.get('password')
        role=session.get('role')
      
        sql = "UPDATE SIGNUP_TABLE SET HEIGHT=?,WEIGHT=?,BLOODGROUP=?,AGE=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newheight) 
        ibm_db.bind_param(stmt,2,newweight)
        ibm_db.bind_param(stmt,3,newbloodgroup)
        ibm_db.bind_param(stmt,4,newage)
        ibm_db.bind_param(stmt,5,email)
        
        ibm_db.execute(stmt)
        
        
        session['height']=newheight
        session['weight']=newweight
        session['bloodgroup']=newbloodgroup
        session['age']=newage
         

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=user,email=email,password=password,msg="Your Details have been updated successfully",role=role) 
            

@app.route('/change_donor_details',methods = ['POST', 'GET'])
def change_donor_details(): 
    if request.method == 'POST':
        email=session.get('email')
        user=session.get('user')
        password=session.get('password')
        role=session.get('role')

        newheight = request.form['d-height']
        newweight = request.form['d-weight']
        newbloodgroup = request.form['d-bloodgroup']
        newage = request.form['d-age']
        newillnessdetails=request.form['illness']
        
        
      
        sql = "UPDATE SIGNUP_TABLE SET HEIGHT=?,WEIGHT=?,BLOODGROUP=?,AGE=?,ILLNESS_DETAILS=? WHERE email=? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newheight) 
        ibm_db.bind_param(stmt,2,newweight)
        ibm_db.bind_param(stmt,3,newbloodgroup)
        ibm_db.bind_param(stmt,4,newage)
        ibm_db.bind_param(stmt,5,newillnessdetails)
        ibm_db.bind_param(stmt,6,email)
        
        ibm_db.execute(stmt)
        
        
        session['height']=newheight
        session['weight']=newweight
        session['bloodgroup']=newbloodgroup
        session['age']=newage 
        session['illness_details']=newillnessdetails
         

        #flash("Password updated successfully!!")    

    
    return render_template('profile.html', user=user,email=email,password=password,msg="Your Details have been updated successfully",role=role) 
            




@app.before_request 
def before_request():
    g.user=None 
    user=session.get('user')

    if 'user' in session:
        g.user=user

@app.route('/dropsession') 
def dropsession():
    session.pop('user',None) 
    return render_template('signin.html')



if __name__ == "__main__":
    
    with app.test_request_context("/"):
        session["key"] = "value" 
    app.run(host='0.0.0.0', port=5000, debug=True)   


