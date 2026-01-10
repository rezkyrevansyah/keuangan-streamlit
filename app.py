import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# App Config
# =========================
st.set_page_config(page_title="Financial Planner Revan 2026", layout="wide")

st.title("📊 Financial Planner Revan 2026")
st.write("Aplikasi untuk simulasi budget, wishlist, dan tabungan akhir tahun.")

# --- KONSTANTA ---
MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# =========================
# Session State Init
# =========================
if "wishlist" not in st.session_state:
    st.session_state["wishlist"] = [
        {"name": "Samsung Tab S10 FE", "price": 6000000, "month": "Maret", "enabled": True},
        {"name": "Motorola Edge 60 Fusion", "price": 4300000, "month": "April", "enabled": True},
        {"name": "Trip Jogja", "price": 2000000, "month": "Mei", "enabled": False},
        {"name": "Trip Malang", "price": 2500000, "month": "Juni", "enabled": False},
    ]

# Pengeluaran rutin itemized (baru)
if "rutin_items" not in st.session_state:
    st.session_state["rutin_items"] = [
        {"desc": "Kirim ke Ibu", "amount": 2000000},
        {"desc": "Kebutuhan Pribadi", "amount": 1840000},
    ]

# =========================
# Sidebar - Basic Config
# =========================
st.sidebar.header("Konfigurasi Dasar")
initial_balance = st.sidebar.number_input("Saldo Awal (Jan)", value=6400000, step=100000)
monthly_salary = st.sidebar.number_input("Gaji Bulanan", value=5200000, step=100000)
thr_amount = st.sidebar.number_input("Nominal THR (Cair Maret)", value=1800000, step=100000)

# =========================
# Sidebar - Pengeluaran Rutin (itemized)
# =========================
st.sidebar.header("Pengeluaran Rutin (Bulanan)")
st.sidebar.caption("Tambah pengeluaran rutin: isi nominal & keterangan, lalu Enter atau klik tombol Add.")

with st.sidebar.form("form_add_rutin", clear_on_submit=True):
    new_amount = st.number_input("Nominal", min_value=0, value=0, step=50000)
    new_desc = st.text_input("Keterangan", placeholder="Contoh: Internet, Cicilan, Makan, dll")
    add = st.form_submit_button("➕ Add Pengeluaran")

    if add:
        if new_amount <= 0:
            st.sidebar.warning("Nominal harus > 0.")
        elif not new_desc.strip():
            st.sidebar.warning("Keterangan wajib diisi.")
        else:
            st.session_state["rutin_items"].append({"desc": new_desc.strip(), "amount": int(new_amount)})
            st.sidebar.success("Pengeluaran rutin ditambahkan.")
            st.rerun()

# List pengeluaran rutin + delete
st.sidebar.markdown("**Daftar Pengeluaran Rutin**")
if len(st.session_state["rutin_items"]) == 0:
    st.sidebar.info("Belum ada pengeluaran rutin.")
else:
    total_rutin_default = sum(x["amount"] for x in st.session_state["rutin_items"])
    st.sidebar.write(f"Total rutin (default/bulan): **Rp {total_rutin_default:,.0f}**".replace(",", "."))

    for idx, it in enumerate(st.session_state["rutin_items"]):
        c1, c2, c3 = st.sidebar.columns([1.4, 1, 0.6])
        with c1:
            st.write(it["desc"])
        with c2:
            st.write(f"Rp {it['amount']:,.0f}".replace(",", "."))
        with c3:
            if st.button("🗑️", key=f"del_rutin_{idx}", help="Hapus item ini"):
                st.session_state["rutin_items"].pop(idx)
                st.rerun()

# =========================
# Sidebar - Override Pengeluaran per Bulan (baru)
# =========================
st.sidebar.divider()
st.sidebar.header("Override Pengeluaran Rutin (Per Bulan)")
st.sidebar.caption("Pilih bulan yang ingin dioverride. Jika nominal = 0, override dianggap tidak aktif.")

override_month = st.sidebar.selectbox("Pilih Bulan Override", MONTHS, index=0)
override_amount = st.sidebar.number_input(
    "Nominal Override",
    min_value=0,
    value=0,          # <= sesuai request: default 0
    step=100000
)

