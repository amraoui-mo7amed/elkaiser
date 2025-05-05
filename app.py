from flask import Flask , render_template , request , jsonify , Response ,session,url_for,redirect
from flask_mail import Mail, Message
from flask import current_app
import uuid
from flask_session import Session
from fileinput import filename
from werkzeug.utils import secure_filename
from distutils.log import debug
import sqlite3
from flask import *
import os
import re
import datetime
import jinja2





Home = Flask(__name__)
Home.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Home.config['SECRET_KEY'] = 'mysecretkey'
Home.config['MAIL_SERVER'] = 'smtp.gmail.com'
Home.config['MAIL_PORT'] = 587
Home.config['MAIL_USE_TLS'] = True
Home.config['MAIL_USERNAME'] = 'nouhhamdadou@gmail.com'
Home.config['MAIL_PASSWORD'] = 'jkowzvufaqlmcfys'

mail = Mail(Home)


Home.jinja_env.globals.update(int=int)



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
         cursor.execute(f'create table if not exists {name} ( boss_name text, name1 text,name2 text , user_email text,money1 text , benefit text)')
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
    allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@. "
    return ''.join(c for c in input_string if c in allowed_characters)

@Home.route("/addaccount_affiliate")
def add_account_affiliate():
    return render_template('add_account_two.html')
@Home.route("/addaccount_affiliate" , methods=['POST'])
def add_account_two():

    name1 = request.form['name1']
    name2 = request.form['name2']
    password = request.form['password']
    dateofbirth = sanitize_input(request.form['dateofbirth'])
    email = request.form['email']
    phone = sanitize_input(request.form['phone'])
    adress = sanitize_input(request.form['adress'])
    boss_name = request.form['boss_name']

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
       cursur.execute(f"INSERT INTO {boss_name} (boss_name, name1 , name2 , user_email,money1, benefit) VALUES (?, ?, ? ,? , ? , ?)", (boss_name, name1 , name2,email,'0', '0'))
       db.commit()
       db.close()

       db = sqlite3.connect('users_add.db')
       cr = db.cursor()
       cr.execute('create table if not exists user (name1 text , name2 text, password text , date_of_birth integer , email text , phone integer , adress text , card_number integer , money1 text , money2 text , message text , date_close text ,first_date text ,reset_token text , dosi text , user_send_money text)')
       cr.execute("insert into user (name1, name2, password, date_of_birth, email, phone, adress, money1, money2 , message  , date_close , first_date , reset_token ,dosi , user_send_money ) values (?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,?,?,?,?,?)", (name1 ,name2 , password, dateofbirth, email, phone, adress, 0, 0 ,'' , '' , '' , '' ,'' , ''))
       db.commit()
       db.close()

       message_to_user = 'مبارك تسجيلكم في موقع القيصر للإستثمار . يمكنكم البدأ الآن بتشغيل أموالكم والإستثمار'

       email_template = render_template('email.html', message_to_user=message_to_user)

       msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[email])
       msg.body = f"Name: {name1.encode('utf-8').decode()}\nEmail: {email}\nMessage:\n{message_to_user}"
       msg.html = email_template

       mail.send(msg)


       db = sqlite3.connect('projet.db')
       cur = db.cursor()
       cur.execute('select projet from projet')
       projet = ''.join(cur.fetchone())

       cur.execute('select user_account_msg from projet')
       all_user_message = ''.join(cur.fetchone())
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

       return render_template('tsjil_7isab_jadid.html' , first_name = name1 ,
                                                     projet=projet ,
                                                     money1 = money1,
                                                     money2 = money2,
                                                     message = message,
                                                     date_close_projet = date_close_projet,
                                                     first_date = first_date,
                                                     user_email = email,
                                                     all_user_message = all_user_message )


@Home.route("/addaccount")
def addpage():
    return render_template('add_account.html')
