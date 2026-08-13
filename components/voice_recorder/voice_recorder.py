import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))

voice_recorder = components.declare_component(
    "voice_recorder",
    path=_COMPONENT_DIR
)

def speech_to_text(key=None):
    return voice_recorder(
        key=key,
        default=None
    )