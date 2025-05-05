from flask import Flask , render_template , request , jsonify , Response ,session 
from flask_session import Session
from fileinput import filename
from werkzeug.utils import secure_filename
from distutils.log import debug
import sqlite3
from flask import * 
import os
import re
import datetime

Home = Flask(__name__)
Home.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@Home.route("/")
def homepage():
    conn = sqlite3.connect('projet.db')
    c = conn.cursor()
    c.execute("select home_text from projet")
    text = ''.join(c.fetchone())
    conn.close()
    return render_template('home.html' , text = text)

    


@Home.route("/boss_user")
def boss_user():
         conn = sqlite3.connect('user_boss_data.db')
         c = conn.cursor()
         c.execute("SELECT name FROM sqlite_master WHERE type='table';")
         table_names = [row[0] for row in c.fetchall()]
         return render_template("boss_of_users.html" , table_names=table_names)

@Home.route("/boss_user" ,methods=['POST'])
def add_boss():
    name = request.form['name']

    if name != 'none':
         db = sqlite3.connect('user_boss_data.db')
         cursor = db.cursor()
         cursor.execute(f'create table if not exists {name} ( boss_name text, user_name text,user_email text,money1 text , benefit text)') 
         db.commit()
         db.close()
         conn = sqlite3.connect('user_boss_data.db')
         c = conn.cursor()
         c.execute("SELECT name FROM sqlite_master WHERE type='table';")
         table_names = [row[0] for row in c.fetchall()]
         return render_template("boss_of_users.html" ,table_names=table_names  )

@Home.route("/affiliate/<name>")
def affiliate_signup(name):
    db = sqlite3.connect('user_boss_data.db')
    cursor = db.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    db.close()
    
    if name in table_names:
        return render_template('add_account_two.html', name=name  )
    else:
        return "Error: Invalid affiliate code"

#hnaya bch ndirou sanitiz lal inputs 3la injections atacks
def sanitize_input(input_string):
    allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@."
    return ''.join(c for c in input_string if c in allowed_characters)

@Home.route("/addaccount_affiliate")
def add_account_affiliate():
    return render_template('add_account_two.html')