@Home.route("/addaccount", methods=['POST'])
def add_account():
    name1 = request.form['name1']
    name2 = request.form['name2']
    password = request.form['password']
    date_of_birth = sanitize_input(request.form['dateofbirth'])
    email = request.form['email']
    phone = sanitize_input(request.form['phone'])
    adress = sanitize_input(request.form['adress'])
    session['user_namefrom_addaccount'] = name1

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
        cr.execute('create table if not exists user (name1 text , name2 text, password text , date_of_birth integer , email text , phone integer , adress text  , money1 text , money2 text , message text , date_close text , first_date text , reset_token text ,dosi text , user_send_money text)')
        cr.execute("INSERT INTO user (name1,name2, password, date_of_birth, email, phone, adress, money1, money2 , message  , date_close , first_date , reset_token ,dosi , user_send_money ) VALUES (?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,?,?,?,?,?)", (name1,name2, password, date_of_birth, email, phone, adress, 0, 0 , '', '' , '' ,'' ,'',''))
        db.commit()
        db.close()

        message_to_user = 'مبارك تسجيلكم في موقع القيصر للإستثمار . يمكنكم البدأ الآن بتشغيل أموالكم والإستثمار'

        email_template = render_template('email.html', message_to_user=message_to_user)

        msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[email])
        msg.body = f"Name: {name1.encode('utf-8').decode()}\nEmail: {email}\nMessage:\n{message_to_user}"
        msg.html = email_template

        mail.send(msg)

        db = sqlite3.connect('projet.db')
        cur = db.cursor()
        cur.execute('select projet from projet')
        projet = ''.join(cur.fetchone())

        cur.execute('select user_account_msg from projet')
        all_user_message = ''.join(cur.fetchone())

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

        return render_template('tsjil_7isab_jadid.html' , first_name = name1 ,
                                                     projet=projet ,
                                                     money1 = money1,
                                                     money2 = money2,
                                                     message = message,
                                                     date_close_projet = date_close_projet,
                                                     first_date = first_date,
                                                     user_email = email,
                                                     all_user_message = all_user_message )

@Home.route("/first_login", methods=['POST'])
def first_login():

    first_name = request.form['first_name']
    projet = request.form['projet']
    money1 = request.form['money1']
    money2 = request.form['money2']
    user_email = request.form['user_email']
    all_user_message = request.form['all_user_message']

    session['user_email'] = user_email
    session['money1'] = money1
    session['money2'] = money2
    session['projet'] = projet
    session['all_user_message'] = all_user_message
    session['user_name'] = first_name

    return render_template('user_account.html' ,     first_name = first_name ,
                                                     projet=projet,
                                                     money1 = money1,
                                                     money2 = money2,
                                                     user_email = user_email,
                                                     all_user_message = all_user_message,)


@Home.route("/first_login_1", methods=['POST'])
def first_login_1():

    first_name = request.form['first_name']
    projet = request.form['projet']
    money1 = request.form['money1']
    money2 = request.form['money2']
    user_email = request.form['user_email']
    all_user_message = request.form['all_user_message']

    session['user_email'] = user_email
    session['money1'] = money1
    session['money2'] = money2
    session['projet'] = projet
    session['all_user_message'] = all_user_message
    session['user_name'] = first_name

    return render_template('user_account.html' ,     first_name = first_name ,
                                                     projet=projet,
                                                     money1 = money1,
                                                     money2 = money2,
                                                     user_email = user_email,
                                                     all_user_message = all_user_message,)


@Home.route("/login")
def login():
    return render_template('login.html')
