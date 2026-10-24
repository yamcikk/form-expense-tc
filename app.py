import streamlit as st
import pandas as pd
from datetime import datetime
import io
import json
import os

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

# File lokal untuk menyimpan memori permanen agar tidak hilang saat refresh/ganti hari
DB_FILE = "gasoline_memory.json"

def load_memory():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Muat memori ke session state
if 'km_history_per_code' not in st.session_state:
    st.session_state['km_history_per_code'] = load_memory()

if 'download_data' not in st.session_state:
    st.session_state['download_data'] = None
if 'file_name_download' not in st.session_state:
    st.session_state['file_name_download'] = ""

# Menampilkan Logo jika ada
try:
    st.image("logo.png", width=150)
except:
    pass

st.title("PT. DGW FIT")
st.subheader("Settlement Report Expense - AST TCS Training Center Nasional")

# Fungsi untuk merapikan teks
def format_teks_rapi(teks):
    if not teks:
        return ""
    kalimat_list = teks.split('. ')
    kalimat_rapi = [k.strip().capitalize() for k in kalimat_list if k.strip()]
    return '. '.join(kalimat_rapi) + ('.' if teks.endswith('.') else '')

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

# KATEGORI UTAMA PENGELUARAN
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
        "Hotel (Jika perdin dan ada laundry, masukan pada post ini)",
        "Others"
    ]
)

# FORM KHUSUS GASOLINE
liter = 0.0
km_sebelumnya = 0
km_sekarang = 0
pilihan_kode_g = ""

if "Gasoline" in kategori_gl:
    st.info("⛽ Form Gasoline Terdeteksi")
    
    pilihan_kode_g = st.selectbox(
        "Pilih Nomor Gasoline",
        ["G", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]
    )
    
    liter = st.number_input("Jumlah Liter", min_value=0.0, step=0.1)
    
    mapping_prev_code = {
        "G1": "G", "G2": "G1", "G3": "G2", "G4": "G3", "G5": "G4",
        "G6": "G5", "G7": "G6", "G8": "G7", "G9": "G8", "G10": "G9"
    }
    
    suggested_km = 0
    if pilihan_nama != "Pilih Nama...":
        user_memory = st.session_state['km_history_per_code'].get(pilihan_nama, {})
        
        if pilihan_kode_g in mapping_prev_code:
            target_prev = mapping_prev_code[pilihan_kode_g]
            suggested_km = user_memory.get(target_prev, 0)
        elif pilihan_kode_g == "G":
            suggested_km = user_memory.get("latest_km", 0)

    km_sebelumnya = st.number_input(
        f"KM Sebelumnya (Otomatis menyambung dari pengisian sebelumnya)", 
        value=int(suggested_km), 
        step=1
    )
    km_sekarang = st.number_input("KM Sekarang", min_value=0, step=1)

deskripsi = st.text_area("Description (Keterangan Kegiatan)")
nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)

st.markdown("---")
st.markdown("### 3. Status Dokumen (Bill / Non-Bill)")
status_nota = st.radio("Pilih Jenis Nota", ["Ada Nota / Bill Resmi", "Non Bill"])

tempat = ""
alamat = ""
nama_pic = pilihan_nama if pilihan_nama != "Pilih Nama..." else ""
posisi_pic = data_terpilih["jabatan"] if pilihan_nama != "Pilih Nama..." else ""
perusahaan = "PT DGW FIT"
alasan_non_bill = ""

if status_nota == "Non Bill":
    st.info("📝 Masukkan Detail Alasan & Informasi Non-Bill")
    pilihan_alasan = st.selectbox(
        "Kategori Nota Non Bill",
        ["Non Bill - Gasoline", "Non Bill - Meals", "Non Bill Lainnya"]
    )
    tempat = st.text_input("Tempat Pembelian")
    alamat = st.text_input("Alamat Pembelian")
    nama_pic = st.text_input("Nama PIC (Bisa > 1 orang, pisahkan dengan koma)", value=pilihan_nama)
    posisi_pic = st.text_input("Posisi PIC", value=data_terpilih["jabatan"])
    perusahaan = st.text_input("Perusahaan", value="PT DGW FIT")
    note_alasan = st.text_area("Note Alasan Non Bill (Jelaskan mengapa nota tersebut non bill)")
    
    if note_alasan:
        alasan_non_bill = f"{pilihan_alasan} - {note_alasan}"
    else:
        alasan_non_bill = pilihan_alasan

