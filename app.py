import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# App Config & Styling
# =========================
st.set_page_config(
    page_title="Financial Planner Revan 2026",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 700;
        font-size: 1.8rem;
    }

    /* Headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0f172a;
        border-radius: 8px 8px 0 0;
        border: 1px solid transparent;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b;
        color: #38bdf8;
        border-color: #334155;
        border-bottom-color: #1e293b;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Constants & Init
# =========================
MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

if "wishlist" not in st.session_state:
    st.session_state["wishlist"] = [
        {"name": "Samsung Tab S10 FE", "price": 6000000, "month": "Maret", "enabled": True},
        {"name": "Motorola Edge 60 Fusion", "price": 4300000, "month": "April", "enabled": True},
        {"name": "Trip Jogja", "price": 2000000, "month": "Mei", "enabled": False},
        {"name": "Trip Malang", "price": 2500000, "month": "Juni", "enabled": False},
    ]

if "rutin_items" not in st.session_state:
    st.session_state["rutin_items"] = [
        {"desc": "Kirim ke Ibu", "amount": 2000000, "active": True},
        {"desc": "Kebutuhan Pribadi", "amount": 1840000, "active": True},
    ]

# =========================
# Sidebar Controls
# =========================
with st.sidebar:
    st.title("⚙️ Konfigurasi")
    
    with st.expander("💰 Pemasukan", expanded=True):
        initial_balance = st.number_input("Saldo Awal (Jan)", value=6400000, step=100000, format="%d")
        monthly_salary = st.number_input("Gaji Bulanan", value=5200000, step=100000, format="%d")
        thr_amount = st.number_input("THR (Maret)", value=1800000, step=100000, format="%d")

    st.divider()
    
    with st.expander("🗓️ Override Bulanan"):
        st.write("Override total pengeluaran rutin untuk bulan tertentu.")
        override_month = st.selectbox("Bulan", MONTHS, index=0)
        override_amount = st.number_input("Nominal (0 = Off)", value=0, step=100000)

# =========================
# Data Management (Logic)
# =========================

# 1. Processing Dataframes for Editors
df_rutin = pd.DataFrame(st.session_state["rutin_items"])
df_wishlist = pd.DataFrame(st.session_state["wishlist"])

# =========================
# Main Layout
# =========================
st.title("💎 Financial Dashboard Revan 2026")
st.markdown("---")

# =========================
# Manage Data Section
# =========================
st.subheader("📝 Kelola Data")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 🔁 Pengeluaran Rutin")
    st.info("Edit langsung di tabel. Centang 'active' untuk mengaktifkan.")
    edited_rutin = st.data_editor(
        df_rutin,
        num_rows="dynamic",
        column_config={
            "desc": "Keterangan",
            "amount": st.column_config.NumberColumn("Nominal (Rp)", format="Rp %d"),
            "active": st.column_config.CheckboxColumn("Aktif?", default=True)
        },
        key="editor_rutin",
        width="stretch"
    )
    
with c2:
    st.markdown("#### 🎁 Wishlist & Goal")
    st.info("Rencanakan keinginanmu di sini.")
    edited_wishlist = st.data_editor(
        df_wishlist,
        num_rows="dynamic",
        column_config={
            "name": "Nama Barang",
            "price": st.column_config.NumberColumn("Harga (Rp)", format="Rp %d"),
            "month": st.column_config.SelectboxColumn("Bulan Rencana", options=MONTHS),
            "enabled": st.column_config.CheckboxColumn("Beli?", default=True)
        },
        key="editor_wishlist",
        width="stretch"
    )

# Sync back to session state
if not edited_rutin.equals(df_rutin):
    st.session_state["rutin_items"] = edited_rutin.to_dict("records")
    st.rerun()
    
if not edited_wishlist.equals(df_wishlist):
    st.session_state["wishlist"] = edited_wishlist.to_dict("records")
    st.rerun()

# =========================
# Calculations
# =========================
# Recalculate based on currently edited data
rutin_list = edited_rutin.to_dict("records")
wishlist_list = edited_wishlist.to_dict("records")

total_rutin_default = sum(x["amount"] for x in rutin_list if x.get("active", True))

data = []
current_balance = initial_balance

for month in MONTHS:
    income = monthly_salary
    if month == "Maret":
        income += thr_amount

    # Rutin
    exp_rutin = total_rutin_default
    # Override check
    if (month == override_month) and (override_amount > 0):
        exp_rutin = override_amount

    # Wishlist
    wishlist_cost = 0
    for item in wishlist_list:
        if item.get("enabled") and item.get("month") == month:
            wishlist_cost += int(item.get("price", 0))

    total_exp = exp_rutin + wishlist_cost
    balance_before = current_balance
    current_balance = current_balance + income - total_exp

    data.append({
        "Bulan": month,
        "Income": income,
        "Rutin": exp_rutin,
        "Wishlist": wishlist_cost,
        "TotalOut": total_exp,
        "EndBalance": current_balance
    })

df_calc = pd.DataFrame(data)

# =========================
# Dashboard Section
# =========================
st.markdown("---")
st.subheader("📊 Dashboard Overview")
# Top Metrics
tot_inc = df_calc["Income"].sum()
tot_exp = df_calc["TotalOut"].sum()
tot_wish = df_calc["Wishlist"].sum()
final_bal = df_calc["EndBalance"].iloc[-1]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Pemasukan", f"Rp {tot_inc/1e6:,.1f} Jt")
m2.metric("Total Pengeluaran", f"Rp {tot_exp/1e6:,.1f} Jt")
m3.metric("Total Wishlist", f"Rp {tot_wish/1e6:,.1f} Jt")
m4.metric("Sisa Akhir Tahun", f"Rp {final_bal:,.0f}", delta="Net Worth" if final_bal > 0 else "Deficit")

st.markdown("### 📈 Visualisasi Keuangan")

g1, g2 = st.columns([1.5, 1])

with g1:
    # Stacked Bar Chart for Expenses
    fig_bar = px.bar(
        df_calc, 
        x="Bulan", 
        y=["Rutin", "Wishlist"], 
        title="Komposisi Pengeluaran Bulanan",
        color_discrete_map={"Rutin": "#3b82f6", "Wishlist": "#f43f5e"},
        template="plotly_dark"
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Tipe"
    )
    st.plotly_chart(fig_bar, width="stretch")

with g2:
    # Area Chart for Balance
    fig_area = px.area(
        df_calc,
        x="Bulan",
        y="EndBalance",
        title="Proyeksi Tabungan",
        markers=True,
        color_discrete_sequence=["#10b981"],
        template="plotly_dark"
    )
    fig_area.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Saldo (Rp)"
    )
    st.plotly_chart(fig_area, width="stretch")

# =========================
# Detail Section
# =========================
st.markdown("---")
st.subheader("📄 Rincian Per Bulan")

# Styling the dataframe
st.dataframe(
    df_calc.style.format({
        "Income": "Rp {:,.0f}",
        "Rutin": "Rp {:,.0f}",
        "Wishlist": "Rp {:,.0f}",
        "TotalOut": "Rp {:,.0f}",
        "EndBalance": "Rp {:,.0f}"
    }),
    width="stretch",
    height=500
)

