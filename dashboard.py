import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cyber-Trener Dashboard", page_icon="🏐", layout="wide")


def load_data():
    try:
        conn = sqlite3.connect('cyber_trener.db')
        df = pd.read_sql_query("SELECT * FROM historia_treningow", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


st.title("🏐 Cyber-Trener: Panel Analityczny")

df = load_data()

if df.empty:
    st.warning("Baza danych jest pusta. Wykonaj najpierw trening!")
else:
    df['data_treningu'] = pd.to_datetime(df['data_treningu'])

    uzytkownicy = df['uzytkownik'].unique()
    wybrany_user = st.sidebar.selectbox("Wybierz profil:", uzytkownicy)
    df_user = df[df['uzytkownik'] == wybrany_user]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Ostatnie błędy: {wybrany_user}")
        st.dataframe(df_user.sort_values(by='data_treningu', ascending=False), use_container_width=True)

    with col2:
        st.subheader("Najczęściej popełniane błędy")
        bledy_count = df_user['typ_bledu'].value_counts().reset_index()
        bledy_count.columns = ['Typ Błędu', 'Liczba']

        if not bledy_count.empty:
            fig = px.pie(bledy_count, values='Liczba', names='Typ Błędu', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Brak błędów! Świetny trening.")