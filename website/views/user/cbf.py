from ...models.user import Treatment
from flask import Blueprint, render_template, redirect, url_for, request, flash
from pathlib import Path
from ... import app
from os import path

cbf_algoritma = Blueprint('cbf_algoritma', __name__)

upload_images = path.join(Path(__file__).parents[2], 'static', app.config['UPLOAD_FOLDER'])
named_img = path.join(Path(__file__).parents[5], app.config['UPLOAD_FOLDER'])

def hitung_kesamaan(kasus_baru, kasus_lama):
   
    kesamaan = 0

    # Hitung kesamaan gejala dengan bobot
    for gejala in kasus_baru['gejala'].split(","):
        gejala = gejala.strip().lower()
        if gejala in kasus_lama.treatment.lower():
            kesamaan += 0.3 * 1  # Bobot untuk gejala

    # Hitung kesamaan jenis kulit dengan bobot
    for jenis_kulit in kasus_baru['jenis_kulit'].split(","):
        jenis_kulit = jenis_kulit.strip().lower()
        if jenis_kulit in kasus_lama.skin.lower():
            kesamaan += 0.7 * 1  # Bobot untuk jenis kulit

    return kesamaan

@cbf_algoritma.route('/layanan-konsultasi', methods=['GET', 'POST'])
def input_gejala():

    if request.method == 'POST':
        gejala = request.form['gejala'].lower()
        jenis_kulit = request.form['jenis_kulit'].lower()

        kasus_baru = {'gejala': gejala, 'jenis_kulit': jenis_kulit}
        semua_kasus = Treatment.query.all()

        if semua_kasus:
            # Hitung kesamaan dengan semua kasus
            kesamaan_list = [(hitung_kesamaan(kasus_baru, kasus), kasus) for kasus in semua_kasus]

            # Urutkan kesamaan_list berdasarkan nilai kesamaan secara descending
            kesamaan_list.sort(key=lambda x: x[0], reverse=True)

            # Ambil k kasus terdekat (k = 5)
            k_terdekat = kesamaan_list[:5]

            # Rekomendasi berdasarkan voting
            rekomendasi_voting = None
            rekomendasi_vote_count = 0
            for _, kasus in k_terdekat:
                rekomendasi_kandidat = kasus.treatment
                if rekomendasi_kandidat != rekomendasi_voting:
                    rekomendasi_voting = rekomendasi_kandidat
                    rekomendasi_vote_count = 1
                else:
                    rekomendasi_vote_count += 1

            # Rekomendasi dengan bobot kesamaan
            rekomendasi_bobot = None
            rekomendasi_bobot_score = 0
            for _, kasus in k_terdekat:
                rekomendasi_kandidat = kasus.treatment
                kesamaan_kandidat = hitung_kesamaan(kasus_baru, kasus)
                if kesamaan_kandidat > rekomendasi_bobot_score:
                    rekomendasi_bobot = rekomendasi_kandidat
                    rekomendasi_bobot_score = kesamaan_kandidat

            # Pilih rekomendasi terbaik
            rekomendasi = rekomendasi_voting if rekomendasi_vote_count > 1 else rekomendasi_bobot

            final_rekomendasi = Treatment.query.filter_by(treatment=rekomendasi).first()

            if rekomendasi:
                # Tampilkan rekomendasi
                return render_template('user/rekomendasi.html', rekomendasi=final_rekomendasi)
            else:
                # Tidak ada rekomendasi yang cocok
                flash('Tidak ada rekomendasi perawatan yang ditemukan untuk gejala dan jenis kulit ini.', 'error')
                return redirect(url_for('cbf_algoritma.input_gejala'))
        else:
            # Tidak ada data kasus yang tersedia
            flash('Tidak ada data kasus yang tersedia.', 'error')
            return redirect(url_for('cbf_algoritma.input_gejala'))

    return render_template('user/case.html')