@Home.route("/login", methods=['POST'])
def logindef():

    log_email = request.form['log_email']
    log_code = request.form['log_code']

    if log_email == 'admiN12594@gmail.com' and log_code == 'Admin_boss1567' :

            db = sqlite3.connect('users_add.db')
            cur = db.cursor()
            cur.execute("SELECT name1,name2, email, phone, password, dosi, user_send_money  FROM user")
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
            return render_template('admin_page.html' , names = names,
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
           statement2 = f'select name1 from user where email="{log_email}"'
           cr.execute(statement2)
           name_login = ''.join(cr.fetchone())
           cr.close()
           db = sqlite3.connect('users_add.db')
           cr = db.cursor()
           user_money1 = f'select money1 from user where email="{log_email}";'
           user_money2 = f'select money2 from user where email="{log_email}";'
           message_user = f'select message from user where email="{log_email}";'
           date_first_money = f'select first_date from user where email="{log_email}";'
           cr.execute(user_money1)
           money1 = ''.join(cr.fetchone())
           cr.execute(user_money2)
           money2 = ''.join(cr.fetchone())
           cr.execute(message_user)
           message = ''.join(cr.fetchone())
           cr.execute(date_first_money)
           first_date = ''.join(cr.fetchone())
           db.commit()
           db.close()

           recipient = log_email
           conn = sqlite3.connect('messages.db')
           c = conn.cursor()
           c.execute('''SELECT COUNT(*) FROM messages
                 WHERE recipient = ? ''', (recipient,))
           count = c.fetchone()[0]
           conn.close()

           session['count'] = count

           db = sqlite3.connect('projet.db')
           cur = db.cursor()
           cur.execute('select projet from projet')
           projet = ''.join(cur.fetchone())
           cur.execute('select date_take_benifit from date_take_benifit')
           date_take_benifit = ''.join(cur.fetchone())
           cur.execute('select user_account_msg from projet')
           all_user_message = ''.join(cur.fetchone())
           db.close()
           money3 = int(money1) + int(money2)
           money4 = 1200000 - money3
           session['user_email'] = log_email
           session['money1'] = money1
           session['money2'] = money2
           session['money3'] = money3
           session['money4'] = money4
           session['projet'] = projet
           session['all_user_message'] = all_user_message
           session['user_name'] = name_login
           session['message'] = message
           session['first_date'] = first_date
           session['date_take_benifit'] = date_take_benifit
           return render_template('user_account.html' , first_name = name_login ,
                                                        money1 = money1,
                                                        money2 = money2,
                                                        money3 = money3,
                                                        money4 = money4,
                                                        projet = projet,
                                                        message = message,
                                                        first_date = first_date,
                                                        date_take_benifit = date_take_benifit,
                                                        all_user_message = all_user_message,
                                                        count = count)



@Home.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = sqlite3.connect('users_add.db')
        cr = db.cursor()
        statement = f'select name1 from user where email="{email}"'
        cr.execute(statement)
        name = cr.fetchone()
        if name is not None:
            token = str(uuid.uuid4())
            statement = f'update user set reset_token="{token}" where email="{email}";'
            cr.execute(statement)
            db.commit()
            db.close()
            reset_link = url_for('reset_password', token=token, _external=True)
            msg = Message('Reset your password', sender='nouhhamdadou@gmail.com', recipients=[email])
            msg.body = f"Hello {name},\n\nTo reset your password, please click on the following link:\n{reset_link}\n\nIf you didn't request a password reset, please ignore this email.\n\nThanks,\nElkaysar team"
            mail.send(msg)
        return '<h1 style="font-size: 50px;text-align: center;">تفقد الإيمايل الخاص بك لإعادة كلمة السر الخاصة بك</h1>'
    return render_template('forgot_password.html')

@Home.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db = sqlite3.connect('users_add.db')
    cr = db.cursor()
    statement = f'select email from user where reset_token="{token}"'
    cr.execute(statement)
    email = cr.fetchone()
    if email is None:
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = request.form['password']
        statement = f'update user set password="{password}", reset_token=null where email="{email[0]}";'
        cr.execute(statement)
        db.commit()
        db.close()
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)


@Home.route("/logout" , methods=['POST'])
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login'))

