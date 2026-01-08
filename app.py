import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Planner Revan 2026", layout="wide")

st.title("📊 Financial Planner Revan 2026")
st.write("Aplikasi untuk simulasi budget, wishlist, dan tabungan akhir tahun.")

# --- LIST BULAN (dipakai untuk dropdown + loop) ---
months = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
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

# --- WISHLIST (toggle + harga + bulan) ---
st.sidebar.header("Wishlist (Pilih item, harga, dan bulan pembelian)")

with st.sidebar.expander("Atur Wishlist", expanded=True):
    st.caption("Centang item yang ingin dibeli, atur harga, lalu pilih bulan pembelian.")

    # Item 1
    st.markdown("**Samsung Tab S10 FE**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        buy_tab = st.checkbox("Beli Tab", value=True, key="buy_tab")
    with col2:
        tab_price = st.number_input("Harga", value=6000000, step=100000, key="tab_price")
    with col3:
        tab_month = st.selectbox("Bulan beli", months, index=2, key="tab_month")  # default Maret

    st.divider()

    # Item 2
    st.markdown("**Motorola Edge 60 Fusion**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        buy_hp = st.checkbox("Beli HP", value=True, key="buy_hp")
    with col2:
        hp_price = st.number_input("Harga", value=4300000, step=100000, key="hp_price")
    with col3:
        hp_month = st.selectbox("Bulan beli", months, index=3, key="hp_month")  # default April

    st.divider()

    # Item 3
    st.markdown("**Trip Jogja**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        go_jogja = st.checkbox("Jalan Jogja", value=False, key="go_jogja")
    with col2:
        jogja_price = st.number_input("Budget", value=2000000, step=100000, key="jogja_price")
    with col3:
        jogja_month = st.selectbox("Bulan pergi", months, index=4, key="jogja_month")  # default Mei

    st.divider()

    # Item 4
    st.markdown("**Trip Malang**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        go_malang = st.checkbox("Jalan Malang", value=False, key="go_malang")
    with col2:
        malang_price = st.number_input("Budget", value=2500000, step=100000, key="malang_price")
    with col3:
        malang_month = st.selectbox("Bulan pergi", months, index=5, key="malang_month")  # default Juni

# --- mapping wishlist ke bulan (biar gampang dihitung saat loop) ---
wishlist_plan = [
    {"name": "Tab", "enabled": buy_tab, "price": tab_price, "month": tab_month},
    {"name": "HP", "enabled": buy_hp, "price": hp_price, "month": hp_month},
    {"name": "Jogja", "enabled": go_jogja, "price": jogja_price, "month": jogja_month},
    {"name": "Malang", "enabled": go_malang, "price": malang_price, "month": malang_month},
]

# --- LOGIKA PERHITUNGAN ---
data = []
current_balance = initial_balance

for month in months:
    income = monthly_salary

    # THR di bulan Maret
    if month == "Maret":
        income += thr_amount

    # Pengeluaran rutin (Januari lebih hemat)
    exp_rutin = total_rutin
    if month == "Januari":
        exp_rutin = 2840000

    # Pengeluaran wishlist mengikuti bulan yang dipilih
    wishlist_cost = sum(
        item["price"]
        for item in wishlist_plan
        if item["enabled"] and item["month"] == month
    )

    total_exp = exp_rutin + wishlist_cost

    balance_before = current_balance
    current_balance = current_balance + income - total_exp

    data.append({
        "Bulan": month,
        "Saldo Awal": balance_before,
        "Pemasukan": income,
        "Pengeluaran": total_exp,
        "Saldo Akhir": current_balance
    })

df = pd.DataFrame(data)

# --- DISPLAY ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Proyeksi Saldo Bulanan")
    # PERBAIKAN: Menghapus use_container_width=True (default plotly biasanya sudah responsif)
    # Jika masih error, bisa coba tambahkan width="stretch" jika library mendukung
    fig = px.line(df, x="Bulan", y="Saldo Akhir", markers=True, title="Trend Tabungan Revan 2026")
    st.plotly_chart(fig) 

with col2:
    st.subheader("Summary")
    final_savings = df["Saldo Akhir"].iloc[-1]
    st.metric(label="Total Sisa Uang (Saldo Akhir) Des 2026", value=f"Rp {final_savings:,.0f}")

    if final_savings > 0:
        survival_months = final_savings / total_rutin
        st.caption(f"Cukup untuk hidup **{survival_months:.1f} bulan** tanpa kerja.")
    else:
        st.error("Warning: Saldo akhir minus!")

st.subheader("📋 Tabel Detail Keuangan")

def color_negative_red(val):
    return "color: red" if val < 0 else "color: green"

# PERBAIKAN: Mengganti use_container_width=True menjadi width="stretch"
st.dataframe(
    df.style.format({
        "Saldo Awal": "Rp {:,.0f}",
        "Pemasukan": "Rp {:,.0f}",
        "Pengeluaran": "Rp {:,.0f}",
        "Saldo Akhir": "Rp {:,.0f}"
    }).applymap(color_negative_red, subset=["Saldo Akhir"]),
    width="stretch"
)