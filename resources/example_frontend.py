import streamlit as st

# === STORY DATA ===
story = {
    "states": {
        "start": {
            "text": "Ti svegli su una spiaggia deserta. All'orizzonte vedi una capanna e una grotta.",
            "transitions": {
                "Vai verso la capanna": "hut",
                "Esplora la grotta": "cave"
            }
        },
        "hut": {
            "text": "La capanna è abbandonata ma trovi una mappa che indica un tesoro nella grotta.",
            "transitions": {
                "Segui la mappa e vai alla grotta": "cave"
            }
        },
        "cave": {
            "text": "Dentro la grotta buia, un serpente gigante blocca il passaggio.",
            "transitions": {
                "Affronta il serpente": "fight",
                "Fuggi": "beach_end"
            }
        },
        "fight": {
            "text": "Sconfiggi il serpente con astuzia e trovi uno scrigno dorato.",
            "transitions": {
                "Apri lo scrigno": "victory"
            }
        },
        "victory": {
            "text": "Hai trovato il tesoro nascosto! Sei ricco.",
            "transitions": {}
        },
        "beach_end": {
            "text": "Torni sulla spiaggia. Il mistero del tesoro resta irrisolto.",
            "transitions": {}
        }
    },
    "initial": "start",
    "goal": "victory"
}

# === SESSION STATE INIT ===
if "current_state" not in st.session_state:
    st.session_state.current_state = story["initial"]

# === RENDER CURRENT STATE ===
state = story["states"][st.session_state.current_state]
st.markdown(f"## {state['text']}")

# === RENDER CHOICES ===
if state["transitions"]:
    for action, target in state["transitions"].items():
        if st.button(action):
            st.session_state.current_state = target
            st.rerun()
else:
    st.success("Fine della storia.")
    if st.button("Ricomincia"):
        st.session_state.current_state = story["initial"]
        st.rerun()
