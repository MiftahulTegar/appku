from datetime import date, datetime
from website.models.utils.export import Export
from website.utils.func import images
from ... import db
from ...models.user import Booking, Doctor, Treatment, TypeTreatment, User, Profile
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash, make_response
from flask_login import login_required
from pathlib import Path
from ... import db, app
from os import path
import os
from dotenv import load_dotenv
import locale

DBhome = Blueprint('DBhome', __name__)

load_dotenv(path.join(path.dirname(__file__), '.env'))
upload_images = path.join(Path(__file__).parents[2], 'static', app.config['UPLOAD_FOLDER'])
named_img = path.join(Path(__file__).parents[5], app.config['UPLOAD_FOLDER'])

######################### DASHBOARD #########################

@DBhome.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    countUser = User.query.all()
    countDoctor = Doctor.query.all()
    countTreatment = Treatment.query.all()
    return render_template('admin/home.html', countUser=countUser, countDoctor=countDoctor, countTreatment=countTreatment)

######################### DATA KONSULTASI #########################

@DBhome.route('/data-dokter', methods=['GET', 'POST', 'DELETE'])
@login_required
def doctor():
    viewDoctor = Doctor.query.all()
    return render_template('admin/konsultasi/dokter.html', viewDoctor=viewDoctor)

@DBhome.route('data-dokter/tambah-data-dokter', methods=['GET', 'POST'])
@login_required
def adddoctor():
    if request.method == 'POST':
        name = request.form.get('name')
        photo = request.files.get('photo')
        telp = request.form.get('telp')
        time = request.form.get('time')
        date = request.form.get('date')
        information = request.form.get('information')

        # Validasi data
        if not all([name, photo, telp, date, time, information]):
            flash('Semua bidang harus diisi.', 'error')
            return redirect(url_for('DBhome.adddoctor'))

        if photo and images(photo.filename):
            user_dir = path.join(upload_images)
            if not path.exists(user_dir):
                os.makedirs(user_dir)
                    
            extension = photo.filename.split(".")[-1]
            photo_filename = f'{name}_{telp}.{extension}'
            photo_filenamed = path.join(user_dir, photo_filename)
            photo_path = path.join(app.config['UPLOAD_FOLDER'], named_img, photo_filename)
            photo.save(photo_filenamed)

            # Tambahkan data dokter baru ke database
            new_doctor = Doctor(
                name=name,
                photo=photo_path,
                telp=telp,
                date=date,
                time=time,
                information=information
            )
            db.session.add(new_doctor)
            db.session.commit()

            flash('Data dokter berhasil ditambahkan.', 'success')
            return redirect(url_for('DBhome.doctor'))
        
        else :

            flash('Data gagal ditambahkan.', 'error')
            return redirect(url_for('DBhome.adddoctor'))

    return render_template('admin/konsultasi/add-dokter.html')

@DBhome.route('data-dokter/ubah-data-dokter', methods=['GET', 'POST', 'PUT'])
@login_required
def editdoctor():
    
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        photo = request.files.get('photo')
        telp = request.form.get('telp')
        time = request.form.get('time')
        date = request.form.get('date')
        information = request.form.get('information')

        doctorData = Doctor.query.filter_by(id=id).first()

        # Validasi data
        if photo and images(photo.filename):
            user_dir = path.join(upload_images)
            if not path.exists(user_dir):
                os.makedirs(user_dir)
                    
            extension = photo.filename.split(".")[-1]
            photo_filename = f'{name}_{telp}.{extension}'
            photo_filenamed = path.join(user_dir, photo_filename)
            photo_path = path.join(app.config['UPLOAD_FOLDER'], named_img, photo_filename)
            photo.save(photo_filenamed)

            doctorData.name = name
            doctorData.photo = photo_path
            doctorData.telp = telp
            doctorData.time = time
            doctorData.date = date
            doctorData.information = information
            db.session.commit()

            flash('Data dokter berhasil diubah.', 'success')
            return redirect(url_for('DBhome.doctor'))

        else :

            doctorData.name = name
            doctorData.telp = telp
            doctorData.time = time
            doctorData.date = date
            doctorData.information = information
            db.session.commit()

            flash('Data dokter berhasil diubah.', 'success')
            return redirect(url_for('DBhome.doctor'))
    
    id = request.args.get('id')
    doctor = Doctor.query.filter_by(id=id).first()
    return render_template('admin/konsultasi/edit-dokter.html', doctorData=doctor)