@Home.route("/home")
def user_acount():
           db = sqlite3.connect('projet.db')
           cur = db.cursor()
           cur.execute('select user_account_msg from projet')
           all_user_message = ''.join(cur.fetchone())
           db.close()


           return render_template('user_account.html' ,
                                                 all_user_message = all_user_message)





@Home.route("/admin")
def admin_acount():
  if 'user_email' not in session:
        return redirect(url_for('login'))
  else:
    img_folder = 'static/img/ccp'
    imgs = os.listdir(img_folder)

    db = sqlite3.connect('users_add.db')
    cur = db.cursor()
    cur.execute("SELECT name1,name2 , email, phone, password, dosi, user_send_money  FROM user")
    names = cur.fetchall()
    db.close()
    return render_template('admin_page.html' , imgs=imgs , names = names)

@Home.route('/admin' , methods=['POST'])
def user_modify_user():
    user_email = request.form['email_from_boss']
    message = request.form['message']
    image = request.files['user_image']
    if request.form['boss_user_control_submit'] == "إضافة إلى رأس المال":
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
        done = 'done'
        cur.execute("UPDATE user SET user_send_money = ?  WHERE email = ?", (done ,user_email ))
        db.commit()
        db.close()

        message_to_user = f'مبارك إنضمامكم الرسمي لعائلة القيصر ,لقد تم تفعيل رأس المال لديكم'

        email_template = render_template('email.html', message_to_user=message_to_user)

        msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[user_email])
        msg.body = f"Email: {user_email}\nMessage:\n{message_to_user}"
        msg.html = email_template

        mail.send(msg)

        #hadi bach ndirou update alasome ali falista te3 lmousawi9e te3 koul 3amil
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
               cursor2.execute('UPDATE {} SET money1 = ?, benefit = ? WHERE user_email = ?'.format(table[0]), (money_addd, money_benifis ,user_email))

               break
# Commit the changes to the second database
        conn2.commit()
# Close the connections
        conn2.close()

    elif request.form['boss_user_control_submit'] == "إضافة إلى الأرباح" :
        money_addd = request.form['boss_add_money']
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

        message_to_user = 'يسعد عائلة القيصر تهنأتك بحصولك على الأرباح ,لا تنسو تفقد حسابكم في الموقع'

        email_template = render_template('email.html', message_to_user=message_to_user)

        msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[user_email])
        msg.body = f"Email: {user_email}\nMessage:\n{message_to_user}"
        msg.html = email_template

        mail.send(msg)


    elif request.form['boss_user_control_submit'] == "حذف المستخدم" :
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute(f'delete from user where email ="{user_email}"')
        db.commit()
        db.close()

    elif request.form['boss_user_control_submit'] == "إرسال الرسالة" :
        sender = 'admin@help.com'
        recipient = user_email
        message = message

        conn = sqlite3.connect('messages.db')
        c = conn.cursor()

        c.execute('''INSERT INTO messages (sender, recipient, message)
                     VALUES (?, ?, ?)''', (sender, recipient, message))

        conn.commit()
        conn.close()

    elif request.form['boss_user_control_submit'] == "تصفير الأرباح" :
        money = 0
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute("UPDATE user SET money2 = ?  WHERE email = ?", (money ,user_email ))
        db.commit()
        db.close()

        message_to_user = f'بكل حب نعلمك أنه تم صب أرباحك في حسابك الرسمي وبهاذا تم تصفير أرباحك في الموقع'

        user_folder = f'static/img/user_ccp_send'
        file_name = f'{user_email}_arba7.png'
        for file in request.files.getlist("user_image"):
            file_name = f'{user_email}_raslmal.png'
            file.save(os.path.join(user_folder, file_name))

        email_template = render_template('email.html', message_to_user=message_to_user)

        msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[user_email])
        msg.body = f"Email: {user_email}\nMessage:\n{message_to_user}"
        msg.html = email_template

        with current_app.open_resource(os.path.join(user_folder, file_name)) as f:
             msg.attach(file_name, 'image/png', f.read())

        mail.send(msg)




        user_folder = f'static/img/user_case/{user_email}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        for file in request.files.getlist("user_image"):
            file_name = f'{user_email}_arba7.png'
            file.save(os.path.join(user_folder, file_name))


    elif request.form['boss_user_control_submit'] == "تصفير رأس المال" :
        money = 0
        db = sqlite3.connect('users_add.db')
        cur = db.cursor()
        cur.execute("UPDATE user SET money1 = ?  WHERE email = ?", (money ,user_email ))
        db.commit()
        db.close()
        #hadi bach naraslou lal user email fiha ataswira ali nkhayrouha m3end page admin
        message_to_user = f'تم إرسال رأس المال إلى حسابك الخاص وبهاذا تم تصفير رأس المال في الموقع'

        user_folder = f'static/img/user_ccp_send'
        file_name = f'{user_email}_raslmal.png'
        for file in request.files.getlist("user_image"):
            file_name = f'{user_email}_raslmal.png'
            file.save(os.path.join(user_folder, file_name))

        email_template = render_template('email.html', message_to_user=message_to_user)

        msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[user_email])
        msg.body = f"Email: {user_email}\nMessage:\n{message_to_user}"
        msg.html = email_template

        with current_app.open_resource(os.path.join(user_folder, file_name)) as f:
             msg.attach(file_name, 'image/png', f.read())

        mail.send(msg)

    elif request.form['boss_user_control_submit'] == "مدة طلب الأرباح" :
        date_take_benifits = request.form['date_take_benifit']
        db = sqlite3.connect('projet.db')
        cur = db.cursor()
        cur.execute(f'UPDATE date_take_benifit SET date_take_benifit = "{date_take_benifits}"')
        db.commit()
        db.close()


    db = sqlite3.connect('users_add.db')
    cur = db.cursor()
    cur.execute("SELECT name1,name2, email, phone, password, dosi, user_send_money  FROM user")
    names = cur.fetchall()
    db.close()
    return render_template('admin_page.html' , names = names)


