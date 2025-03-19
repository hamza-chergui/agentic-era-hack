import streamlit as st
import json
import random
from google.cloud import storage

BUCKET_NAME = "bucket-agentic-era-hack"

def list_folders():
    """Liste tous les dossiers (topics) dans le bucket GCP Storage."""
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME)
    folders = set()
    for blob in blobs:
        folder = blob.name.split('/')[0]
        folders.add(folder)
    return list(folders)

def read_file(bucket_name, file_path):
    """Lit le contenu d'un fichier depuis GCP Storage."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    return blob.download_as_text()

def combined_page():
    """Page combinée avec la sélection d'un topic, un cours et un test."""
    st.title("📚 Courses and tests")

    # Lister les dossiers (topics) disponibles
    topics = list_folders()
    if not topics:
        st.warning("Aucun topic disponible dans le bucket.")
        return

    selected_topic = st.selectbox("Choisissez un topic :", topics)

    if selected_topic:
        # Charger et afficher le contenu du cours
        course_file = f"{selected_topic}/course"
        try:
            course_content = read_file(BUCKET_NAME, course_file)
            st.subheader(f"📖 Cours - {selected_topic}")
            st.markdown(course_content)
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier cours : {e}")
        
        # Charger et afficher le test
        test_file = f"{selected_topic}/test"
        try:
            test_data = json.loads(read_file(BUCKET_NAME, test_file))
            questions = test_data.get("questions", [])
            if questions:
                st.subheader(f"📋 Test - {selected_topic}")
                
                if "test_data" not in st.session_state or st.session_state["last_test_file"] != test_file:
                    random.shuffle(questions)
                    st.session_state["user_answers"] = {}
                    st.session_state["current_question"] = 0  # Index de la question actuelle
                    st.session_state["last_test_file"] = test_file
                
                total_questions = len(questions)
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

                # Bouton "Suivant"
                if col2.button("Suivant ➡️", disabled=current_index == total_questions - 1):
                    st.session_state["current_question"] += 1

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

        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier test : {e}")
