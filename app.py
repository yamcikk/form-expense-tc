import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

st.title("Form Laporan Expense Lapangan")
st.markdown("Isi form pengeluaran ini langsung dari HP. Pastikan foto diambil *real-time*.")

# Membuat Form Input
with st.form("expense_form"):
    nama = st.text_input("Nama Sales / Supervisor")
    area = st.text_input("Area Coverage")
    tanggal = st.date_input("Tanggal Kegiatan")
    
    # Opsi kegiatan disesuaikan dengan aktivitas operasional harian
    post_kegiatan = st.selectbox(
        "Post Kegiatan", 
        ["Demo Plot Pupuk", "Edukasi Petani", "Kunjungan Toko/Kios", "Entertain/Meeting", "Lainnya"]
    )
    
    keterangan = st.text_area("Keterangan Kegiatan (Nama toko, agenda, dll.)")
    nominal = st.number_input("Nominal Pengeluaran (Rp)", min_value=0, step=5000)
    
    # Fitur Kamera HP (Wajib foto langsung untuk validasi timestamp)
    st.write("Dokumentasi (Nota / Bukti Kegiatan)")
    foto = st.camera_input("Ambil Foto Sekarang")

    submitted = st.form_submit_button("Submit Laporan")

# Logika setelah tombol Submit ditekan
if submitted:
    if nama and area and nominal > 0 and foto:
        waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Data pengeluaran Rp {nominal:,} berhasil dicatat pada {waktu_input}!")
        
        # 1. Menyiapkan Sheet Rekap (Sesuai format Excel HO)
        df_rekap = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d-%m-%Y"),
            "Nama Sales": nama,
            "Area": area,
            "Post Kegiatan": post_kegiatan,
            "Keterangan": keterangan,
            "Nominal (Rp)": nominal
        }])
        
        # 2. Menyiapkan Sheet Dokumentasi
        df_dokumen = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d-%m-%Y"),
            "Nama Sales": nama,
            "Nama File Bukti": foto.name,
            "Timestamp Sistem (Waktu Upload)": waktu_input,
            "Status Lampiran": "Terlampir di Database/Drive"
        }])
        
        # 3. Proses Konversi ke File Excel (.xlsx)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_rekap.to_excel(writer, sheet_name='Rekap Pengeluaran', index=False)
            df_dokumen.to_excel(writer, sheet_name='Dokumentasi', index=False)
        
        # Tombol Unduh untuk simulasi pengambilan data oleh tim HO
        st.download_button(
            label="⬇️ Unduh File Excel (Format HO)",
            data=output.getvalue(),
            file_name=f"Expense_{nama}_{tanggal}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Gagal! Pastikan Nama, Area, Nominal, dan Foto Kamera sudah terisi.")
