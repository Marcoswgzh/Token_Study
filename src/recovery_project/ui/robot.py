#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

from pathlib import Path
import json
import streamlit as st

def _strip_lottie_background(animation: dict) -> dict:
    """Remove static pale background layers from the current robot Lottie."""
    layers = animation.get("layers")
    if not isinstance(layers, list) or len(layers) < 2:
        return animation

    filtered: list[dict] = []
    for idx, layer in enumerate(layers):
        if (
            idx >= len(layers) - 2
            and layer.get("ty") == 4
            and layer.get("nm") in {"Layer 1", "Layer 2"}
        ):
            continue
        filtered.append(layer)
    animation["layers"] = filtered
    return animation

@st.cache_data(show_spinner=False)
def _load_lottie() -> dict | None:
    candidates = [
        Path("cute_robot.json"),
        Path(Path(__file__).parent / "cute_robot.json")
    ]
    for path in candidates:
        if path.exists():
            try:
                animation = json.loads(path.read_text(encoding="utf-8"))
                return _strip_lottie_background(animation)
            except json.JSONDecodeError:
                return None
    return None
