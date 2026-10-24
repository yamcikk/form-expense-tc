import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

st.title("PT. DGW FIT")
st.subheader("Settlement Report Expense - AST TCS Training Center Nasional")

# DATABASE KARYAWAN (Header Atas)
DATA_KARYAWAN = {
    "Pilih Nama...": {
        "jabatan": "", "tc_area": "", "periode": "OKTOBER 2026", 
        "budget": "", "phone": "", "bank": "", "rekening": ""
    },
    "DIKA APRILYANTO": {
        "jabatan": "ASS.TCS", "tc_area": "TC MAGELANG- JAWA TENGAH", "periode": "OKTOBER 2026", 
        "budget": "2.500.000", "phone": "081119128778", "bank": "BCA", "rekening": "0312839855"
    },
    "AHMAD NABIEL Z": {
        "jabatan": "FA RND", "tc_area": "TC MAGELANG- JAWA TENGAH", "periode": "OKTOBER 2026", 
        "budget": "2.500.000", "phone": "081234567890", "bank": "MANDIRI", "rekening": "1234567890"
    }
}

# Membuat Form Input
with st.form("expense_form"):
    st.markdown("### 1. Informasi Karyawan & Area")
    pilihan_nama = st.selectbox("Nama Karyawan (Pembuat Laporan)", list(DATA_KARYAWAN.keys()))
    data_terpilih = DATA_KARYAWAN[pilihan_nama]
    
    jabatan = st.text_input("Jabatan", value=data_terpilih["jabatan"])
    tc_area = st.text_input("TC - Area", value=data_terpilih["tc_area"])
    periode = st.text_input("Periode", value=data_terpilih["periode"])
    budget_pettycash = st.text_input("Budget Pettycash", value=data_terpilih["budget"])
    no_phone = st.text_input("No Phone", value=data_terpilih["phone"])
    nama_bank = st.text_input("Nama Bank", value=data_terpilih["bank"])
    no_rekening = st.text_input("No. Rekening", value=data_terpilih["rekening"])
    
    st.markdown("---")
    st.markdown("### 2. Rincian Transaksi")
    
    tanggal = st.date_input("Date (Tanggal Pembelian)")
    
    # KATEGORI PENGELUARAN UTAMA
    kategori_gl = st.selectbox(
        "Pilih Jenis Pengeluaran",
        [
            "Biaya TC (Umum / Non-Spesifik)",
            "Parking/Toll",
            "Gasoline (Konversi jika Pertamax)",
            "Vehicle Maintenance",
            "Stationery",
            "Postage",
            "Transport",
            "Meals",
            "Hotel (Jika perdin dan ada laundry)",
            "Others"
        ]
    )
    
    # VARIABEL DEFAULT
    jenis_meals = ""
    nama_pic = pilihan_nama if pilihan_nama != "Pilih Nama..." else ""
    posisi_pic = data_terpilih["jabatan"] if pilihan_nama != "Pilih Nama..." else ""
    perusahaan = "PT DGW FIT"
    
    # FORM KHUSUS HANYA MUNCUL JIKA MEMILIH "Meals"
    if kategori_gl == "Meals":
        st.info("🍽️ Masukkan Detail Rincian Meals")
        jenis_meals = st.selectbox("Jenis Meals", ["BF (Breakfast)", "LC (Lunch)", "CB (Coffeebreak)", "DN (Dinner)"])
        nama_pic = st.text_input("Nama PIC yang Ikut Makan (Bisa > 1 orang, pisahkan dengan koma)", value=pilihan_nama)
        posisi_pic = st.text_input("Posisi PIC (Urutkan sesuai nama PIC)", value=data_terpilih["jabatan"])
        perusahaan = st.text_input("Perusahaan", value="PT DGW FIT")
    
    tempat = st.text_input("Tempat Pembelian")
    alamat = st.text_input("Alamat Pembelian")
    
    # Jika bukan meals, tetap sediakan input PIC standar
    if kategori_gl != "Meals":
        nama_pic = st.text_input("Nama PIC", value=pilihan_nama if pilihan_nama != "Pilih Nama..." else "")
        posisi_pic = st.text_input("Posisi PIC", value=data_terpilih["jabatan"])
        perusahaan = st.text_input("Perusahaan", value="PT DGW FIT")

    deskripsi = st.text_area("Description (Keterangan Kegiatan)")
    
    alasan_non_bill = st.selectbox(
        "Alasan Non Bill",
        ["Non Bill - Gasoline", "Non Bill - Meals", "Non Bill"]
    )
    
    # Form khusus jika memilih Gasoline
    liter = 0.0
    km_sebelumnya = 0
    km_sekarang = 0
    if "Gasoline" in kategori_gl:
        st.info("⛽ Masukkan Data Liter & Kilometer Kendaraan")
        liter = st.number_input("Jumlah Liter", min_value=0.0, step=0.1)
        km_sebelumnya = st.number_input("KM Sebelumnya", min_value=0, step=1)
        km_sekarang = st.number_input("KM Sekarang", min_value=0, step=1)

    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    st.markdown("---")
    st.write("**Dokumentasi (Wajib Lampirkan Bukti Ber-Timestamp)**")
    foto = st.camera_input("Ambil Foto Sekarang")

    submitted = st.form_submit_button("Submit Laporan")