@Home.route('/user_messages', methods=['GET'])
def user():

    recipient = session['user_email']

    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM messages
                 WHERE recipient = ?
                 ORDER BY timestamp DESC''', (recipient,))

    messages = c.fetchall()

    conn.close()

    return render_template('user_messages.html', messages=messages , user_email = session['user_email'] )



@Home.route("/projet")
def boss_project():
    return render_template ('boss_project.html')
@Home.route("/projet" , methods=['POST'])
def add_projet():

    if request.form['creat_date_submit'] == "نشر المشروع":
       projet1 = request.form['projet_text1']
       db = sqlite3.connect('projet.db')
       cur = db.cursor()
       cur.execute(f'UPDATE projet SET projet = "{projet1}"')
       db.commit()
       db.close()

    if request.form['creat_date_submit'] == 'نشر':
       projet = request.form['projet_text']
       db = sqlite3.connect('projet.db')
       cur = db.cursor()
       cur.execute(f'UPDATE projet SET user_account_msg = "{projet}"')
       db.commit()
       db.close()

    elif request.form['creat_date_submit'] == 'نشر في صفحة الموقع' :
         home_text = request.form['home_text']
         db = sqlite3.connect('projet.db')
         cur = db.cursor()
         cur.execute(f'UPDATE projet SET home_text  = "{home_text}"')
         db.commit()
         db.close()

    elif request.form['creat_date_submit'] == "نشر الصورة في صفحة الموقع" :
      if 'user_image' in request.files:
        file = request.files['user_image']
        if file.filename != '':
            file_name = 'pic_from_admin.png'
            file.save(os.path.join(Home.root_path, 'static/img', file_name))

    elif request.form['creat_date_submit'] == "نشر الفيديو في صفحة الموقع" :
      if 'user_image' in request.files:
        file = request.files['user_video']
        if file.filename != '':
            file_name = 'video_from_admin.mp4'
            file.save(os.path.join(Home.root_path, 'static/img', file_name))


    elif request.form['creat_date_submit'] == "نشر بي دي ف في صفحة الموقع" :
      if 'user_image' in request.files:
        file = request.files['user_pdf']
        if file.filename != '':
            file_name = 'pdf_from_admin.pdf'
            file.save(os.path.join(Home.root_path, 'static/img', file_name))



    return render_template('boss_project.html')


@Home.route("/boss_info")
def boss_info():
    return render_template('boss_info.html')
@Home.route("/boss_info" , methods=['POST'])
def boss_infoo():
    name = request.form['name']

    if request.form['boss_user_control_submit'] == "عرض":
       conn = sqlite3.connect("user_boss_data.db")
       cursor = conn.cursor()
       cursor.execute(f"SELECT * FROM {name}")
       data = cursor.fetchall()
       conn.close()
       return render_template("boss_info.html", data=data)

    elif request.form['boss_user_control_submit'] == "حذف المستخدم":
         conn = sqlite3.connect('user_boss_data.db')
         c = conn.cursor()
         c.execute(f'DROP TABLE IF EXISTS {name}')
         conn.commit()
         conn.close()
         return render_template('boss_info.html')


#hadi te3 bch naraslou adosi mal user
@Home.route("/case")
def case():
    return render_template("dosi.html" , user_name = session['user_name'],
                                         user_email = session['user_email'])

@Home.route("/case" , methods=['POST'])
def send_case():
            if request.method == 'POST':
                email = request.form['email']
                user_folder = f'static/img/user_case/{email}'
                if not os.path.exists(user_folder):
                   os.makedirs(user_folder)
                files = request.files.getlist("file")
                filenames = ['ID photo', 'ccp', 'deposit receipt', 'carte identite']
                for i, file in enumerate(files):
                       filename, extension = os.path.splitext(file.filename)
                       unique_filename = f"{filenames[i]}{extension}"
                       file.save(os.path.join(user_folder, unique_filename))


            db = sqlite3.connect('users_add.db')
            dosi_message = f'https://www.elkaysar.com/files/{email}'
            cur = db.cursor()
            cur.execute("UPDATE user SET dosi = ?  WHERE email = ?", (dosi_message ,email ))
            db.commit()
            db.close()

            message_to_user = f'لقد تم إكمال التسجيل بنجاح ,سيتم التحقق من ملفكم وتفعيل المبلغ في حسابكم'

            email_template = render_template('email.html', message_to_user=message_to_user)

            msg = Message(subject='القيصر للإستثمار',
              sender=('Home', 'nouhhamdadou@gmail.com'),
              recipients=[email])
            msg.body = f"Email: {email}\nMessage:\n{message_to_user}"
            msg.html = email_template

            mail.send(msg)

            return render_template('tasjil.html' ,  first_name = session['user_name'],
                                                    user_email =session['user_email'],
                                                    money1 = session['money1'] ,
                                                    money2 = session['money2'] ,
                                                    projet = session['projet'] ,
                                                    all_user_message = session['all_user_message'],
                                                    count = 0, )


@Home.route("/user_messages" , methods=['POST'])
def user_messages():
    if request.form['two_submit'] == "إرسال" :
        email = session['user_email']
        user_folder = f'static/img/user_case/{email}'
        file = request.files.get("one_picture")
        if file:
          filename, extension = os.path.splitext(file.filename)
          unique_filename = "picture_add" + extension  # specify the name of the picture here
          file.save(os.path.join(user_folder, unique_filename))

        recipient = session['user_email']
        conn = sqlite3.connect('messages.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM messages
                 WHERE recipient = ?
                 ORDER BY timestamp DESC''', (recipient,))
        messages = c.fetchall()
        conn.close()
        return render_template('user_messages.html', messages=messages , user_email = session['user_email'] )
    elif request.form['two_submit'] == "العودة إلى الصفحة الرئيسية" :
        return render_template('user_account.html' ,first_name = session['user_name'],
                                                    money1 = session['money1'],
                                                    money2 = session['money2'],
                                                    projet = session['projet'],
                                                    money3 = session['money3'],
                                                    money4 = session['money4'],
                                                    message = session['message'],
                                                    first_date = session['first_date'],
                                                    date_take_benifit = session['date_take_benifit'],
                                                    all_user_message = session['all_user_message'] )



