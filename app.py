import math
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
from flask_mail import Mail
import pymysql

pymysql.install_as_MySQLdb()

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config['COMPANY_UPLOAD_FOLDER'] = params['company_upload_location']
app.config['ALUMNI_PIC_UPLOAD_FOLDER'] = params['alumni_pic_upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    tittle = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(100), nullable=True)


class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.Text, nullable=False)
    company_cat = db.Column(db.Text, nullable=False)
    company_desc = db.Column(db.Text, nullable=False)
    company_ctc = db.Column(db.Float, nullable=False)
    company_img = db.Column(db.String(100), nullable=True)
    company_url = db.Column(db.Text, nullable=False)
    company_career_url = db.Column(db.Text, nullable=False)
    company_linkedin_url = db.Column(db.Text, nullable=False)

class AlumniStudents(db.Model):
    alumni_id = db.Column(db.Integer, primary_key=True)
    register_no = db.Column(db.String(15), nullable=False)
    first_name = db.Column(db.String(45), unique=False, nullable=False)
    last_name = db.Column(db.String(45), unique=False, nullable=False)
    email_ID = db.Column(db.String(45), unique=True, nullable=False)
    phone_no = db.Column(db.String(12), unique=True, nullable=False)
    college_name = db.Column(db.String(45), unique=False, nullable=True)
    DOB = db.Column(db.String(15), unique=False, nullable=False)
    Gender = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    confirm_password = db.Column(db.String(20), unique=False, nullable=False)
    linkedin_profile = db.Column(db.String(80), unique=False, nullable=True)
    github_profile = db.Column(db.String(80), unique=False, nullable=True)
    other_links = db.Column(db.String(80), unique=False, nullable=True)
    profile_pic = db.Column(db.String(80), unique=False, nullable=True)
    alumni_about = db.Column(db.String(6000), unique=False, nullable=True)

@app.route('/home')
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    # [0:params['no_of_posts']]
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']): (page - 1) * int(params['no_of_posts']) + int(params['no_of_posts'])]
    # Pagination Logic :-
    # First :-
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    companies = Company.query.filter_by().all()
    return render_template('post.html', params=params, post=post, companies=companies)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/companyGallery", methods=['GET'])
def companyGallery():
    companies = Company.query.filter_by().all()
    return render_template('companyGallery.html', params=params, companies=companies)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
        else:
            flash('Incorrect username or password', 'danger')
    return render_template('login.html', params=params)


@app.route("/alumniDashboard", methods=['GET', 'POST'])
def alumniDashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        alumnistudents = AlumniStudents.query.all()
        return render_template('alumniDashboard.html', params=params, alumnistudents=alumnistudents)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            alumnistudents = AlumniStudents.query.all()
            return render_template('alumniDashboard.html', params=params, alumnistudents=alumnistudents)
        else:
            flash('Incorrect username or password', 'danger')
    return render_template('login.html', params=params)

@app.route("/companyDashboard", methods=['GET', 'POST'])
def companyDashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        companies = Company.query.all()
        return render_template('companyDashboard.html', params=params, companies=companies)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            companies = Company.query.all()
            return render_template('companyDashboard.html', params=params, companies=companies)
        else:
            flash('Incorrect username or password', 'danger')
    return render_template('login.html', params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file1']
            if f.filename == '':
                pass
            else:
                # secure_filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            box_tittle = request.form.get('tittle')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno == '0':
                if box_tittle == '' and tline == '' and slug == '' and content == '':
                    flash('Below fields are mandatory to create a post!', 'danger')
                else:
                    post = Posts(tittle=box_tittle, slug=slug, content=content,
                                 tagline=tline, img_file=img_file, date=date)
                    db.session.add(post)
                    db.session.commit()
                    flash('Post has been added successfully', 'success')
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.tittle = box_tittle
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                flash('Post has been edited successfully', 'success')

                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)

@app.route("/alumniEdit/<string:alumni_id>", methods=['GET', 'POST'])
def alumniEdit(alumni_id):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file2']
            if f.filename == '':
                pass
            else:
                # secure_filename
                f.save(os.path.join(app.config['ALUMNI_PIC_UPLOAD_FOLDER'], f.filename))

            registerNum = request.form.get('registerNo')
            firstName = request.form.get('fname')
            lastName = request.form.get('lname')
            alumniBio = request.form.get('alumniAbout')
            alumniLinkedIn = request.form.get('alumniLinkedin')
            alumniGitHub = request.form.get('alumniGithub')
            alumniTwitterUrl = request.form.get('alumniTwitter')
            alumniCollegeName = request.form.get('collegeName')
            alumniProfilePic = request.form.get('profilePic')

            if alumni_id == '0':
                if registerNum == '' and firstName == '' and lastName == '' and alumniBio == '' and alumniCollegeName == '':
                    flash('Below fields are mandatory to add details!', 'danger')
                else:
                    alumnistudents = AlumniStudents(register_no=registerNum, first_name=firstName, last_name=lastName, alumni_about=alumniBio, linkedin_profile=alumniLinkedIn, github_profile=alumniGitHub, other_links=alumniTwitterUrl, college_name=alumniCollegeName, profile_pic=alumniProfilePic)
                    db.session.add(alumnistudents)
                    db.session.commit()
                    flash('Alumni details has been added successfully', 'success')
            else:
                alumnistudents = AlumniStudents.query.filter_by(alumni_id=alumni_id).first()
                print(f"Alumni ID: {alumni_id}")

                alumnistudents.first_name = firstName
                alumnistudents.last_name = lastName
                alumnistudents.alumni_about = alumniBio
                alumnistudents.linkedin_profile = alumniLinkedIn
                alumnistudents.github_profile = alumniGitHub
                alumnistudents.other_links = alumniTwitterUrl
                alumnistudents.college_name = alumniCollegeName
                alumnistudents.profile_pic = alumniProfilePic
                db.session.commit()
                flash('Alumni details has been edited successfully', 'success')

                return redirect('/alumniDashboard')
        alumnistudents = AlumniStudents.query.filter_by(alumni_id=alumni_id).first()
        return render_template('alumniEdit.html', params=params, alumnistudents=alumnistudents, alumni_id=alumni_id)