@Home.route("/addaccount_affiliate" , methods=['POST'])
def add_account_two():

    name = sanitize_input(request.form['name'])
    password = sanitize_input(request.form['password'])
    dateofbirth = sanitize_input(request.form['dateofbirth'])
    email = sanitize_input(request.form['email'])
    phone = sanitize_input(request.form['phone'])
    adress = sanitize_input(request.form['adress'])
    boss_name = sanitize_input(request.form['boss_name'])
    
    email = request.form['email']
    conn = sqlite3.connect('users_add.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM user WHERE email=?", (email,))
    result = cur.fetchone()
    conn.close()
    
    if result:
       return '<h1 style:"font-size:40px"> إيميل مستعمل من قبل أعد المحاولة</h1>'
    
    else :  
       db = sqlite3.connect('user_boss_data.db')
       cursur = db.cursor()
       cursur.execute("INSERT INTO ? (boss_name, user_name, user_email,money1, benefit) VALUES (?, ?, ? ,? , ?)", (boss_name, boss_name, name,email,'0', '0'))
       db.commit()
       db.close()

       db = sqlite3.connect('users_add.db')
       cr = db.cursor()
       cr.execute('create table if not exists user (name text , password text , date_of_birth integer , email text , phone integer , adress text , card_number integer , money1 text , money2 text , message text , date_close text ,first_date text)')
       cr.execute("insert into user (name, password, date_of_birth, email, phone, adress, money1, money2 , message  , date_close , first_date ) values (%s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s ,%s)", (name, password, dateofbirth, email, phone, adress, 0, 0 ,'' , '' , ''))
       db.commit()
       db.close()

       db = sqlite3.connect('projet.db')
       cur = db.cursor()
       cur.execute('select projet from projet')
       projet = ''.join(cur.fetchone())
       db.close()
    
       return render_template('user_account.html' , first_name = name , projet=projet )

@Home.route("/addaccount")
def addpage():
    return render_template('add_account.html')
@Home.route("/addaccount", methods=['POST'])
def add_account():
    name = sanitize_input(request.form['name'])
    password = sanitize_input(request.form['password'])
    date_of_birth = sanitize_input(request.form['dateofbirth'])
    email = sanitize_input(request.form['email'])
    phone = sanitize_input(request.form['phone'])
    adress = sanitize_input(request.form['adress'])
    session['user_namefrom_addaccount'] = name

    email = request.form['email']
    conn = sqlite3.connect('users_add.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM user WHERE email=?", (email,))
    result = cur.fetchone()
    conn.close()
    
    if result:
       return '<h1 style:"font-size:40px"> إيميل مستعمل من قبل أعد المحاولة</h1>'
    else :  
        db = sqlite3.connect('users_add.db')
        cr = db.cursor()
        cr.execute('create table if not exists user (name text , password text , date_of_birth integer , email text , phone integer , adress text  , money1 text , money2 text , message text , date_close text , first_date text)')
        cr.execute("INSERT INTO user (name, password, date_of_birth, email, phone, adress, money1, money2 , message  , date_close , first_date ) VALUES (?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,?)", (name, password, date_of_birth, email, phone, adress, 0, 0 , '', '' , ''))
        db.commit()
        db.close()
        db = sqlite3.connect('projet.db')
        cur = db.cursor()
        cur.execute('select projet from projet')
        projet = ''.join(cur.fetchone())
        db.close()
        db = sqlite3.connect('users_add.db')
        cr = db.cursor()
        user_money1 = f'select money1 from user where email="{email}";'
        user_money2 = f'select money2 from user where email="{email}";'
        message_user = f'select message from user where email="{email}";'
        date_close = f'select date_close from user where email="{email}";'
        date_first_money = f'select first_date from user where email="{email}";'
        cr.execute(user_money1)
        money1 = ''.join(cr.fetchone())
        cr.execute(user_money2)
        money2 = ''.join(cr.fetchone())
        cr.execute(message_user)
        message = ''.join(cr.fetchone())
        cr.execute(date_close)
        date_close_projet = ''.join(cr.fetchone())
        cr.execute(date_first_money)
        first_date = ''.join(cr.fetchone())
        db.commit()
        db.close()
        
        return render_template('user_account.html' , first_name = name ,
                                                     projet=projet ,
                                                     money1 = money1,
                                                     money2 = money2,
                                                     message = message,
                                                     date_close_projet = date_close_projet,
                                                     first_date = first_date )
    

    
@Home.route("/login")
def login():
    return render_template('login.html')
@Home.route("/login", methods=['POST'])
def logindef():
    
    log_email = request.form['log_email'] 
    log_code = request.form['log_code']

    if log_email == 'admiN12594@gmail.com' and log_code == 'Admin_boss1567' :
            img_folder = 'static/img/ccp'
            imgs = os.listdir(img_folder)
            path = os.path.join(Home.static_folder, 'img', 'user_case')
            files = os.listdir(path)

            db = sqlite3.connect('users_add.db')
            cur = db.cursor()
            cur.execute("SELECT name, email FROM user")
            names = cur.fetchall()
            db.close()

            db = sqlite3.connect('projet.db')
            cur = db.cursor()
            cur.execute('select * from benifit')
            data = cur.fetchall()
            cur.execute("SELECT * FROM feedback")
            feedback = cur.fetchall()
            cur.execute('select * from i3adet_istithmer_rasalmal')
            i3adet_istithmer_rasalmal = cur.fetchall()
            cur.execute("SELECT * FROM sa7b_ras_almal")
            sa7b_ras_almal = cur.fetchall()
            db.close()
            session['user_email'] = log_email
            return render_template('admin_page.html' , imgs=imgs ,
                                                       names = names,
                                                       files = files ,
                                                       data = data ,
                                                       i3adet_istithmer_rasalmal = i3adet_istithmer_rasalmal,
                                                       sa7b_ras_almal = sa7b_ras_almal,
                                                       feedback = feedback)

    elif log_email != 'none':
       db = sqlite3.connect('users_add.db')
       cr = db.cursor()
       statement = f'select email from user where email="{log_email}" and password="{log_code}";'
       cr.execute(statement)

       if not cr.fetchone():
           return render_template('login.html')

       else:
           statement2 = f'select name from user where email="{log_email}"'
           cr.execute(statement2)
           name_login = ''.join(cr.fetchone())
           cr.close()
           db = sqlite3.connect('users_add.db')
           cr = db.cursor()
           user_money1 = f'select money1 from user where email="{log_email}";'
           user_money2 = f'select money2 from user where email="{log_email}";'
           message_user = f'select message from user where email="{log_email}";'
           date_close = f'select date_close from user where email="{log_email}";'
           date_first_money = f'select first_date from user where email="{log_email}";'
           cr.execute(user_money1)
           money1 = ''.join(cr.fetchone())
           cr.execute(user_money2)
           money2 = ''.join(cr.fetchone())
           cr.execute(message_user)
           message = ''.join(cr.fetchone())
           cr.execute(date_close)
           date_close_projet = ''.join(cr.fetchone())
           cr.execute(date_first_money)
           first_date = ''.join(cr.fetchone())
           db.commit()
           db.close()
           
           db = sqlite3.connect('projet.db')
           cur = db.cursor()
           cur.execute('select projet from projet')
           projet = ''.join(cur.fetchone())
           cur.execute('select date_take_benifit from date_take_benifit')
           date_take_benifit = ''.join(cur.fetchone())
           db.close()
           money3 = int(money1) + int(money2)
           money4 = 1200000 - money3
           session['user_email'] = log_email
           session['money1'] = money1
           session['money2'] = money2
           session['money3'] = money3
           session['money4'] = money4
           session['projet'] = projet
           session['user_name'] = name_login
           session['message'] = message
           session['date_close'] = date_close_projet
           session['first_date'] = first_date
           session['date_take_benifit'] = date_take_benifit
           return render_template('user_account.html' , first_name = name_login ,
                                                        money1 = money1,
                                                        money2 = money2,
                                                        money3 = money3,
                                                        money4 = money4,
                                                        projet = projet,
                                                        message = message,
                                                        date_close = date_close_projet,
                                                        first_date = first_date,
                                                        date_take_benifit = date_take_benifit)

    
@Home.route("/logout" , methods=['POST'])
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login'))

@Home.route("/home")
def user_acount():
    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date']
                                                 )





@Home.route("/admin")
def admin_acount():
  if 'user_email' not in session:
        return redirect(url_for('login')) 
  else:    
    img_folder = 'static/img/ccp'
    imgs = os.listdir(img_folder)

    db = sqlite3.connect('users_add.db')
    cur = db.cursor()
    cur.execute("SELECT name, email FROM user")
    names = cur.fetchall()
    db.close()
    return render_template('admin_page.html' , imgs=imgs , names = names)
    
@Home.route('/admin' , methods=['POST'])
def user_modify_user():
    user_email = request.form['email_from_boss']
    message = request.form['message']
    
    if request.form['boss_user_control_submit'] == 'إرسال':
        current_date = datetime.datetime.now().strftime("%y/%m/%d")
        money_addd = request.form['boss_add_money']
        money_add = int(money_addd)
        money_benifis = money_add * 2 / 100
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        user_money1 = f'select money1 from user where email ="{user_email}";'
        cur.execute(user_money1)
        money1 = int(''.join(cur.fetchone()))
        new_money = money1 + money_add
        cur.execute("UPDATE user SET money1 = ?  WHERE email = ?", (new_money ,user_email ))
        cur.execute("UPDATE user SET first_date = ?  WHERE email = ?", (current_date ,user_email ))
        db.commit()
        db.close()
        #hadi bach ndirou update alasome ali falista te3 lmousaqi2e te3 koul 3amil
# Connect to the second database
        conn2 = sqlite3.connect('user_boss_data.db')
        cursor2 = conn2.cursor()

# Get a list of all tables in the second database
        cursor2.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor2.fetchall()

# Loop through all tables and search for the email input
        for table in tables:
            cursor2.execute('SELECT * FROM {} WHERE user_email = ?'.format(table[0]), (user_email,))
            user = cursor2.fetchone()
            if user:
        # Update the corresponding row with the money1 value
               cursor2.execute('UPDATE {} SET money1 = ?, benefit = ? WHERE user_email = ?'.format(table[0]), (money_add, money_benifis ,user_email))
               
            break
# Commit the changes to the second database
        conn2.commit()
# Close the connections
        conn2.close()
        
    elif request.form['boss_user_control_submit'] == "حذف المستخدم" :
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute(f'delete from user where email ="{user_email}"')
        db.commit()
        db.close()
    
    elif request.form['boss_user_control_submit'] == "إرسال الرسالة" :
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute("UPDATE user SET message = ?  WHERE email = ?", (message ,user_email ))
        db.commit()
        db.close()
    
    elif request.form['boss_user_control_submit'] == "تصفير الأرباح" :
        money = 0
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute("UPDATE user SET money2 = ?  WHERE email = ?", (money ,user_email ))
        db.commit()
        db.close()

    elif request.form['boss_user_control_submit'] == "تصفير رأس المال" :
        money = 0
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute("UPDATE user SET money1 = ?  WHERE email = ?", (money ,user_email ))
        db.commit()
        db.close()

    elif request.form['boss_user_control_submit'] == "مدة طلب الأرباح" :
        date_take_benifits = request.form['date_take_benifit']
        db = sqlite3.connect('projet.db')
        cur = db.cursor()
        cur.execute(f'UPDATE date_take_benifit SET date_take_benifit = "{date_take_benifits}"')
        db.commit()
        db.close()
        

    img_folder = 'static/img/ccp'
    imgs = os.listdir(img_folder)

    db = sqlite3.connect('users_add.db')
    cur = db.cursor()
    cur.execute("SELECT name, email FROM user")
    names = cur.fetchall()
    db.close()
    return render_template('admin_page.html' , imgs=imgs , names = names)


@Home.route("/user_benefit")
def user_benefit():
    return render_template('user_benefit.html')
@Home.route("/user_benefit" , methods=["POST"])
def user_benefit_add():
        user_email = request.form['email']
        money_addd = request.form['money']
        money_add = int(money_addd)
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        user_money1 = f'select money2 from user where email ="{user_email}";'
        cur.execute(user_money1)
        money2 = int(''.join(cur.fetchone()))
        new_money = money2 + money_add
        cur.execute("UPDATE user SET money2 = ?  WHERE email = ?", (new_money ,user_email ))
        db.commit()
        db.close()
        return render_template('user_benefit.html')



@Home.route("/projet")
def boss_project():
    return render_template ('boss_project.html')
@Home.route("/projet" , methods=['POST'])
def add_projet():
    if request.form['creat_date_submit'] == 'نشر':
       projet = request.form['projet_text']
       db = sqlite3.connect('projet.db')
       cur = db.cursor()
       cur.execute(f'UPDATE projet SET projet = "{projet}"')
       db.commit()
       db.close()

    elif request.form['creat_date_submit'] == 'إرسال' :
        close_date = request.form['creat_date']
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute(f"UPDATE user SET date_close = '{close_date}'")
        db.commit()
        db.close()

    elif request.form['creat_date_submit'] == 'نشر في صفحة الموقع' :
         home_text = request.form['home_text']
         db = sqlite3.connect('projet.db')
         cur = db.cursor()
         cur.execute(f'UPDATE projet SET home_text  = "{home_text}"')
         db.commit()
         db.close()

    return render_template('boss_project.html')


@Home.route("/boss_info")
def boss_info():
    return render_template('boss_info.html')
@Home.route("/boss_info" , methods=['POST'])
def boss_infoo():
    name = request.form['name']
    conn = sqlite3.connect("user_boss_data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {name}")
    data = cursor.fetchall()
    conn.close()
    return render_template("boss_info.html", data=data)

#hadi bch naraslou sora te3 ccp
@Home.route("/deposit")
def add_money():
    return render_template('add_money.html' , user_name = session['user_name'])
@Home.route("/deposit" , methods=['POST'])
def send_money():
  if request.method == 'POST':
    picture = request.files['pic']
    user_name = sanitize_input(request.form['user_name'])
    picture_name = secure_filename(picture.filename)
    picture.save(f'static/img/ccp/{user_name}_{picture_name}')
    return render_template('add_money.html')

#hadi te3 bch naraslou adosi mal user 
@Home.route("/case")
def case():
    return render_template("dosi.html" , user_name = session['user_name'])
@Home.route("/case" , methods=['POST'])
def send_case():
    if request.method == 'POST':
        email = request.form['email']
        user_folder = f'static/img/user_case/{email}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            for file in request.files.getlist("file"):
                file_name = secure_filename(file.filename)
                file.save(f'{user_folder}/{email}_{file_name}')
    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])

    
