import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

st.title("PT. DGW FIT")
st.subheader("Form Laporan Expense (AST TCS TC NASIONAL)")

# Membuat Form Input
with st.form("expense_form"):
    nama = st.text_input("Nama Sales / Supervisor", value="DIKA APRILYANTO")
    jabatan = st.text_input("Jabatan", value="ASS.TCS")
    area = st.text_input("Area", value="TC Magelang - Jawa Tengah")
    
    st.markdown("---")
    
    # Input Data Transaksi
    tanggal = st.date_input("Date (Tanggal Pembelian)")
    tempat = st.text_input("Tempat Pembelian (Misal: RM.Sekar Keraton Pajang)")
    alamat = st.text_input("Alamat Pembelian (Misal: Jl. Magelang-Purworejo KM 23)")
    nama_pic = st.text_input("Nama PIC (Misal: Dika Aprilyanto, Ahmad Nabiel Z, dll)")
    posisi_pic = st.text_input("Posisi PIC (Misal: Ass.TCS, FA RnD, MT)")
    perusahaan = st.text_input("Perusahaan", value="PT.FIT")
    
    # Opsi Kategori Form (Non Bill / Meals / Gasoline)
    kategori = st.selectbox(
        "Kategori Pengeluaran",
        ["Non Bill / Gasoline (G) - GNB", "Meals (M) - MB", "Gasoline (G)"]
    )
    
    deskripsi = st.text_area("Description (Keterangan Kegiatan)")
    alasan_non_bill = st.text_area("Alasan Non Bill (Jika ada)")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    st.markdown("---")
    
    # Fitur Kamera HP (Dokumentasi wajib timestamp)
    st.write("**Dokumentasi (Wajib Lampirkan Bukti Ber-Timestamp)**")
    foto = st.camera_input("Ambil Foto Sekarang")

    submitted = st.form_submit_button("Submit Laporan")

# Logika setelah tombol Submit ditekan
if submitted:
    if tempat and deskripsi and nominal > 0 and foto:
        waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Data pengeluaran Rp {nominal:,} berhasil dicatat pada {waktu_input}!")
        
        # 1. Menyiapkan Sheet Rekap (Format persis dengan Excel HO)
        df_rekap = pd.DataFrame([{
            "Date": tanggal.strftime("%d/%m/%Y"),
            "Tempat Pembelian": tempat,
            "Alamat Pembelian": alamat,
            "Nama PIC": nama_pic,
            "Posisi": posisi_pic,
            "Perusahaan": perusahaan,
            "Description": deskripsi,
            "Alasan Non Bill": alasan_non_bill,
            "Nominal": nominal
        }])
        
        # 2. Menyiapkan Sheet Dokumentasi
        df_dokumen = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d %b %Y"),
            "Kegiatan & Keterangan (Link dengan sheet utama rekapan all)": deskripsi,
            "Nama File Foto": foto.name,
            "Timestamp Upload": waktu_input
        }])
        
        # 3. Proses Konversi ke File Excel (.xlsx)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Menyimpan ke sheet sesuai kategori
            sheet_name_rekap = "Form Non Bill" if "Non Bill" in kategori else ("Meals" if "Meals" in kategori else "Form Gasoline")
            df_rekap.to_excel(writer, sheet_name=sheet_name_rekap, index=False)
            df_dokumen.to_excel(writer, sheet_name='Dok. Kegiatan', index=False)
        
        # Tombol Unduh untuk simulasi pengambilan data
        st.download_button(
            label="⬇️ Unduh File Excel (Format HO)",
            data=output.getvalue(),
            file_name=f"Expense_{nama}_{tanggal}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Gagal! Pastikan Tempat Pembelian, Keterangan, Nominal, dan Foto sudah terisi.")
