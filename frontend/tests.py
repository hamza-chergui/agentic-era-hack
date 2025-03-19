import streamlit as st
import json
import random
from google.cloud import storage  # Accès au bucket GCS

BUCKET_NAME = "bucket-agentic-era-hack"
FOLDER_NAME = "tests"

def list_json_files(bucket_name, folder_name):
    """Liste les fichiers JSON dans un dossier du bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name + "/")
    return [blob.name for blob in blobs if blob.name.endswith(".json")]

def load_test_from_bucket(bucket_name, file_path):
    """Charge un fichier JSON depuis le bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    return json.loads(content)

def tests_page():
    """Affiche l'interface du test interactif."""
    st.title("📋 Test d'évaluation")

    # Lister les fichiers de test
    test_files = list_json_files(BUCKET_NAME, FOLDER_NAME)
    if not test_files:
        st.error("Aucun test disponible.")
        return

    # Sélection du test
    test_file = st.selectbox("Sélectionnez un test :", test_files, key="selected_test")
    
    if "test_data" not in st.session_state or st.session_state["last_test_file"] != test_file:
        st.session_state["test_data"] = load_test_from_bucket(BUCKET_NAME, test_file)
        st.session_state["questions"] = st.session_state["test_data"].get("questions", [])
        random.shuffle(st.session_state["questions"])
        st.session_state["user_answers"] = {}
        st.session_state["current_question"] = 0  # Index de la question actuelle
        st.session_state["last_test_file"] = test_file

    questions = st.session_state["questions"]
    total_questions = len(questions)

    if total_questions == 0:
        st.error("Aucune question disponible dans ce test.")
        return

    current_index = st.session_state["current_question"]
    question_data = questions[current_index]

    st.subheader(f"Question {current_index + 1}/{total_questions}: {question_data['question']}")

    # Récupération de la réponse stockée (s'il y en a une)
    if f"q{current_index}" not in st.session_state["user_answers"]:
        st.session_state["user_answers"][f"q{current_index}"] = None

    # Affichage des choix de réponse
    selected_answer = st.radio(
        "Choisissez une réponse :",
        question_data["answers"],
        index=question_data["answers"].index(st.session_state["user_answers"].get(f"q{current_index}", None))
        if st.session_state["user_answers"][f"q{current_index}"] in question_data["answers"]
        else None,
        key=f"radio_q{current_index}"
    )

    # Mise à jour de la réponse
    if selected_answer:
        st.session_state["user_answers"][f"q{current_index}"] = selected_answer

    col1, col2 = st.columns([1, 1])

    # Bouton "Précédent"
    if col1.button("⬅️ Précédent", disabled=current_index == 0):
        st.session_state["current_question"] -= 1
        st.rerun()

    # Bouton "Suivant"
    if col2.button("Suivant ➡️", disabled=current_index == total_questions - 1):
        st.session_state["current_question"] += 1
        st.rerun()

    # Bouton "Valider mes réponses"
    if st.session_state["current_question"] == total_questions - 1:
        if st.button("✅ Valider mes réponses"):
            score = sum(1 for i, q in enumerate(questions) if st.session_state["user_answers"].get(f"q{i}") == q["correct_answer"])
            st.success(f"✅ Votre score : {score} / {total_questions}")

            if score == total_questions:
                st.balloons()
                st.write("🎉 Félicitations, score parfait !")
            elif score >= total_questions * 0.7:
                st.write("👍 Bon travail !")
            else:
                st.write("📚 Continuez à apprendre !")