st.markdown("---")
st.write("**Dokumentasi (Wajib Lampirkan Bukti Ber-Timestamp)**")
foto = st.camera_input("Ambil Foto Sekarang")

submitted = st.button("Submit Laporan")

if submitted:
    if pilihan_nama != "Pilih Nama..." and deskripsi and nominal > 0 and foto:
        waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simpan KM ke memori permanen JSON
        if "Gasoline" in kategori_gl and km_sekarang > 0 and pilihan_nama != "Pilih Nama...":
            if pilihan_nama not in st.session_state['km_history_per_code']:
                st.session_state['km_history_per_code'][pilihan_nama] = {}
            
            st.session_state['km_history_per_code'][pilihan_nama][pilihan_kode_g] = km_sekarang
            st.session_state['km_history_per_code'][pilihan_nama]["latest_km"] = km_sekarang
            
            # Simpan ke file fisik server
            save_memory(st.session_state['km_history_per_code'])

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
        
        final_deskripsi = format_teks_rapi(deskripsi)
        
        row_data = {
            "Date": tanggal.strftime("%d/%m/%Y"),
            "Non Bill/Gasoline (G) - GNB (Gasoline Non Bill)/Meals (Wajib Diisi)": pilihan_kode_g if "Gasoline" in kategori_gl else (alasan_non_bill if status_nota == "Non Bill" else ""),
            "Liter": liter if "Gasoline" in kategori_gl else "",
            "KM Sebelumnya": km_sebelumnya if "Gasoline" in kategori_gl else "",
            "KM Sekarang": km_sekarang if "Gasoline" in kategori_gl else "",
            "Description": final_deskripsi,
            "Code GL Biaya TC": "",
            "Category 1": "",
            "Biaya TC": nominal if "Biaya TC" in kategori_gl else "",
            "Parking/Toll": nominal if "Parking" in kategori_gl else "",
            "Gasoline (Konversi jika Pertamax)": nominal if "Gasoline" in kategori_gl else "",
            "Vehicle Maintenance": nominal if "Vehicle" in kategori_gl else "",
            "Stationery": nominal if "Stationery" in kategori_gl else "",
            "Postage": nominal if "Postage" in kategori_gl else "",
            "Transport": nominal if "Transport" in kategori_gl else "",
            "Meals": nominal if kategori_gl == "Meals" else "",
            "Hotel (Jika perdin dan ada laundry, masukan pada post ini)": nominal if "Hotel" in kategori_gl else "",
            "Others": nominal if "Others" in kategori_gl else "",
            "TOTAL": nominal
        }
        
        df_transaksi = pd.DataFrame([row_data])
        
        df_dokumen = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%d %b %Y"),
            "Kegiatan & Keterangan": format_teks_rapi(deskripsi),
            "Nama File Foto": foto.name,
            "Timestamp Upload": waktu_input
        }])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            sheet_name_rekap = "Form Expense"
            df_header.to_excel(writer, sheet_name=sheet_name_rekap, index=False, header=False)
            df_transaksi.to_excel(writer, sheet_name=sheet_name_rekap, index=False, startrow=len(header_info))
            df_dokumen.to_excel(writer, sheet_name='Dok. Kegiatan', index=False)
        
        st.session_state['download_data'] = output.getvalue()
        st.session_state['file_name_download'] = f"Expense_{pilihan_nama}.xlsx"
        
        st.success(f"Data pengeluaran Rp {nominal:,} berhasil dicatat pada {waktu_input}!")
    else:
        st.error("Gagal! Pilih Nama Karyawan, lengkapi Keterangan, Nominal, dan ambil foto bukti.")

if st.session_state['download_data'] is not None:
    st.download_button(
        label="⬇️ Unduh File Excel (Sesuai Format HO)",
        data=st.session_state['download_data'],
        file_name=st.session_state['file_name_download'],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
