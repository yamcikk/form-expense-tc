import streamlit as st
import pandas as pd
from datetime import datetime
import io
import json
import os

# Konfigurasi Halaman (Tampilan Mobile)
st.set_page_config(page_title="Form Expense Area", page_icon="📋", layout="centered")

# File lokal untuk memori permanen gasoline
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

if 'km_history_per_code' not in st.session_state:
    st.session_state['km_history_per_code'] = load_memory()

if 'list_transaksi' not in st.session_state:
    st.session_state['list_transaksi'] = []

# INISIALISASI SESSION STATE UNTUK DOWNLOAD DATA AGAR TIDAK KEYERROR
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

# VARIABEL KHUSUS GASOLINE
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

    km_sebelumnya = st.number_input("KM Sebelumnya", value=int(suggested_km), step=1)
    km_sekarang = st.number_input("KM Sekarang", min_value=0, step=1)

# VARIABEL KHUSUS MEALS
jenis_meal = ""
tempat_makan = ""
alamat_makan = ""
daftar_pic_meals = []

if kategori_gl == "Meals":
    st.info("🍽️ Form Rincian Meals Terdeteksi")
    jenis_meal = st.selectbox("Jenis Meal", ["BF (Breakfast)", "LC (Lunch)", "CB (Coffee Break)", "DN (Dinner)"])
    tempat_makan = st.text_input("Tempat Makan (Restoran/Warung)")
    alamat_makan = st.text_input("Alamat Tempat Makan")
    
    st.markdown("**Daftar PIC / Orang yang Ikut Makan:**")
    if 'jumlah_pic_meals' not in st.session_state:
        st.session_state['jumlah_pic_meals'] = 1
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Tambah Orang"):
            st.session_state['jumlah_pic_meals'] += 1
    with col_btn2:
        if st.session_state['jumlah_pic_meals'] > 1 and st.button("➖ Kurangi Orang"):
            st.session_state['jumlah_pic_meals'] -= 1
            
    for i in range(st.session_state['jumlah_pic_meals']):
        st.markdown(f"*PIC ke-{i+1}*")
        p_nama = st.text_input(f"Nama PIC {i+1}", value=pilihan_nama if i == 0 else "", key=f"pic_nama_{i}")
        p_jbt = st.text_input(f"Jabatan {i+1}", value=data_terpilih["jabatan"] if i == 0 else "", key=f"pic_jbt_{i}")
        p_perusahaan = st.text_input(f"Perusahaan {i+1}", value="PT DGW FIT", key=f"pic_perusahaan_{i}")
        if p_nama:
            daftar_pic_meals.append({
                "nama": p_nama,
                "jabatan": p_jbt,
                "perusahaan": p_perusahaan
            })

deskripsi = st.text_area("Description (Keterangan Kegiatan)")
nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)

st.markdown("---")
st.markdown("### 3. Status Dokumen (Bill / Non-Bill)")
status_nota = st.radio("Pilih Jenis Nota", ["Ada Nota / Bill Resmi", "Non Bill"])

tempat_nb = ""
alamat_nb = ""
nama_pic_nb = pilihan_nama if pilihan_nama != "Pilih Nama..." else ""
posisi_pic_nb = data_terpilih["jabatan"] if pilihan_nama != "Pilih Nama..." else ""
perusahaan_nb = "PT DGW FIT"
alasan_non_bill = "Tidak ada nota Resmi"
pilihan_alasan = ""
note_alasan = ""

if status_nota == "Non Bill":
    st.info("📝 Masukkan Detail Alasan & Informasi Non-Bill")
    pilihan_alasan = st.selectbox(
        "Kategori Nota Non Bill",
        ["Non Bill - Gasoline", "Non Bill - Meals", "Non Bill Lainnya"]
    )
    tempat_nb = st.text_input("Tempat Pembelian")
    alamat_nb = st.text_input("Alamat Pembelian")
    nama_pic_nb = st.text_input("Nama PIC", value=pilihan_nama)
    posisi_pic_nb = st.text_input("Posisi PIC", value=data_terpilih["jabatan"])
    perusahaan_nb = st.text_input("Perusahaan", value="PT DGW FIT")
    note_alasan = st.text_area("Note Alasan Non Bill")
    alasan_non_bill = "Tidak ada nota Resmi"