#hadi a def darna fiha kiy3abaz al user lbutton tro7 had adef tadi man value te3 arib7
#mouda3af ra9m 3 wtonjistrih fi variable wal rest fi variable ou tmodifyi al db
@Home.route('/i3adat_istithmar', methods=['POST'])
def i3adet_istithmer():
    user_email = session['user_email']
    db = sqlite3.connect('users_add.db')
    cur = db.cursor()
    user_money2 = f'select money2 from user where email ="{user_email}";'
    cur.execute(user_money2)
    money2 = int(''.join(cur.fetchone()))
    user_money1 = f'select money1 from user where email ="{user_email}";'
    cur.execute(user_money1)
    money1 = int(''.join(cur.fetchone()))
    money1 = money2 + money1 
    money2 = 0
    cur.execute("UPDATE user SET money2 = ?, money1 =?  WHERE email = ?", (money2 , money1 ,user_email ))
    db.commit()
    db.close()
    
    return render_template('user_account.html' , money1 = money1,
                                                 money2 = money2,
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])

#hadi te3 sa7b al2arba7
@Home.route('/sa7b_benifit', methods=['POST'])
def sa7b_benifit():
    name = session['user_email']
    db = sqlite3.connect('projet.db')
    cur = db.cursor()
    cur.execute('insert into benifit (benifit) values (?)', [name])
    db.commit()
    db.close()

    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])


