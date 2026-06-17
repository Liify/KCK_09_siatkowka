import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database_manager import DB_PATH

st.set_page_config(page_title="Cyber-Trener Dashboard", page_icon="🏐", layout="wide")

@st.cache_data(ttl=10)   # odświeżanie co 10 sekund
def load_data():
    try:
        if not os.path.exists(DB_PATH):
            return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM historia_treningow", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Błąd odczytu bazy: {e}")
        return pd.DataFrame()

st.title("🏐 Cyber-Trener: Panel Analityczny")
st.caption(f"Baza danych: `{DB_PATH}`")

if st.button("🔄 Odśwież dane"):
    st.cache_data.clear()

df = load_data()

if df.empty:
    st.warning("Baza danych jest pusta lub nie istnieje. Wykonaj najpierw trening!")
    st.stop()

df['data_treningu'] = pd.to_datetime(df['data_treningu'])

uzytkownicy = df['uzytkownik'].unique()
wybrany_user = st.sidebar.selectbox("Wybierz profil:", uzytkownicy)
df_user = df[df['uzytkownik'] == wybrany_user]

total = len(df_user)
najczestszy = df_user['typ_bledu'].value_counts().idxmax() if total > 0 else "—"
ostatni_trening = df_user['data_treningu'].max().strftime("%Y-%m-%d %H:%M") if total > 0 else "—"

m1, m2, m3 = st.columns(3)
m1.metric("Łącznie błędów", total)
m2.metric("Najczęstszy błąd", najczestszy)
m3.metric("Ostatni trening", ostatni_trening)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Historia błędów: {wybrany_user}")
    st.dataframe(
        df_user[['data_treningu', 'typ_bledu']]
        .sort_values(by='data_treningu', ascending=False)
        .reset_index(drop=True),
        use_container_width=True
    )

with col2:
    st.subheader("Rozkład błędów")
    bledy_count = df_user['typ_bledu'].value_counts().reset_index()
    bledy_count.columns = ['Typ Błędu', 'Liczba']

    if not bledy_count.empty:
        fig = px.pie(
            bledy_count,
            values='Liczba',
            names='Typ Błędu',
            hole=0.35,
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Brak błędów — świetny trening! 🏆")

st.subheader("Błędy w czasie")
df_timeline = df_user.groupby(['data_treningu', 'typ_bledu']).size().reset_index(name='liczba')
if not df_timeline.empty:
    fig2 = px.bar(df_timeline, x='data_treningu', y='liczba', color='typ_bledu',
                  labels={'data_treningu': 'Data', 'liczba': 'Liczba', 'typ_bledu': 'Błąd'})
    st.plotly_chart(fig2, use_container_width=True)