from website.utils.func import images
from ... import db
from ...models.user import User, Profile
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash, abort, session
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from pathlib import Path
from ... import db, app
from os import path
import os
import re

auth = Blueprint('auth', __name__)

upload_images = path.join(Path(__file__).parents[2], "static", app.config['UPLOAD_FOLDER'])

@auth.route('/', methods=['GET', 'POST'])
def home():
    return render_template('autentikasi/login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user)
                    if user.role == "admin" :
                        return redirect(url_for('DBhome.dashboard'))
                    else :
                        return redirect(url_for('home.beranda'))
            flash('Username atau Password salah.', category='error')
            return redirect(url_for('auth.login'))
        return render_template('autentikasi/login.html', user=current_user)
    except Exception as e:
        print(e)
        abort(404)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    try:

        if request.method == 'POST':
            name = request.form.get('name')
            username = request.form.get('username')
            address = request.form.get('address')
            password = request.form.get('password')
            
            try:

                # Check if username already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username sudah terdaftar. Silakan gunakan username lain.', category='error')
                    return redirect(url_for('auth.register'))

                # Password validation
                if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$', password):
                    flash('Password harus minimal 8 karakter dan mencakup huruf, angka, dan simbol.', category='error')
                    return redirect(url_for('auth.register'))

                # Password hashing
                hashed_password = generate_password_hash(password, method='sha256')

                # Create a new user
                new_user = User(username=username, password=hashed_password, role="user")
                db.session.add(new_user)
                db.session.commit()

                # Create a new profile
                new_profile = Profile(name=name, address=address, user_id=new_user.id)
                db.session.add(new_profile)
                db.session.commit()

                flash('Registrasi berhasil. Silahkan masuk.', category='success')
                return redirect(url_for('auth.login'))
            
            except Exception as e:
                flash('Registrasi gagal. Coba lagi nanti.', category='error')
                return redirect(url_for('auth.register'))
            
        return render_template('autentikasi/register.html', user=current_user)
        
    except Exception as e:
        print(e)
        abort(404)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