#hadi te3 sa7b ras almal
@Home.route('/sa7b_ras_almal', methods=['POST'])
def sa7b_ras_almal():
    email = session['user_email']
    db = sqlite3.connect('projet.db')
    cur = db.cursor()
    cur.execute('insert into sa7b_ras_almal (sa7b_ras_almal) values (?)', [email])
    db.commit()
    db.close()

    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])


#hadi te3 1year_button alawlaniya te3 2i3adat 2istithmer ra2s almal
@Home.route('/i3adet_ras_almal', methods=['POST'])
def i3adet_ras_almal():
    email = session['user_email']
    db = sqlite3.connect('projet.db')
    cur = db.cursor()
    cur.execute('insert into i3adet_istithmer_rasalmal (i3adet_istithmer_rasalmal) values (?)', [email])
    db.commit()
    db.close()

    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])

#hadi te3 bch tatongistra al feedback fal db te3 projet bch nafichiw manha fal admin page
@Home.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    email = session['user_email']
    feedback = request.form["feedback"]

    conn = sqlite3.connect('projet.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (email, feedback) VALUES (?,?)", (email, feedback))
    conn.commit()
    conn.close()
    return render_template('user_account.html' , money1 = session['money1'],
                                                 money2 = session['money2'],
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 date_close = session['date_close'],
                                                 first_date = session['first_date'])


#hadi paga ali tataficha fiha tsawer te3 al3amil watilichargiha kitackliki
@Home.route('/files/<file_name>')
def show_images(file_name):
    if 'user_email' not in session:
        return render_template('login.html')
    else:
        image_names = os.listdir(f'static/img/user_case/{file_name}')
        return render_template('user_file_pics.html', file_name=file_name, image_names=image_names)
        
@Home.route('/download/<file_name>/<image_name>')
def download_image(file_name, image_name):
    if 'user_email' not in session:
        return render_template('login.html')
    else:
        return send_from_directory(f'static/img/user_case/{file_name}', image_name, as_attachment=True)






if __name__ == "__main__":
    Home.run( debug=False)