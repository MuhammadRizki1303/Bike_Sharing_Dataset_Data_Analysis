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
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Fungsi untuk memuat dan mempersiapkan data
@st.cache_data
def load_data():
    # Pastikan path dataset benar
    base_path = "Bike Sharing Dataset"
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
            return "Kering"
        elif hum < 65:
            return "Ideal"
        else:
            return "Lembab"
    
    for df in [day_df, hour_df]:
        df["humidity_category"] = df["humidity"].apply(categorize_humidity)
    
    return day_df, hour_df

# Memuat data
day_df, hour_df = load_data()

# Tampilan Dashboard
st.title("🚲 Dashboard Penyewaan Sepeda")
st.markdown("Analisis data penyewaan sepeda berdasarkan berbagai faktor.")

# Sidebar untuk filter
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

# Visualisasi
st.subheader("Jumlah Penyewaan Berdasarkan Jam")
if not hour_df.empty:
    hourly_count = hour_df.groupby('hour')['total_rentals'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='hour', y='total_rentals', data=hourly_count, ax=ax, palette='viridis')
    ax.set_xlabel("Jam")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

st.subheader("Jumlah Penyewaan Berdasarkan Musim")
if not day_df.empty:
    season_count = day_df.groupby('season')['total_rentals'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='season', y='total_rentals', data=season_count, ax=ax, palette='viridis')
    ax.set_xlabel("Musim")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

# Menampilkan pertanyaan
st.subheader("📌 Bagaimana tren jumlah penyewaan sepeda berdasarkan hari kerja dan akhir pekan?")
st.markdown("Tren penyewaan sepeda berdasarkan tipe hari (Weekday vs. Weekend) dapat memberikan wawasan apakah orang lebih sering menyewa sepeda pada hari kerja atau akhir pekan.")

# Visualisasi Penyewaan Berdasarkan Tipe Hari
day_category_count = day_df.groupby("day_category")["total_rentals"].sum().reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="day_category", y="total_rentals", data=day_category_count, ax=ax, palette="coolwarm")
ax.set_xlabel("Kategori Hari")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan")
st.pyplot(fig)

# Menampilkan kesimpulan
weekday_rentals = day_category_count[day_category_count["day_category"] == "Weekday"]["total_rentals"].values[0]
weekend_rentals = day_category_count[day_category_count["day_category"] == "Weekend"]["total_rentals"].values[0]

if weekday_rentals > weekend_rentals:
    st.markdown(f"✅ **Hasil:** Jumlah penyewaan sepeda lebih tinggi pada **hari kerja ({weekday_rentals:,})** dibandingkan akhir pekan ({weekend_rentals:,}).")
else:
    st.markdown(f"✅ **Hasil:** Jumlah penyewaan sepeda lebih tinggi pada **akhir pekan ({weekend_rentals:,})** dibandingkan hari kerja ({weekday_rentals:,}).")

# Menampilkan pertanyaan
st.subheader("📌 Bagaimana pengaruh suhu terhadap jumlah penyewaan sepeda?")
st.markdown("Suhu udara dapat mempengaruhi keputusan seseorang untuk menyewa sepeda. Grafik berikut menunjukkan hubungan antara suhu dan jumlah penyewaan.")

# Scatter plot suhu vs penyewaan
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x=day_df["temp"], y=day_df["total_rentals"], alpha=0.6, ax=ax)
ax.set_xlabel("Suhu (Normalized)")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Pengaruh Suhu terhadap Penyewaan Sepeda")
st.pyplot(fig)

# Menampilkan kesimpulan
st.markdown("✅ **Hasil:** Dari grafik terlihat bahwa semakin tinggi suhu, jumlah penyewaan cenderung meningkat. Hal ini menunjukkan bahwa orang lebih sering menyewa sepeda saat cuaca lebih hangat.")

