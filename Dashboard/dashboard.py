import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Dashboard by Muhammad Rizki MC-55",
    page_icon="🚲",
    layout="wide"
)

# Sambutan
st.title("Selamat Datang di Dashboard Muhammad Rizki dari MC-55")
st.markdown("""
    **Dashboard Penyewaan Sepeda** ini dirancang untuk menganalisis pola penyewaan sepeda berdasarkan berbagai faktor seperti waktu, musim, cuaca, dan kondisi lingkungan. 
    Mari eksplorasi data bersama-sama!
""")

# Fungsi untuk memuat dan mempersiapkan data
@st.cache_data
def load_data():
    # Pastikan path dataset benar
    base_path = "Dashboard"
    day_df = pd.read_csv(os.path.join(base_path, "day.csv"))
    hour_df = pd.read_csv(os.path.join(base_path, "hour.csv"))
    
    # Menghapus kolom yang tidak diperlukan
    for df in [day_df, hour_df]:
        df.drop(['workingday'], axis=1, inplace=True)
    
    # Mengubah tipe data menjadi kategori
    kategori_kolom = ['season', 'mnth', 'holiday', 'weekday', 'weathersit']
    for df in [day_df, hour_df]:
        for col in kategori_kolom:
            df[col] = df[col].astype("category")
    
    # Mengubah tipe data tanggal
    for df in [day_df, hour_df]:
        df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Mengganti nama kolom agar lebih mudah dipahami
    rename_dict = {
        'yr': 'year',
        'mnth': 'month',
        'weekday': 'day_of_week',
        'weathersit': 'weather_situation',
        'windspeed': 'wind_speed',
        'cnt': 'total_rentals',
        'hum': 'humidity'
    }
    day_df.rename(columns=rename_dict, inplace=True)
    hour_df.rename(columns={**rename_dict, 'hr': 'hour'}, inplace=True)
    
    # Mengganti nilai kategori dengan label yang lebih mudah dibaca
    mapping_dict = {
        'season': {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'},
        'month': {i: month for i, month in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)},
        'weather_situation': {1: 'Clear', 2: 'Misty', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'},
        'day_of_week': {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                        4: 'Thursday', 5: 'Friday', 6: 'Saturday'},
        'year': {0: '2011', 1: '2012'}
    }
    for col, mapping in mapping_dict.items():
        day_df[col] = day_df[col].replace(mapping)
        hour_df[col] = hour_df[col].replace(mapping)
    
    # Menentukan kategori hari
    def categorize_day(day):
        return "Weekend" if day in ["Saturday", "Sunday"] else "Weekday"
    
    for df in [day_df, hour_df]:
        df["day_category"] = df["day_of_week"].apply(categorize_day)
    
    # Menentukan kategori kelembaban
    def categorize_humidity(hum):
        if hum < 45:
            return "Dry"
        elif hum < 65:
            return "Ideal"
        else:
            return "Humid"
    
    for df in [day_df, hour_df]:
        df["humidity_category"] = df["humidity"].apply(categorize_humidity)
    
    return day_df, hour_df

# Memuat data
day_df, hour_df = load_data()

# Sidebar untuk filter
st.sidebar.title("🔍 Filter Data")
tahun = st.sidebar.selectbox("Pilih Tahun", ['Semua', '2011', '2012'])
if tahun != 'Semua':
    day_df = day_df[day_df['year'] == tahun]
    hour_df = hour_df[hour_df['year'] == tahun]

musim = st.sidebar.selectbox("Pilih Musim", ['Semua', 'Spring', 'Summer', 'Fall', 'Winter'])
if musim != 'Semua':
    day_df = day_df[day_df['season'] == musim]
    hour_df = hour_df[hour_df['season'] == musim]

tipe_hari = st.sidebar.selectbox("Pilih Tipe Hari", ['Semua', 'Weekday', 'Weekend'])
if tipe_hari != 'Semua':
    day_df = day_df[day_df['day_category'] == tipe_hari]
    hour_df = hour_df[hour_df['day_category'] == tipe_hari]

# Menampilkan metrik
st.header("📊 Metrik Utama")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.metric("Total Penyewaan", f"{day_df['total_rentals'].sum():,}")

with col2:
    st.metric("Rata-rata Penyewaan per Hari", f"{day_df['total_rentals'].mean():,.0f}")

with col3:
    if not day_df.empty:
        max_day = day_df.loc[day_df['total_rentals'].idxmax()]
        st.metric("Penyewaan Tertinggi", f"{int(max_day['total_rentals']):,}", 
                  f"{max_day['dteday'].strftime('%d %b %Y')}")

# Analisis 1: Penyewaan Berdasarkan Tipe Hari
st.header("📈 Analisis Data Penyewaan Sepeda")
st.subheader("1. Bagaimana perbandingan penyewaan sepeda antara hari kerja dan akhir pekan?")
st.markdown("""
    Pertanyaan ini bertujuan untuk membandingkan pola penyewaan sepeda pada hari kerja (Weekday) dan akhir pekan (Weekend).
""")

day_category_count = day_df.groupby("day_category")["total_rentals"].sum().reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="day_category", y="total_rentals", data=day_category_count, ax=ax, palette="coolwarm")
ax.set_xlabel("Kategori Hari")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan")
st.pyplot(fig)

