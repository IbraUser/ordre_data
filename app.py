import streamlit as st
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Tri & Remplissage Excel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEBUG (à laisser pour vérifier démarrage) ---
st.write("APP OK ✅")

# --- CSS + NAVBAR FIXÉE ---
st.markdown("""
<style>

/* NAVBAR FIXE */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #E5E7EB;
    border-bottom: 1px solid #D1D5DB;
    z-index: 999;

    display: flex;
    align-items: center;
    justify-content: center;
}

/* TITRE CENTRÉ */
.navbar-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-size: 20px;
    font-weight: 600;
    color: #111827;
}

/* Décalage contenu */
.block-container {
    padding-top: 80px !important;
}

/* Fond global */
.stApp {
    background-color: #F5F7FA !important;
}

/* Header transparent */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ECEFF3 !important;
    border-right: 1px solid #D0D0D0;
}

/* Icône sidebar */
button[kind="header"] svg {
    fill: #374151 !important;
}

/* Texte */
h1, h2, h3, h4, h5, h6, p, label {
    color: #1F2937 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 1px solid #C0C0C0 !important;
    border-radius: 10px;
    padding: 15px;
}

/* Boutons */
.stButton>button {
    background-color: #6B7280 !important;
    color: #FFFFFF !important;
    border: 1px solid #9CA3AF !important;
    border-radius: 8px;
}
.stButton>button:hover {
    background-color: #4B5563 !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #E5E7EB !important;
    color: #111827 !important;
    border: 1px solid #9CA3AF !important;
}
div[data-baseweb="select"] span {
    color: #111827 !important;
}

/* Dropdown */
div[role="listbox"] {
    background-color: #E5E7EB !important;
}
div[role="option"] {
    background-color: #E5E7EB !important;
    color: #111827 !important;
}
div[role="option"]:hover {
    background-color: #D1D5DB !important;
}

</style>

<div class="navbar">
    <div class="navbar-title">📂 Tri et Remplissage Automatique</div>
</div>
""", unsafe_allow_html=True)

# --- FONCTIONS ---
def nettoyer(val):
    if pd.isna(val):
        return ""
    v = str(val).strip()
    if v.endswith('.0'):
        v = v[:-2]
    return v

def executer_traitement(df_base, df_data, col_sap_base, col_sap_data):
    col_num_base = df_base.columns[0]
    col_num_data = df_data.columns[0]

    df_b = df_base.copy()
    df_d = df_data.copy()

    df_b['CLE_TEMP'] = df_b[col_sap_base].apply(nettoyer)
    df_d['CLE_TEMP'] = df_d[col_sap_data].apply(nettoyer)

    mapping_numero = dict(zip(df_b['CLE_TEMP'], df_b[col_num_base]))
    ordre_base = df_b['CLE_TEMP'].unique().tolist()
    mapping_ordre = {code: i for i, code in enumerate(ordre_base)}

    df_d[col_num_data] = df_d['CLE_TEMP'].map(mapping_numero)
    df_d['POSITION_TRI'] = df_d['CLE_TEMP'].map(mapping_ordre).fillna(999999)

    df_final = df_d.sort_values(by='POSITION_TRI', kind='mergesort').copy()
    df_final = df_final.drop(columns=['CLE_TEMP', 'POSITION_TRI'])

    return df_final

# --- SIDEBAR ---
st.sidebar.title("🛠️ Menu")
page = st.sidebar.radio("Navigation", ["Accueil", "Instructions"])

# --- INTERFACE ---
if page == "Accueil":
    st.write("Ordonnez vos données selon un fichier de référence.")
    st.divider()

    # BASE
    st.subheader("1️⃣ Fichier de BASE")
    file_base = st.file_uploader("Importer BASE", type=["xlsx", "xls"])

    if file_base is not None:
        df_base = pd.read_excel(file_base, dtype=str)
        st.write("Aperçu BASE")
        st.dataframe(df_base.head())

    st.divider()

    # DATA
    st.subheader("2️⃣ Fichier DATA")
    file_data = st.file_uploader("Importer DATA", type=["xlsx", "xls"])

    if file_data is not None:
        df_data = pd.read_excel(file_data, dtype=str)
        st.write("Aperçu DATA")
        st.dataframe(df_data.head())

    # TRAITEMENT
    if file_base is not None and file_data is not None:
        st.divider()
        st.subheader("Paramètres")

        c1, c2 = st.columns(2)
        with c1:
            col_sap_base = st.selectbox("Colonne BASE", df_base.columns)
        with c2:
            col_sap_data = st.selectbox("Colonne DATA", df_data.columns)

        if st.button("Lancer traitement"):
            try:
                df_res = executer_traitement(df_base, df_data, col_sap_base, col_sap_data)
                st.success("Terminé")
                st.dataframe(df_res.head(10))

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False)

                st.download_button(
                    label="Télécharger Excel",
                    data=buffer.getvalue(),
                    file_name="RESULTAT.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Erreur : {e}")

else:
    st.subheader("Instructions")
    st.write("Importer BASE puis DATA. La première colonne de BASE sera utilisée comme numéro.")