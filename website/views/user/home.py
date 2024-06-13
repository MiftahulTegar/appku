from website.utils.func import images
from ... import db
from ...models.user import Booking, Doctor, Time, User, Profile
from flask import Blueprint, jsonify, render_template, redirect, send_file, send_from_directory, url_for, request, flash, abort, session
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from pathlib import Path
from ... import db, app
from os import path
import os
import re
from sqlalchemy import asc

home = Blueprint('home', __name__)

upload_images = os.path.join(Path(__file__).parents[2], 'static', app.config.get('UPLOAD_FOLDER', ''))
named_img = os.path.join(Path(__file__).parents[5], app.config.get('UPLOAD_FOLDER', ''))

@home.route('/beranda', methods=['GET', 'POST'])
@login_required
def beranda():
    doctors = Doctor.query.all()
    results = []
    for data in doctors:
        photo_path = data.photo.replace('E:\\', '').replace('\\', '/')
        photo_path = photo_path.replace('/static', '/static/storage')
        results.append({
            'id' : data.id,
            'name': data.name,
            'telp': data.telp,
            'information': data.information,
            'time': data.time,
            'photo': photo_path,
        })

    return render_template('user/home.html', doctors=results)

@home.route('/get-confirmed-times')
def get_confirmed_times():
    selected_date = request.args.get('date')
    confirmed_times = Booking.query.filter_by(date=selected_date, status="confirmed").all()
    confirmed_times_list = [booking.time for booking in confirmed_times]
    return jsonify({'confirmed_times': confirmed_times_list})

import locale
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
def format_date_with_day(date_obj):
    return date_obj.strftime('%A, %d-%m-%Y')

from datetime import datetime, timedelta

def get_time_slots(time_range):
    start_time_str, end_time_str = time_range.split(' s.d ')
    start_time = datetime.strptime(start_time_str, '%H.%M')
    end_time = datetime.strptime(end_time_str.split()[0], '%H.%M')  # Remove 'WIB'

    time_slots = []

    while start_time + timedelta(hours=1) <= end_time:
        end_slot = (start_time + timedelta(hours=1)).strftime('%H.%M')
        time_slots.append(f"{start_time.strftime('%H.%M')} s.d {end_slot} WIB")
        start_time += timedelta(hours=1)

    return time_slots

@home.route('/form-konsultasi', methods=['GET', 'POST'])
@login_required
def formkonsultasi():
    id = request.args.get('id')
    doctors = Doctor.query.filter_by(id=id).first()
    if request.method == 'POST':
        id_doctor = request.form.get('id')
        name = request.form.get('name')
        telp = request.form.get('telp')
        time = request.form.get('time')
        date = request.form.get('date')

        # Validasi data
        if not all([name, telp, time, date]):
            flash('Semua bidang harus diisi.', 'error')
            return redirect(url_for('home.formkonsultasi', id=id))
        
        new_doctor = Booking(
            telp=telp,
            time=time,
            date=date,
            status="waiting",
            customer_id=current_user.id,
            doctor_id=id_doctor,
        )
        db.session.add(new_doctor)
        db.session.commit()

        flash('Jadwal konsultasi berhasil dibuat.', 'success')
        return redirect(url_for('home.data_konsultasi'))
        
    option_all = Time.query.order_by(asc(Time.time)).all()
    time_slots = get_time_slots(doctors.time) 
    return render_template('user/konsultasi.html', doctors=doctors, option_all=option_all, time_slots=time_slots)

@home.route('/data-konsultasi', methods=['GET', 'POST'])
@login_required
def data_konsultasi():
    viewDoctor = Booking.query.filter_by(customer_id=current_user.id).all()
    results = []
    for booking in viewDoctor:
        results.append(
            {
                'id': booking.id,
                'telp': booking.telp,
                'time': booking.time,
                'date': format_date_with_day(booking.date),
                'status': booking.status,
                'spcustomer': {
                    'name': booking.spcustomer.profile.name,
                },
                'spdoctor': {
                    'profile': {
                        'name': booking.spdoctor.name
                    }
                }
            }
        )
    return render_template('user/datakonsultasi.html', datas=results)

@home.route('/data-dokter-praktik', methods=['GET', 'POST'])
@login_required
def data_dokter():
    doctors = Doctor.query.all()
    results = []
    for data in doctors:
        photo_path = data.photo.replace('E:\\', '').replace('\\', '/')
        photo_path = photo_path.replace('/static', '/static/storage')
        results.append({
            'id' : data.id,
            'name': data.name,
            'telp': data.telp,
            'information': data.information,
            'time': data.time,
            'photo': photo_path,
        })
    return render_template('user/datadokter.html', datas=results)