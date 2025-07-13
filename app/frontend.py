import streamlit as st
import json

# Load the story from story.json
story_data = '''
{
  "states": [
    {
      "id": "start",
      "text": "Ti svegli su una spiaggia deserta. All'orizzonte vedi una capanna e una grotta.",
      "transitions": [
        {"action": "Vai verso la capanna", "target": "hut"},
        {"action": "Esplora la grotta", "target": "cave"}
      ]
    },
    {
      "id": "hut",
      "text": "La capanna è abbandonata ma trovi una mappa che indica un tesoro nella grotta.",
      "transitions": [
        {"action": "Segui la mappa e vai alla grotta", "target": "cave"}
      ]
    },
    {
      "id": "cave",
      "text": "Dentro la grotta buia, un serpente gigante blocca il passaggio.",
      "transitions": [
        {"action": "Affronta il serpente", "target": "fight"},
        {"action": "Fuggi", "target": "beach_end"}
      ]
    },
    {
      "id": "fight",
      "text": "Sconfiggi il serpente con astuzia e trovi uno scrigno dorato.",
      "transitions": [
        {"action": "Apri lo scrigno", "target": "victory"}
      ]
    },
    {
      "id": "victory",
      "text": "Hai trovato il tesoro nascosto! Sei ricco.",
      "transitions": []
    },
    {
      "id": "beach_end",
      "text": "Torni sulla spiaggia. Il mistero del tesoro resta irrisolto.",
      "transitions": []
    }
  ],
  "initial": "start",
  "goal": "victory"
}
'''

# Parse story JSON
story = json.loads(story_data)

# Game state
if 'current_state' not in st.session_state:
    st.session_state.current_state = story['initial']

def update_state(target_id):
    st.session_state.current_state = target_id

# Display current state text
current_state = next(state for state in story['states'] if state['id'] == st.session_state.current_state)
st.write(current_state['text'])

# Display choices
if current_state['transitions']:
    choice = st.selectbox("Fai la tua scelta:", [t['action'] for t in current_state['transitions']])
    if st.button("Conferma scelta"):
        selected_transition = next(t for t in current_state['transitions'] if t['action'] == choice)
        update_state(selected_transition['target'])
else:
    st.write("La tua avventura è finita.")