@app.route("/companyEdit/<int:company_id>", methods=['GET', 'POST'])
def companyEdit(company_id):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file2']
            if f.filename == '':
                pass
            else:
                # secure_filename
                f.save(os.path.join(app.config['COMPANY_UPLOAD_FOLDER'], f.filename))

            companyName = request.form.get('name')
            companyCat = request.form.get('category')
            companyDesc = request.form.get('desc')
            companyCTC = request.form.get('companyctc')
            companyImg = request.form.get('companyImage')
            companyURL = request.form.get('companyLink')
            companyCareerURL = request.form.get('companyCareerLink')
            companyLinkedinURL = request.form.get('companyLinkedinLink')

            if company_id == 0:
                if companyName == '' and companyCat == '' and companyDesc == '' and companyCTC == '':
                    flash('Below fields are mandatory to add a company!', 'danger')
                else:
                    company = Company(company_name=companyName, company_cat=companyCat, company_desc=companyDesc, company_ctc=companyCTC,
                                company_img=companyImg, company_url=companyURL, company_career_url=companyCareerURL,
                                company_linkedin_url=companyLinkedinURL)
                    db.session.add(company)
                    db.session.commit()
                    flash('company has been added successfully', 'success')
            else:
                company = Company.query.filter_by(company_id=company_id).first()
                company.company_name = companyName
                company.company_cat = companyCat
                company.company_desc = companyDesc
                company.company_ctc = companyCTC
                company.company_img = companyImg
                company.company_url = companyURL
                company.company_career_url = companyCareerURL
                company.company_linkedin_url = companyLinkedinURL
                db.session.commit()
                flash('Company has been edited successfully', 'success')

                return redirect('/companyEdit/' + str(company_id))
        company = Company.query.filter_by(company_id=company_id).first()
        return render_template('companyEdit.html', params=params, company=company, company_id=company_id)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        flash('Post has been deleted successfully', 'success')
    return redirect('/dashboard')


@app.route("/companyDelete/<int:company_id>", methods=['GET', 'POST'])
def companyDelete(company_id):
    if 'user' in session and session['user'] == params['admin_user']:
        company = Company.query.filter_by(company_id=company_id).first()
        db.session.delete(company)
        db.session.commit()
        flash('Company has been deleted successfully', 'success')
    return redirect('/companyDashboard')

@app.route("/alumniProfile", methods=['GET', 'POST'])
def alumniProfile():
    return render_template('alumniProfile.html', params=params)

# Login page using python flask
@app.route("/alumniLogin", methods=['GET', 'POST'])
def alumniLogin():
    if request.method == 'POST':
        registerNum = request.form.get('registerNum')
        password = request.form.get('password')
        alumnistudents = AlumniStudents.query.filter_by(register_no=registerNum).first()
        if alumnistudents is not None:
            if alumnistudents.password == password:
                session['user'] = registerNum
                flash('Logged in successfully!', 'success')
                return redirect('/alumniDashboard')
            else:
                flash('Incorrect Password!', 'danger')
        else:
            flash('Incorrect Register Number!', 'danger')

    return render_template('alumniSignup.html', params=params)


@app.route("/", methods=['GET', 'POST'])
def alumniSignup():
    if request.method == 'POST':
        '''Add entry to the database'''
        registration_no = request.form.get('reg_no')
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        phone_no = request.form.get('phone')
        email_id = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        dob = request.form.get('dob')
        gender = request.form.get('gender')

        entry = AlumniStudents(register_no=registration_no, first_name=fname, last_name=lname, email_ID=email_id, phone_no=phone_no, DOB = dob, Gender=gender, password=password, confirm_password=confirm_password)

        db.session.add(entry)
        db.session.commit()
        return redirect('/alumniProfile')
    return render_template('alumniSignup.html', params=params)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, email=email, phone_no=phone,
                         msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )
        flash('Thank You for contacting us', 'success')
    return render_template('contact.html', params=params)


@app.route("/companyGallery", methods=['GET', 'POST'])
def searchBook():
    words1 = request.form.get('search')
    companySearch1 = Company.query.filter_by().all()
    # print(f" array {bookSearch1}")
    searchResult = []
    for company1 in companySearch1:
        if company1.company_name.lower() == words1.lower() or company1.company_cat.lower() == words1.lower():
            # print(f"company- {company1}")
            searchResult.append(company1)
    if len(searchResult) == 0:
        wordArray = words1.split(" ")
        for company2 in companySearch1:
            for word in wordArray:
                if company2.company_name.lower() == word.lower() or company2.company_cat.lower() == word.lower():
                    searchResult.append(company2)
    return render_template('companyGallery.html', params=params, companies=searchResult)


if __name__ == '__main__':
    app.run(debug=True)
