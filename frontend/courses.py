import streamlit as st
from google.cloud import storage

BUCKET_NAME = "bucket-agentic-era-hack"
FOLDER_NAME = "courses/"

def list_text_files():
    """Liste tous les fichiers texte dans le dossier GCP Storage."""
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME, prefix=FOLDER_NAME)
    return [blob.name.replace(FOLDER_NAME, "") for blob in blobs ]

def read_text_file(file_name):
    """Lit le contenu d'un fichier texte depuis GCP Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FOLDER_NAME + file_name)
    return blob.download_as_text()

def courses_page():
    """Affiche la page des cours avec la liste des fichiers disponibles."""
    st.title("📚 Courses")
    st.write("Sélectionnez un cours pour afficher son contenu.")

    files = list_text_files()

    if not files:
        st.warning("Aucun fichier disponible dans le bucket.")
        return

    selected_file = st.selectbox("Choisissez un fichier :", files)

    if selected_file:
        content = read_text_file(selected_file)
        st.subheader(f"📖 Contenu de {selected_file}")
        st.markdown(content)
        # st.text_area("", content, height=400, disabled=True)