#hadi a def darna fiha kiy3abaz al user lbutton tro7 had adef tadi man value te3 arib7
#mouda3af ra9m 3 wtonjistrih fi variable wal rest fi variable ou tmodifyi al db
@Home.route('/i3adat_istithmar', methods=['POST'])
def i3adet_istithmer():
    user_email = session['user_email']
    db = sqlite3.connect('users_add.db')
    cur = db.cursor()

    if request.form['investment'] == 'all':  # if the user chose to reinvest all the profits
        user_money2 = f'select money2 from user where email ="{user_email}";'
        cur.execute(user_money2)
        money2 = int(''.join(cur.fetchone()))
        user_money1 = f'select money1 from user where email ="{user_email}";'
        cur.execute(user_money1)
        money1 = int(''.join(cur.fetchone()))
        money1 = money2 + money1
        money2 = 0
        cur.execute("UPDATE user SET money2 = ?, money1 =?  WHERE email = ?", (money2, money1, user_email))
        db.commit()
    else:  # if the user chose to reinvest part of the profits
        user_money2 = f'select money2 from user where email ="{user_email}";'
        cur.execute(user_money2)
        money2 = int(''.join(cur.fetchone()))
        user_money1 = f'select money1 from user where email ="{user_email}";'
        cur.execute(user_money1)
        money1 = int(''.join(cur.fetchone()))

        amount = int(request.form['investment-amount-select'])  # get the amount to reinvest from the form

        if amount > money2:
            return '<h1  style:"font-size:30px;text-align:center;">أرباحك غير كافية إختر المبلغ الذي يكون اصغر أو يساوي أرباحك<h1>'

        money1 += amount
        money2 -= amount
        cur.execute("UPDATE user SET money2 = ?, money1 =?  WHERE email = ?", (money2, money1, user_email))
        db.commit()

    db.close()

    return render_template('user_account.html' , money1 = money1,
                                                 money2 = money2,
                                                 money3 = session['money3'],
                                                 money4 = session['money4'],
                                                 projet = session['projet'],
                                                 message = session['message'],
                                                 first_date = session['first_date'],
                                                 user_email = session['user_name'],
                                                 all_user_message = session['all_user_message'])

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
                                                 first_date = session['first_date'],
                                                 user_email = session['user_name'],
                                                 all_user_message = session['all_user_message'])


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
                                                 first_date = session['first_date'],
                                                 user_email = session['user_name'],
                                                 all_user_message = session['all_user_message'])


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
                                                 first_date = session['first_date'],
                                                 user_email = session['user_name'],
                                                 all_user_message = session['all_user_message'])

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
                                                 all_user_message = session['all_user_message'],
                                                 first_date = session['first_date'],
                                                 user_email = session['user_name'])


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


@Home.route('/delete-image', methods=['POST'])
def delete_image():
    data = request.get_json()
    path = data['path']
    filename = data['filename']
    full_path = os.path.join(path, filename)

    if not os.path.exists(full_path):
        response = { "success": False, "error": "File not found: " + full_path }
        print("Error deleting image:", response['error'])
        return jsonify(response)

    try:
        os.remove(full_path)
        response = { "success": True }
        print("Image deleted successfully:", full_path)
    except Exception as e:
        response = { "success": False, "error": str(e) }
        print("Error deleting image:", response['error'])

    return jsonify(response)


if __name__ == "__main__":
    Home.run( debug=False)