# Kesimpulan
weekday_rentals = day_category_count[day_category_count["day_category"] == "Weekday"]["total_rentals"].values[0]
weekend_rentals = day_category_count[day_category_count["day_category"] == "Weekend"]["total_rentals"].values[0]

if weekday_rentals > weekend_rentals:
    st.markdown(f"""
        ✅ **Kesimpulan:** 
        - Penyewaan sepeda lebih tinggi pada **hari kerja ({weekday_rentals:,})** dibandingkan akhir pekan ({weekend_rentals:,}).
        - Hal ini menunjukkan bahwa sepeda banyak digunakan untuk keperluan transportasi sehari-hari seperti pergi ke kantor atau sekolah.
    """)
else:
    st.markdown(f"""
        ✅ **Kesimpulan:** 
        - Penyewaan sepeda lebih tinggi pada **akhir pekan ({weekend_rentals:,})** dibandingkan hari kerja ({weekday_rentals:,}).
        - Hal ini menunjukkan bahwa sepeda lebih sering digunakan untuk aktivitas rekreasi atau bersantai di akhir pekan.
    """)

# Analisis 2: Pengaruh Suhu terhadap Penyewaan
st.subheader("2. Bagaimana pengaruh suhu terhadap jumlah penyewaan sepeda?")
st.markdown("""
    Pertanyaan ini bertujuan untuk memahami apakah suhu udara memengaruhi keputusan seseorang untuk menyewa sepeda.
""")

fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x=day_df["temp"], y=day_df["total_rentals"], alpha=0.6, ax=ax, color='green')
ax.set_xlabel("Suhu (Normalized)")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Pengaruh Suhu terhadap Penyewaan Sepeda")
st.pyplot(fig)

# Kesimpulan
correlation = day_df["temp"].corr(day_df["total_rentals"])
st.markdown(f"""
    ✅ **Kesimpulan:** 
    - Terdapat korelasi positif antara suhu dan jumlah penyewaan sepeda (koefisien korelasi: **{correlation:.2f}**).
    - Semakin tinggi suhu, semakin banyak orang yang menyewa sepeda. Hal ini menunjukkan bahwa cuaca yang hangat mendorong orang untuk bersepeda.
""")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p>Dibuat oleh <strong>Muhammad Rizki MC-55</strong></p>
        <p>© 2023 - Dashboard Penyewaan Sepeda MR-mc-55</p>
    </div>
""", unsafe_allow_html=True)