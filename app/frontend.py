import streamlit as st
import json

from constant import load_story

st.set_page_config(page_title="QuestMaster", layout="centered")
st.title("⚔️ QuestMaster")


@st.cache_data
def load_stories():
    story : str = load_story()
    return json.loads(story)

if "current_state" not in st.session_state:
    st.session_state.current_state = "start"

def change_state(next_state):
    st.session_state.current_state = next_state

story = load_stories()
state = st.session_state.current_state

if state not in story:
    st.error(f"Stato non valido: '{state}' non trovato in story.json")
    st.stop()

scene = story[state]
st.markdown(f"### {scene['text']}")

if scene.get("actions"):
    for action_text, next_state in scene["actions"].items():
        if st.button(action_text):
            change_state(next_state)
            st.rerun()
else:
    st.success("🏁 Fine dell'avventura. Ricarica la pagina per ricominciare.")