@DBhome.route('/hapus-data-dokter', methods=['POST'])
@login_required
def deletedoctor():
    id = request.form.get('id')
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({'success': False, 'message': 'Data dokter tidak ditemukan.'})

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Data dokter berhasil dihapus.'})

locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
def format_date_with_day(date_obj):
    return date_obj.strftime('%A, %d-%m-%Y')
                                 
@DBhome.route('/jadwal-dokter', methods=['GET', 'POST'])
@login_required
def datekonsultasi():
    viewDoctor = Booking.query.all()
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

    return render_template('admin/konsultasi/konsultasi.html', results=results)

@DBhome.route('/search', methods=['POST'])
def search():
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

    filtered_bookings = []
    for booking in Booking.query.filter(Booking.date.between(start_date, end_date)).all():
        filtered_bookings.append(
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

    return render_template('admin/konsultasi/konsultasi.html', results=filtered_bookings)

@app.route('/update-booking-status/<booking_id>', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    data = request.get_json()
    status = data.get('status')
    
    booking = Booking.query.filter_by(id=booking_id).first()
    if booking:
        booking.status = status
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

######################### DATA TYPE TREATMENT #########################

@DBhome.route('/data-type-treatment', methods=['GET', 'POST', 'DELETE'])
@login_required
def type_treatment():
    type_treatment = TypeTreatment.query.all()
    return render_template('admin/treatment/type.html', type_treatment=type_treatment)

@DBhome.route('/add_type_treatment', methods=['POST'])
def add_type_treatment():
    data = request.get_json()
    treatment_type = data.get('treatmentType')
    if treatment_type:
        new_treatment = TypeTreatment(type=treatment_type)
        db.session.add(new_treatment)
        db.session.commit()
        flash('Data type treatment berhasil ditambahkan.', 'success')
        return jsonify({"success": True, "message": "Type Treatment added successfully"}), 200
    else:
        flash('Data type treatment gagal ditambahkan.', 'error')
        return jsonify({"success": False, "message": "Type Treatment is required"}), 400
    
@DBhome.route('/edit_type_treatment', methods=['POST'])
def edit_type_treatment():
    data = request.get_json()
    treatment_id = data.get('id')
    treatment_type = data.get('type')
    if treatment_id and treatment_type:
        treatment = TypeTreatment.query.get(treatment_id)
        if treatment:
            treatment.type = treatment_type
            db.session.commit()
            flash('Data type treatment berhasil diubah.', 'success')
            return jsonify({"success": True, "message": "Type Treatment updated successfully"}), 200
        else:
            flash('Data type treatment tidak diketahui.', 'error')
            return jsonify({"success": False, "message": "Type Treatment not found"}), 404
    else:
        flash('Data type treatment gagal diubah.', 'error')
        return jsonify({"success": False, "message": "Invalid data"}), 400

@DBhome.route('/delete_type_treatment', methods=['POST'])
@login_required
def delete_type_treatment():
    id = request.form.get('id')
    type = TypeTreatment.query.get(id)
    if not type:
        return jsonify({'success': False, 'message': 'Data treatment tidak ditemukan.'})

    db.session.delete(type)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Data treatment berhasil dihapus.'})

######################### DATA TREATMENT #########################

@DBhome.route('/data-treatment', methods=['GET', 'POST', 'DELETE'])
@login_required
def treatment():
    treatment = Treatment.query.all()
    return render_template('admin/treatment/treatment.html', treatment=treatment)

import pandas as pd
import io, os

@DBhome.route('/import-treatment', methods=['GET', 'POST', 'DELETE'])
@login_required
def import_treatment():
    try:
        if request.method == 'POST':
            file = request.files.get('file')
            if file:
                df = pd.read_excel(file, na_filter=False)

                for index, row in df.iterrows():
                    try:
                        cek_Treatment = Treatment.query.filter_by(treatment=row['Treatment']).first()
                        cek_TypeTreatment = TypeTreatment.query.filter_by(type=row['Type Treatment']).first()
                        
                        if not cek_Treatment:
                            if cek_TypeTreatment:
                                save = Treatment(
                                    treatment=row['Treatment'], 
                                    benefit=row['Manfaat'], 
                                    skin=row['Jenis Kulit'], 
                                    information=row['Informasi'], 
                                    type_id=cek_TypeTreatment.id
                                )
                                db.session.add(save)
                                db.session.commit()
                            else:
                                flash(f"Import Gagal! Data Type Treatment tidak terdaftar.", category='error')
                        else:
                            if cek_TypeTreatment:
                                cek_Treatment.treatment = row['Treatment']
                                cek_Treatment.benefit = row['Manfaat']
                                cek_Treatment.skin = row['Jenis Kulit']
                                cek_Treatment.information = row['Informasi']
                                cek_Treatment.type_id = cek_TypeTreatment.id
                                db.session.commit()
                            else:
                                flash(f"Import Gagal! Data Type Treatment tidak terdaftar.", category='error')

                    except Exception as e:
                        print(f"Error processing row {index}: {e}")
                        flash(f"Terdapat kolom kosong yang tidak dapat diimport.", category='error')

            flash("Data berhasil diimport.", category='success')
            return redirect(url_for('DBhome.treatment'))  

        return render_template('admin/treatment/treatment.html')  
    
    except Exception as e:
        print(e)
        flash("Terjadi kesalahan pada server.", category='error')
        return redirect(url_for('DBhome.treatment'))  
    

@DBhome.route('/export-treatment', methods=['GET', 'POST', 'DELETE'])
@login_required
def export_treatment():
    try:
        if 'export' in request.args:
            if request.args.get('export') == 'excel':
                export = Export(Treatment).Export_Treatments()
                df = pd.DataFrame((tuple(item) for item in export), columns=('Type Treatment', 'Treatment', 'Manfaat',
                                  'Jenis Kulit', 'Informasi'))
                out = io.BytesIO()
                writer = pd.ExcelWriter(out, engine='xlsxwriter')
                df.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
                writer.close()
                response = make_response(out.getvalue())
                response.headers[
                    "Content-Disposition"] = f"attachment; filename=export_{date.today()}.xlsx"
                response.headers["Content-type"] = "application/x-xls"
                return response
            
        return render_template('admin/treatment/treatment.html')  
    
    except Exception as e:
        print(e)
        flash("Terjadi kesalahan pada server.", category='error')
        return redirect(url_for('DBhome.treatment'))  

@DBhome.route('data-treatment/ubah-data-treatment', methods=['GET', 'POST', 'PUT'])
@login_required
def edittreatment():
    
    if request.method == 'POST':
        id = request.form.get('id')
        type = request.form.get('type')
        treatment = request.form.get('treatment')
        benefit = request.form.get('benefit')
        skin = request.form.get('skin')
        information = request.form.get('information')
        information = request.form.get('information')

        TreatmentData = Treatment.query.filter_by(id=id).first()
        typesData = TypeTreatment.query.filter_by(id=type).first()

        # Validasi data
        TreatmentData.type_id = typesData.id
        TreatmentData.treatment = treatment
        TreatmentData.benefit = benefit
        TreatmentData.skin = skin
        TreatmentData.information = information
        TreatmentData.information = information
        db.session.commit()

        flash('Data dokter berhasil diubah.', 'success')
        return redirect(url_for('DBhome.treatment'))
    
    id = request.args.get('id')
    treatments = Treatment.query.filter_by(id=id).first()
    types = TypeTreatment.query.all()
    return render_template('admin/treatment/edit-treatment.html', treatments=treatments, types=types)

@DBhome.route('/delete_treatment', methods=['POST'])
@login_required
def delete_treatment():
    id = request.form.get('id')
    type = Treatment.query.get(id)
    if not type:
        return jsonify({'success': False, 'message': 'Data treatment tidak ditemukan.'})

    db.session.delete(type)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Data treatment berhasil dihapus.'})

######################################################################

