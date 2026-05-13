import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cyber-Trener Dashboard", page_icon="🏐", layout="wide")


def load_data():
    """wczytuje historie treningow z bazy danych"""
    try:
        conn = sqlite3.connect('cyber_trener.db')
        df = pd.read_sql_query("SELECT * FROM historia_treningow", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()


st.title("🏐 Cyber-Trener: Panel Analityczny")
st.markdown("Sprawdź swoje błędy i analizuj postępy w odbiciu dolnym!")

df = load_data()

if df.empty:
    st.warning("Baza danych jest pusta lub nie istnieje. Wykonaj najpierw trening!")
else:
    st.success("Połączono z bazą danych pomyślnie!")

    df['data_treningu'] = pd.to_datetime(df['data_treningu'])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ostatnie błędy (Historia)")
        st.dataframe(df.sort_values(by='data_treningu', ascending=False), use_container_width=True)

    with col2:
        st.subheader("Najczęściej popełniane błędy")
        bledy_count = df['typ_bledu'].value_counts().reset_index()
        bledy_count.columns = ['Typ Błędu', 'Liczba']

        fig = px.pie(bledy_count, values='Liczba', names='Typ Błędu', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)