import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

st.title("PT. DGW FIT")
st.subheader("Settlement Report Expense - AST TCS Training Center Nasional")

# Membuat Form Input
with st.form("expense_form"):
    st.markdown("### Informasi Karyawan & Area")
    nama = st.text_input("Nama (Akan otomatis jadi kapital)")
    jabatan = st.text_input("Jabatan (Akan otomatis jadi kapital)")
    tc_area = st.text_input("TC - Area (Akan otomatis jadi kapital)")
    periode = st.text_input("Periode (Akan otomatis jadi kapital)")
    budget_pettycash = st.text_input("Budget Pettycash")
    no_phone = st.text_input("No Phone")
    nama_bank = st.text_input("Nama Bank (Akan otomatis jadi kapital)")
    no_rekening = st.text_input("No. Rekening")
    
    st.markdown("---")
    st.markdown("### Rincian Transaksi")
    
    # Input Data Transaksi
    tanggal = st.date_input("Date (Tanggal Pembelian)")
    tempat = st.text_input("Tempat Pembelian")
    alamat = st.text_input("Alamat Pembelian")
    nama_pic = st.text_input("Nama PIC")
    posisi_pic = st.text_input("Posisi PIC")
    perusahaan = st.text_input("Perusahaan", value="PT.FIT")
    
    # Kategori Pengeluaran
    kategori = st.selectbox(
        "Kategori Pengeluaran",
        ["Non Bill / Gasoline (G) - GNB", "Meals (M) - MB", "Gasoline (G)"]
    )
    
    deskripsi = st.text_area("Description (Keterangan Kegiatan)")
    
    # Pilihan Dropdown untuk Alasan Non Bill
    alasan_non_bill = st.selectbox(
        "Alasan Non Bill",
        ["Non Bill - Gasoline", "Non Bill - Meals", "Non Bill"]
    )
    
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
        
        # Header Info (Otomatis Kapital)
        header_info = [
            ["PT. DGW FIT", ""],
            ["SETTLEMENT REPORT EXPENSE - AST TCS TRAINING CENTER NASIONAL", ""],
            ["Nama", str(nama).upper()],
            ["Jabatan", str(jabatan).upper()],
            ["TC - Area", str(tc_area).upper()],
            ["Periode", str(periode).upper()],
            ["Budget Pettycash", str(budget_pettycash)],
            ["No Phone", str(no_phone)],
            ["Nama Bank", str(nama_bank).upper()],
            ["No. Rekening", str(no_rekening)],
            ["", ""]
        ]
        df_header = pd.DataFrame(header_info)
        
        # Tabel Transaksi (Otomatis Kapital)
        df_transaksi = pd.DataFrame([{
            "Date": tanggal.strftime("%d/%m/%Y"),
            "Tempat Pembelian": str(tempat).upper(),
            "Alamat Pembelian": str(alamat).upper(),
            "Nama PIC": str(nama_pic).upper(),
            "Posisi": str(posisi_pic).upper(),
            "Perusahaan": str(perusahaan).upper(),
            "Description": str(deskripsi).upper(),
            "Alasan Non Bill": str(alasan_non_bill).upper(),
            "Nominal": nominal
        }])
        
        # Sheet Dokumentasi
        df_dokumen = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d %b %Y"),
            "Kegiatan & Keterangan": str(deskripsi).upper(),
            "Nama File Foto": foto.name,
            "Timestamp Upload": waktu_input
        }])
        
        # Proses Konversi ke File Excel (.xlsx)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            sheet_name_rekap = "Form Non Bill" if "Non Bill" in kategori else ("Meals" if "Meals" in kategori else "Form Gasoline")
            
            df_header.to_excel(writer, sheet_name=sheet_name_rekap, index=False, header=False)
            df_transaksi.to_excel(writer, sheet_name=sheet_name_rekap, index=False, startrow=len(header_info))
            df_dokumen.to_excel(writer, sheet_name='Dok. Kegiatan', index=False)
        
        # Tombol Unduh
        st.download_button(
            label="⬇️ Unduh File Excel (Format Lengkap)",
            data=output.getvalue(),
            file_name=f"Expense_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Gagal! Pastikan Tempat Pembelian, Keterangan, Nominal, dan Foto sudah terisi.")
