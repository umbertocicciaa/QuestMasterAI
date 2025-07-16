"""UI components and Streamlit utilities."""

from typing import Any, Dict, List, Optional

import streamlit as st
from ..models import StoryGraph, StoryState


def display_story_state(state: StoryState) -> None:
    """Display a story state in Streamlit.
    
    Args:
        state: Story state to display
    """
    # Display story text
    st.markdown(f"### {state.text}")
    
    # Display image if available
    if state.image_url:
        st.image(state.image_url, use_column_width=True)
    
    # Add some spacing
    st.markdown("---")


def display_action_choices(state: StoryState) -> Optional[str]:
    """Display action choices and return selected target state.
    
    Args:
        state: Current story state
        
    Returns:
        Target state ID if action selected, None otherwise
    """
    if not state.actions:
        return None
    
    st.markdown("**What do you want to do?**")
    
    # Create buttons for each action
    cols = st.columns(min(len(state.actions), 3))
    
    for i, action in enumerate(state.actions):
        col = cols[i % len(cols)]
        
        with col:
            if st.button(
                action.text,
                key=f"action_{state.id}_{action.id}",
                help=action.description,
                use_container_width=True,
            ):
                return action.target_state
    
    return None


def display_game_header(story: StoryGraph) -> None:
    """Display game header with title and description.
    
    Args:
        story: Story graph
    """
    st.title(story.title)
    
    if story.description:
        st.markdown(f"*{story.description}*")
    
    st.markdown("---")


def display_game_sidebar(story: StoryGraph, current_state_id: str) -> None:
    """Display game sidebar with progress and controls.
    
    Args:
        story: Story graph
        current_state_id: Current state ID
    """
    with st.sidebar:
        st.markdown("## 🎮 Game Info")
        
        # Game progress
        visited_states = st.session_state.get("visited_states", set())
        progress = len(visited_states) / len(story.states)
        st.progress(progress, text=f"Progress: {len(visited_states)}/{len(story.states)} states")
        
        # Current state info
        st.markdown(f"**Current State:** {current_state_id}")
        
        # Restart button
        if st.button("🔄 Restart Game", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and key.startswith("story_"):
                    del st.session_state[key]
            if "visited_states" in st.session_state:
                del st.session_state["visited_states"]
            st.rerun()
        
        # Story metadata
        if story.metadata:
            st.markdown("## 📖 Story Info")
            for key, value in story.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    st.markdown(f"**{key.title()}:** {value}")


def display_breadcrumbs(visited_states: List[str], story: StoryGraph) -> None:
    """Display breadcrumb navigation.
    
    Args:
        visited_states: List of visited state IDs
        story: Story graph
    """
    if len(visited_states) <= 1:
        return
    
    st.markdown("**Your Journey:**")
    
    breadcrumb_text = " → ".join([
        story.states[state_id].id if state_id in story.states else state_id
        for state_id in visited_states[-5:]  # Show last 5 states
    ])
    
    if len(visited_states) > 5:
        breadcrumb_text = "... → " + breadcrumb_text
    
    st.markdown(f"`{breadcrumb_text}`")
    st.markdown("---")


def display_terminal_state(state: StoryState, story: StoryGraph) -> None:
    """Display terminal state with special formatting.
    
    Args:
        state: Terminal story state
        story: Story graph
    """
    # Special formatting for endings
    if "victory" in state.id.lower() or "success" in state.id.lower():
        st.success("🎉 **Congratulations!** 🎉")
    elif "defeat" in state.id.lower() or "failure" in state.id.lower():
        st.error("💀 **Game Over** 💀")
    else:
        st.info("🏁 **The End** 🏁")
    
    # Display the state text
    st.markdown(f"### {state.text}")
    
    # Display image if available
    if state.image_url:
        st.image(state.image_url, use_column_width=True)
    
    # Show final stats
    visited_states = st.session_state.get("visited_states", set())
    total_states = len(story.states)
    completion_rate = len(visited_states) / total_states * 100
    
    st.markdown("---")
    st.markdown("### 📊 Final Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("States Visited", len(visited_states))
    
    with col2:
        st.metric("Total States", total_states)
    
    with col3:
        st.metric("Completion", f"{completion_rate:.1f}%")


def initialize_game_state(story: StoryGraph) -> str:
    """Initialize game state in Streamlit session.
    
    Args:
        story: Story graph
        
    Returns:
        Initial state ID
    """
    # Initialize session state
    if "story_current_state" not in st.session_state:
        st.session_state.story_current_state = story.initial_state
    
    if "visited_states" not in st.session_state:
        st.session_state.visited_states = set()
    
    # Add current state to visited
    current_state = st.session_state.story_current_state
    st.session_state.visited_states.add(current_state)
    
    return current_state


def handle_state_transition(target_state_id: str, story: StoryGraph) -> None:
    """Handle transition to a new state.
    
    Args:
        target_state_id: Target state ID
        story: Story graph
    """
    if target_state_id in story.states:
        st.session_state.story_current_state = target_state_id
        st.session_state.visited_states.add(target_state_id)
        st.rerun()
    else:
        st.error(f"Invalid state transition: {target_state_id}")


def create_story_game_app(story: StoryGraph) -> None:
    """Create a complete Streamlit story game application.
    
    Args:
        story: Story graph to create app for
    """
    # Initialize game state
    current_state_id = initialize_game_state(story)
    current_state = story.get_state(current_state_id)
    
    if not current_state:
        st.error(f"Invalid game state: {current_state_id}")
        return
    
    # Display header
    display_game_header(story)
    
    # Display sidebar
    display_game_sidebar(story, current_state_id)
    
    # Display breadcrumbs
    visited_list = list(st.session_state.visited_states)
    display_breadcrumbs(visited_list, story)
    
    # Display current state
    if current_state.is_terminal:
        display_terminal_state(current_state, story)
    else:
        display_story_state(current_state)
        
        # Handle action choices
        selected_target = display_action_choices(current_state)
        
        if selected_target:
            handle_state_transition(selected_target, story)
