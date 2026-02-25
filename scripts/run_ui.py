"""Launch command helper for the Streamlit demo UI."""

from pathlib import Path


def main() -> None:
    app = Path("src/recovery_project/ui/streamlit_app.py")
    print("Run this command:")
    print(f"streamlit run {app}")


if __name__ == "__main__":
    main()