# =========================
# Sidebar - Wishlist (CRUD + tombol mass action)
# =========================
st.sidebar.divider()
st.sidebar.header("Wishlist Management")
st.sidebar.caption("Anda bisa tambah, edit, hapus item. Ada juga tombol mass-action.")

wl_c1, wl_c2, wl_c3 = st.sidebar.columns(3)
with wl_c1:
    if st.sidebar.button("➕ Tambah"):
        st.session_state["wishlist"].append({
            "name": "Item Baru",
            "price": 1000000,
            "month": "Desember",
            "enabled": True
        })
        st.rerun()

with wl_c2:
    if st.sidebar.button("🧹 Hapus Semua"):
        st.session_state["wishlist"] = []
        st.rerun()

with wl_c3:
    if st.sidebar.button("⛔ Nonaktifkan Semua"):
        for i in range(len(st.session_state["wishlist"])):
            st.session_state["wishlist"][i]["enabled"] = False
        st.rerun()

st.sidebar.divider()

# Loop READ & UPDATE & DELETE wishlist
wishlist_items = st.session_state["wishlist"]
for i, item in enumerate(wishlist_items):
    with st.sidebar.expander(f"#{i+1} {item['name']}", expanded=item['enabled']):
        new_name = st.text_input("Nama Barang", value=item['name'], key=f"name_{i}")
        new_enabled = st.checkbox("Aktifkan?", value=item['enabled'], key=f"enable_{i}")
        new_price = st.number_input("Harga", value=int(item['price']), step=100000, key=f"price_{i}")

        try:
            month_index = MONTHS.index(item['month'])
        except ValueError:
            month_index = 0

        new_month = st.selectbox("Bulan Beli", MONTHS, index=month_index, key=f"month_{i}")

        # Update session state
        st.session_state["wishlist"][i]["name"] = new_name
        st.session_state["wishlist"][i]["enabled"] = new_enabled
        st.session_state["wishlist"][i]["price"] = int(new_price)
        st.session_state["wishlist"][i]["month"] = new_month

        if st.button("🗑️ Hapus Item", key=f"del_{i}"):
            st.session_state["wishlist"].pop(i)
            st.rerun()

# =========================
# Perhitungan
# =========================
data = []
current_balance = initial_balance

total_rutin_default = sum(x["amount"] for x in st.session_state["rutin_items"])

for month in MONTHS:
    income = monthly_salary
    if month == "Maret":
        income += thr_amount

    # Default pengeluaran rutin
    exp_rutin = total_rutin_default

    # Apply override jika bulan cocok dan nominal > 0
    if (month == override_month) and (override_amount > 0):
        exp_rutin = override_amount

    # Hitung total wishlist bulan ini
    wishlist_cost = 0
    for item in st.session_state["wishlist"]:
        if item.get("enabled") and item.get("month") == month:
            wishlist_cost += int(item.get("price", 0))

    total_exp = exp_rutin + wishlist_cost
    balance_before = current_balance
    current_balance = current_balance + income - total_exp

    data.append({
        "Bulan": month,
        "Saldo Awal": balance_before,
        "Pemasukan": income,
        "Rutin": exp_rutin,
        "Wishlist": wishlist_cost,
        "Total Pengeluaran": total_exp,
        "Saldo Akhir": current_balance
    })

df = pd.DataFrame(data)

# =========================
# Dashboard Summary Cards
# =========================
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
    val_color = "normal" if final_balance > 0 else "inverse"
    st.metric("Sisa Tabungan (Des)", f"Rp {final_balance:,.0f}".replace(",", "."), delta="Net Worth", delta_color=val_color)

st.divider()

# =========================
# Charts
# =========================
c1, c2 = st.columns([1.5, 1])

with c1:
    st.subheader("📊 Analisis Pengeluaran (Rutin vs Wishlist)")
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
    fig_line = px.line(
        df,
        x="Bulan",
        y="Saldo Akhir",
        markers=True,
        title="Pertumbuhan Aset",
        color_discrete_sequence=["#2ecc71"]
    )
    fig_line.update_traces(fill="tozeroy")
    st.plotly_chart(fig_line, use_container_width=True)

# =========================
# Table Detail
# =========================
st.subheader("📋 Tabel Detail Keuangan")

def color_negative_red(val):
    return "color: red" if val < 0 else "color: green"

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