# Logika setelah tombol Submit ditekan
if submitted:
    if pilihan_nama != "Pilih Nama..." and tempat and deskripsi and nominal > 0 and foto:
        waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Data pengeluaran Rp {nominal:,} berhasil dicatat pada {waktu_input}!")
        
        # Header Info Excel
        header_info = [
            ["PT. DGW FIT", ""],
            ["SETTLEMENT REPORT EXPENSE - AST TCS TRAINING CENTER NASIONAL", ""],
            ["Nama", pilihan_nama],
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
        
        # Susunan baris data berdasarkan kategori
        if kategori_gl == "Meals":
            kode_jenis_meals = jenis_meals.split(" ")[0] # Mengambil kode BF/LC/CB/DN
            row_data = {
                "Date": tanggal.strftime("%d/%m/%Y"),
                "Jenis Meals": kode_jenis_meals,
                "Tempat Pembelian": str(tempat).upper(),
                "Alamat Pembelian": str(alamat).upper(),
                "Nama PIC": str(nama_pic).upper(),
                "Posisi": str(posisi_pic).upper(),
                "Perusahaan": str(perusahaan).upper(),
                "Description": str(deskripsi).upper(),
                "Total Nominal": nominal
            }
        else:
            row_data = {
                "Date": tanggal.strftime("%d/%m/%Y"),
                "Description": str(deskripsi).upper(),
                "Code GL Biaya TC": "",
                "Category 1": "",
                "Biaya TC": nominal if "Biaya TC" in kategori_gl else "",
                "Parking/Toll": nominal if "Parking" in kategori_gl else "",
                "Gasoline (Konversi jika Pertamax)": nominal if "Gasoline" in kategori_gl else "",
                "Vehicle Maintenance": nominal if "Vehicle" in kategori_gl else "",
                "Stationery": nominal if "Stationery" in kategori_gl else "",
                "Postage": nominal if "Postage" in kategori_gl else "",
                "Transport": nominal if "Transport" in kategori_gl else "",
                "Meals": "",
                "Hotel (Jika perdin dan ada laundry, masukan pada post ini)": nominal if "Hotel" in kategori_gl else "",
                "Others": nominal if "Others" in kategori_gl else "",
                "TOTAL": nominal
            }
        
        df_transaksi = pd.DataFrame([row_data])
        
        df_dokumen = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d %b %Y"),
            "Kegiatan & Keterangan": str(deskripsi).upper(),
            "Nama File Foto": foto.name,
            "Timestamp Upload": waktu_input
        }])
        
        # Konversi ke File Excel (.xlsx)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            sheet_name_rekap = "Form Meals" if kategori_gl == "Meals" else "Form Expense"
            
            df_header.to_excel(writer, sheet_name=sheet_name_rekap, index=False, header=False)
            df_transaksi.to_excel(writer, sheet_name=sheet_name_rekap, index=False, startrow=len(header_info))
            df_dokumen.to_excel(writer, sheet_name='Dok. Kegiatan', index=False)
        
        st.download_button(
            label="⬇️ Unduh File Excel (Sesuai Format HO)",
            data=output.getvalue(),
            file_name=f"Expense_{pilihan_nama}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Gagal! Pilih Nama Karyawan terlebih dahulu serta lengkapi Tempat, Keterangan, Nominal, dan Foto.")