st.markdown("---")
st.write("**Dokumentasi (Wajib Lampirkan Bukti Ber-Timestamp)**")
foto = st.camera_input("Ambil Foto Sekarang")

if st.button("➕ Tambahkan Transaksi ini ke Daftar Laporan"):
    if pilihan_nama != "Pilih Nama..." and deskripsi and nominal > 0 and foto:
        waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "Gasoline" in kategori_gl and km_sekarang > 0:
            if pilihan_nama not in st.session_state['km_history_per_code']:
                st.session_state['km_history_per_code'][pilihan_nama] = {}
            st.session_state['km_history_per_code'][pilihan_nama][pilihan_kode_g] = km_sekarang
            st.session_state['km_history_per_code'][pilihan_nama]["latest_km"] = km_sekarang
            save_memory(st.session_state['km_history_per_code'])

        final_deskripsi = format_teks_rapi(deskripsi)
        if kategori_gl == "Meals":
            pic_str = ", ".join([f"{p['nama']} ({p['jabatan']} - {p['perusahaan']})" for p in daftar_pic_meals])
            final_deskripsi = f"[{jenis_meal}] Tempat: {tempat_makan} ({alamat_makan}). PIC: {pic_str}. Keterangan: {final_deskripsi}"

        item_data = {
            "tanggal": tanggal,
            "tanggal_str": tanggal.strftime("%d/%m/%Y"),
            "kategori_gl": kategori_gl,
            "deskripsi": final_deskripsi,
            "nominal": nominal,
            "status_nota": status_nota,
            # Gasoline
            "kode_gasoline": pilihan_kode_g if "Gasoline" in kategori_gl else "",
            "liter": liter if "Gasoline" in kategori_gl else 0,
            "km_sebelumnya": km_sebelumnya if "Gasoline" in kategori_gl else 0,
            "km_sekarang": km_sekarang if "Gasoline" in kategori_gl else 0,
            # Meals
            "jenis_meal": jenis_meal.split(" ")[0] if kategori_gl == "Meals" else "",
            "tempat_makan": tempat_makan if kategori_gl == "Meals" else "",
            "alamat_makan": alamat_makan if kategori_gl == "Meals" else "",
            "daftar_pic_meals": daftar_pic_meals if kategori_gl == "Meals" else [],
            # Non Bill
            "tempat_nb": tempat_nb,
            "alamat_nb": alamat_nb,
            "nama_pic_nb": nama_pic_nb,
            "posisi_pic_nb": posisi_pic_nb,
            "perusahaan_nb": perusahaan_nb,
            "alasan_non_bill": alasan_non_bill,
            # Dokumen
            "foto_name": foto.name,
            "waktu_input": waktu_input
        }

        st.session_state['list_transaksi'].append(item_data)
        st.success(f"Transaksi '{kategori_gl}' berhasil ditambahkan ke daftar!")
    else:
        st.error("Gagal! Pilih Nama Karyawan, lengkapi Keterangan, Nominal, dan ambil foto bukti.")

