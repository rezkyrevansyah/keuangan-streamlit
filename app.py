import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Financial Planner Revan 2026", layout="wide")

st.title("📊 Financial Planner Revan 2026")
st.write("Aplikasi untuk simulasi budget, wishlist, dan tabungan akhir tahun.")

# --- KONSTANTA ---
MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# --- INISIALISASI DATA (SESSION STATE) ---
if "wishlist" not in st.session_state:
    st.session_state["wishlist"] = [
        {"name": "Samsung Tab S10 FE", "price": 6000000, "month": "Maret", "enabled": True},
        {"name": "Motorola Edge 60 Fusion", "price": 4300000, "month": "April", "enabled": True},
        {"name": "Trip Jogja", "price": 2000000, "month": "Mei", "enabled": False},
        {"name": "Trip Malang", "price": 2500000, "month": "Juni", "enabled": False},
    ]

# --- SIDEBAR INPUT ---
st.sidebar.header("Konfigurasi Dasar")
initial_balance = st.sidebar.number_input("Saldo Awal (Jan)", value=6400000, step=100000)
monthly_salary = st.sidebar.number_input("Gaji Bulanan", value=5200000, step=100000)
thr_amount = st.sidebar.number_input("Nominal THR (Cair Maret)", value=1800000, step=100000)

st.sidebar.header("Pengeluaran Rutin")
budget_ibu = st.sidebar.number_input("Kirim ke Ibu", value=2000000, step=100000)
budget_pribadi = st.sidebar.number_input("Kebutuhan Pribadi", value=1840000, step=100000)
total_rutin = budget_ibu + budget_pribadi

# --- SIDEBAR WISHLIST (CRUD SYSTEM) ---
st.sidebar.header("Wishlist Management")
st.sidebar.caption("Anda bisa tambah, edit, atau hapus item di bawah ini.")

# Tombol CREATE
if st.sidebar.button("➕ Tambah Item Baru"):
    st.session_state["wishlist"].append({
        "name": "Item Baru", 
        "price": 1000000, 
        "month": "Desember", 
        "enabled": True
    })
    st.rerun()

# Loop READ & UPDATE & DELETE
wishlist_items = st.session_state["wishlist"]
for i, item in enumerate(wishlist_items):
    with st.sidebar.expander(f"#{i+1} {item['name']}", expanded=item['enabled']):
        new_name = st.text_input("Nama Barang", value=item['name'], key=f"name_{i}")
        new_enabled = st.checkbox("Aktifkan?", value=item['enabled'], key=f"enable_{i}")
        new_price = st.number_input("Harga", value=item['price'], step=100000, key=f"price_{i}")
        
        try:
            month_index = MONTHS.index(item['month'])
        except ValueError:
            month_index = 0
            
        new_month = st.selectbox("Bulan Beli", MONTHS, index=month_index, key=f"month_{i}")
        
        # Update session state
        st.session_state["wishlist"][i]["name"] = new_name
        st.session_state["wishlist"][i]["enabled"] = new_enabled
        st.session_state["wishlist"][i]["price"] = new_price
        st.session_state["wishlist"][i]["month"] = new_month

        if st.button("🗑️ Hapus Item", key=f"del_{i}"):
            st.session_state["wishlist"].pop(i)
            st.rerun()

# --- LOGIKA PERHITUNGAN ---
data = []
current_balance = initial_balance

for month in MONTHS:
    income = monthly_salary
    if month == "Maret":
        income += thr_amount

    exp_rutin = total_rutin
    if month == "Januari":
        exp_rutin = 2840000

    # Hitung total wishlist bulan ini
    wishlist_cost = 0
    for item in st.session_state["wishlist"]:
        if item["enabled"] and item["month"] == month:
            wishlist_cost += item["price"]

    total_exp = exp_rutin + wishlist_cost
    balance_before = current_balance
    current_balance = current_balance + income - total_exp

    data.append({
        "Bulan": month,
        "Saldo Awal": balance_before,
        "Pemasukan": income,
        "Rutin": exp_rutin,            # Dipisah untuk chart
        "Wishlist": wishlist_cost,     # Dipisah untuk chart
        "Total Pengeluaran": total_exp,
        "Saldo Akhir": current_balance
    })

df = pd.DataFrame(data)

# --- DASHBOARD SUMMARY CARDS ---
st.markdown("### 📝 Ringkasan Tahun 2026")
col1, col2, col3, col4 = st.columns(4)

total_income_year = df["Pemasukan"].sum()
total_expense_year = df["Total Pengeluaran"].sum()
total_wishlist_year = df["Wishlist"].sum()
final_balance = df["Saldo Akhir"].iloc[-1]

with col1:
    st.metric("Total Pemasukan", f"Rp {total_income_year/1000000:,.1f} Jt", delta="Setahun")
with col2:
    st.metric("Total Pengeluaran", f"Rp {total_expense_year/1000000:,.1f} Jt", delta="-Flow", delta_color="inverse")
with col3:
    st.metric("Total Biaya Wishlist", f"Rp {total_wishlist_year/1000000:,.1f} Jt", delta="Lifestyle", delta_color="off")
with col4:
    # Logic warna saldo akhir
    val_color = "normal" if final_balance > 0 else "inverse"
    st.metric("Sisa Tabungan (Des)", f"Rp {final_balance:,.0f}", delta="Net Worth", delta_color=val_color)

st.divider()

# --- CHARTS SECTION ---
c1, c2 = st.columns([1.5, 1])

with c1:
    st.subheader("📊 Analisis Pengeluaran (Rutin vs Wishlist)")
    # Chart Stacked Bar untuk melihat komposisi pengeluaran
    fig_bar = px.bar(
        df, 
        x="Bulan", 
        y=["Rutin", "Wishlist"], 
        title="Komposisi Pengeluaran Bulanan",
        color_discrete_map={"Rutin": "#3498db", "Wishlist": "#e74c3c"},
        labels={"value": "Nominal (Rp)", "variable": "Jenis Pengeluaran"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("📈 Trend Saldo Tabungan")
    # Line chart saldo
    fig_line = px.line(
        df, 
        x="Bulan", 
        y="Saldo Akhir", 
        markers=True, 
        title="Pertumbuhan Aset",
        color_discrete_sequence=["#2ecc71"]
    )
    # Menambahkan area shading di bawah garis biar lebih cantik
    fig_line.update_traces(fill='tozeroy') 
    st.plotly_chart(fig_line, use_container_width=True)

# --- TABLE DETAIL ---
st.subheader("📋 Tabel Detail Keuangan")

def color_negative_red(val):
    return "color: red" if val < 0 else "color: green"

# Format tabel agar kolom Rutin dan Wishlist juga terlihat
st.dataframe(
    df.style.format({
        "Saldo Awal": "Rp {:,.0f}",
        "Pemasukan": "Rp {:,.0f}",
        "Rutin": "Rp {:,.0f}",
        "Wishlist": "Rp {:,.0f}",
        "Total Pengeluaran": "Rp {:,.0f}",
        "Saldo Akhir": "Rp {:,.0f}"
    }).map(color_negative_red, subset=["Saldo Akhir"]), 
    width="stretch"
)