if len(st.session_state['list_transaksi']) > 0:
    st.markdown("---")
    st.subheader(f"📋 Daftar Transaksi Sementara ({len(st.session_state['list_transaksi'])} Item)")
    df_sementara = pd.DataFrame([{
        "No": idx+1,
        "Tanggal": item["tanggal_str"],
        "Kategori": item["kategori_gl"],
        "Keterangan": item["deskripsi"],
        "Nominal (Rp)": f"{item['nominal']:,}"
    } for idx, item in enumerate(st.session_state['list_transaksi'])])
    st.table(df_sementara)

    col_rst1, col_rst2 = st.columns(2)
    with col_rst1:
        if st.button("🗑️ Reset / Hapus Semua Daftar"):
            st.session_state['list_transaksi'] = []
            st.rerun()
            
    with col_rst2:
        if st.button("🚀 Generate & Unduh Laporan Lengkap (5 Sheet)"):
            if pilihan_nama == "Pilih Nama...":
                st.error("Pilih Nama Karyawan terlebih dahulu di bagian atas!")
            else:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    workbook = writer.book
                    
                    sig_format_header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'middle', 'border': 1, 'bg_color': '#F2F2F2'})
                    sig_format_name = workbook.add_format({'bold': True, 'italic': True, 'font_color': 'red', 'align': 'center', 'valign': 'middle', 'border': 1})
                    sig_format_box = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'middle'})

                    def create_signature_block(ws):
                        sig_headers = ["Prepared By", "Verified By", "Approved By", "Approved By"]
                        sig_names = [pilihan_nama, "YAM CIK", "HARIS DWIJAYANTO", "EKO AGUS K"]
                        for col_i, header_text in enumerate(sig_headers):
                            c_idx = col_i + 5
                            ws.write(2, c_idx, header_text, sig_format_header)
                            ws.merge_range(3, c_idx, 4, c_idx, "", sig_format_box)
                            ws.write(5, c_idx, sig_names[col_i], sig_format_name)
                        if os.path.exists("ttd.png"):
                            try:
                                ws.insert_image(3, 5, "ttd.png", {'x_scale': 0.3, 'y_scale': 0.3})
                            except:
                                pass

                    def create_employee_header(ws, sub_title=""):
                        ws.write(0, 0, "PT. DGW FIT")
                        ws.write(1, 0, "SETTLEMENT REPORT EXPENSE - AST TCS TRAINING CENTER NASIONAL")
                        if sub_title:
                            ws.write(2, 0, sub_title)
                        
                        info_rows = [
                            ["Nama", pilihan_nama],
                            ["Jabatan", str(jabatan).upper()],
                            ["TC - Area", str(tc_area).upper()],
                            ["Periode", str(periode).upper()],
                            ["Budget Pettycash", str(budget_pettycash)],
                            ["No Phone", str(no_phone)],
                            ["Nama Bank", str(nama_bank).upper()],
                            ["No. Rekening", str(no_rekening)]
                        ]
                        start_row = 3 if sub_title else 2
                        for idx, row_val in enumerate(info_rows):
                            ws.write(start_row + idx, 0, row_val[0])
                            ws.write(start_row + idx, 1, row_val[1])

                    # --- 1. SHEET: Form Expense ---
                    sheet_main = "Form Expense"
                    ws_main = workbook.add_worksheet(sheet_main)
                    writer.sheets[sheet_main] = ws_main
                    create_employee_header(ws_main)
                    create_signature_block(ws_main)

                    rows_main = []
                    for item in st.session_state['list_transaksi']:
                        r = {
                            "Date": item["tanggal_str"],
                            "Description": item["deskripsi"],
                            "Code GL Biaya TC": "",
                            "Category 1": "",
                            "Biaya TC": item["nominal"] if "Biaya TC" in item["kategori_gl"] else "",
                            "Parking/Toll": item["nominal"] if "Parking" in item["kategori_gl"] else "",
                            "Gasoline (Konversi jika Pertamax)": item["nominal"] if "Gasoline" in item["kategori_gl"] else "",
                            "Vehicle Maintenance": item["nominal"] if "Vehicle" in item["kategori_gl"] else "",
                            "Stationery": item["nominal"] if "Stationery" in item["kategori_gl"] else "",
                            "Postage": item["nominal"] if "Postage" in item["kategori_gl"] else "",
                            "Transport": item["nominal"] if "Transport" in item["kategori_gl"] else "",
                            "Meals": item["nominal"] if item["kategori_gl"] == "Meals" else "",
                            "Hotel (Jika perdin dan ada laundry, masukan pada post ini)": item["nominal"] if "Hotel" in item["kategori_gl"] else "",
                            "Others": item["nominal"] if "Others" in item["kategori_gl"] else "",
                            "TOTAL": item["nominal"],
                            "Non Bill/Gasoline (G) - GNB (Gasoline Non Bill)/Meals (Wajib Diisi)": item["kode_gasoline"] if "Gasoline" in item["kategori_gl"] else (item["jenis_meal"] if item["kategori_gl"] == "Meals" else item["alasan_non_bill"]),
                            "Liter": item["liter"] if "Gasoline" in item["kategori_gl"] and item["liter"] > 0 else "",
                            "KM Sebelumnya": item["km_sebelumnya"] if "Gasoline" in item["kategori_gl"] and item["km_sebelumnya"] > 0 else "",
                            "KM Sekarang": item["km_sekarang"] if "Gasoline" in item["kategori_gl"] and item["km_sekarang"] > 0 else ""
                        }
                        rows_main.append(r)
                    
                    df_main = pd.DataFrame(rows_main)
                    start_row_m = 13
                    df_main.to_excel(writer, sheet_name=sheet_main, index=False, startrow=start_row_m)
                    ws_main.add_table(start_row_m, 0, start_row_m + len(df_main), len(df_main.columns) - 1, {'style': 'Table Style Medium 9', 'name': 'MainExpenseTbl'})

                    # --- 2. SHEET: Form Gasoline ---
                    gasoline_items = [item for item in st.session_state['list_transaksi'] if "Gasoline" in item["kategori_gl"]]
                    sheet_gas = "Form Gasoline"
                    ws_gas = workbook.add_worksheet(sheet_gas)
                    writer.sheets[sheet_gas] = ws_gas
                    create_employee_header(ws_gas, "Rekapan Penggunaan Bensin")

                    rows_gas = []
                    for g in gasoline_items:
                        rows_gas.append({
                            "Date": g["tanggal_str"],
                            "Description": g["deskripsi"],
                            "KM Sebelumnya": g["km_sebelumnya"],
                            "KM Sekarang": g["km_sekarang"],
                            "Liter": g["liter"],
                            "Total Nominal": g["nominal"],
                            "Ratio KM/Liter": round((g["km_sekarang"] - g["km_sebelumnya"]) / g["liter"], 2) if g["liter"] > 0 else 0
                        })
                    df_gas = pd.DataFrame(rows_gas) if rows_gas else pd.DataFrame(columns=["Date", "Description", "KM Sebelumnya", "KM Sekarang", "Liter", "Total Nominal", "Ratio KM/Liter"])
                    start_row_g = 13
                    df_gas.to_excel(writer, sheet_name=sheet_gas, index=False, startrow=start_row_g)
                    if len(rows_gas) > 0:
                        ws_gas.add_table(start_row_g, 0, start_row_g + len(df_gas), len(df_gas.columns) - 1, {'style': 'Table Style Medium 9', 'name': 'GasTbl'})

                    # --- 3. SHEET: Form Non Bill ---
                    nonbill_items = [item for item in st.session_state['list_transaksi'] if item["status_nota"] == "Non Bill"]
                    sheet_nb = "Form Non Bill"
                    ws_nb = workbook.add_worksheet(sheet_nb)
                    writer.sheets[sheet_nb] = ws_nb
                    create_employee_header(ws_nb, "Form Non Bill")
                    create_signature_block(ws_nb)

                    rows_nb = []
                    for nb in nonbill_items:
                        rows_nb.append({
                            "Date": nb["tanggal_str"],
                            "Tempat Pembelian": nb["tempat_nb"],
                            "Alamat Pembelian": nb["alamat_nb"],
                            "Nama PIC": nb["nama_pic_nb"],
                            "Posisi": nb["posisi_pic_nb"],
                            "Perusahaan": nb["perusahaan_nb"],
                            "Description": nb["deskripsi"],
                            "Alasan Non Bill": nb["alasan_non_bill"],
                            "Nominal": nb["nominal"]
                        })
                    df_nb = pd.DataFrame(rows_nb) if rows_nb else pd.DataFrame(columns=["Date", "Tempat Pembelian", "Alamat Pembelian", "Nama PIC", "Posisi", "Perusahaan", "Description", "Alasan Non Bill", "Nominal"])
                    start_row_nb = 13
                    df_nb.to_excel(writer, sheet_name=sheet_nb, index=False, startrow=start_row_nb)
                    if len(rows_nb) > 0:
                        ws_nb.add_table(start_row_nb, 0, start_row_nb + len(df_nb), len(df_nb.columns) - 1, {'style': 'Table Style Medium 9', 'name': 'NonBillTbl'})

                    # --- 4. SHEET: Form Meals ---
                    meals_items = [item for item in st.session_state['list_transaksi'] if item["kategori_gl"] == "Meals"]
                    sheet_meals = "Form Meals"
                    ws_meals = workbook.add_worksheet(sheet_meals)
                    writer.sheets[sheet_meals] = ws_meals
                    create_employee_header(ws_meals, "Form Meals")

                    rows_meals = []
                    for m in meals_items:
                        rows_meals.append({
                            "Date": m["tanggal_str"],
                            "Jenis Meals BF/LC/CB/DN": m["jenis_meal"],
                            "Tempat Pembelian": m["tempat_makan"],
                            "Alamat Pembelian": m["alamat_makan"],
                            "Nama PIC": ", ".join([p['nama'] for p in m["daftar_pic_meals"]]),
                            "Posisi": ", ".join([p['jabatan'] for p in m["daftar_pic_meals"]]),
                            "Perusahaan": ", ".join([p['perusahaan'] for p in m["daftar_pic_meals"]]),
                            "Description": m["deskripsi"],
                            "Total Nominal": m["nominal"]
                        })
                    df_meals = pd.DataFrame(rows_meals) if rows_meals else pd.DataFrame(columns=["Date", "Jenis Meals BF/LC/CB/DN", "Tempat Pembelian", "Alamat Pembelian", "Nama PIC", "Posisi", "Perusahaan", "Description", "Total Nominal"])
                    start_row_meals = 13
                    df_meals.to_excel(writer, sheet_name=sheet_meals, index=False, startrow=start_row_meals)
                    if len(rows_meals) > 0:
                        ws_meals.add_table(start_row_meals, 0, start_row_meals + len(df_meals), len(df_meals.columns) - 1, {'style': 'Table Style Medium 9', 'name': 'MealsTbl'})

                    # --- 5. SHEET: Dok. Kegiatan ---
                    sheet_doc = "Dok. Kegiatan"
                    ws_doc = workbook.add_worksheet(sheet_doc)
                    writer.sheets[sheet_doc] = ws_doc

                    rows_doc = []
                    for item in st.session_state['list_transaksi']:
                        rows_doc.append({
                            "Tanggal": item["tanggal_str"],
                            "Kegiatan & Keterangan": item["deskripsi"],
                            "Nama File Foto": item["foto_name"],
                            "Timestamp Upload": item["waktu_input"]
                        })
                    df_dokumen = pd.DataFrame(rows_doc) if rows_doc else pd.DataFrame(columns=["Tanggal", "Kegiatan & Keterangan", "Nama File Foto", "Timestamp Upload"])
                    df_dokumen.to_excel(writer, sheet_name=sheet_doc, index=False)
                    if len(rows_doc) > 0:
                        ws_doc.add_table(0, 0, len(df_dokumen), len(df_dokumen.columns) - 1, {'style': 'Table Style Medium 9', 'name': 'DocTbl'})

                st.session_state['download_data'] = output.getvalue()
                st.session_state['file_name_download'] = f"Expense_Lengkap_{pilihan_nama}.xlsx"
                st.success("Laporan lengkap 5 Sheet berhasil dibuat!")

if st.session_state['download_data'] is not None:
    st.download_button(
        label="⬇️ Unduh File Excel Lengkap (5 Sheet - Sesuai HO)",
        data=st.session_state['download_data'],
        file_name=st.session_state['file_name_download'],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
