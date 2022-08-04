import pyperclip
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path


def local_css(file_name: Path) -> None:
    with open(file_name) as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


def on_copy_button_click(text: str):
    """Copy text to clipboard

    Args:
        text (str): Text to be copied
    """
    # pyperclip.copy(text)
    pass


def auto_copy(text: str) -> None:
    """automatically copies text to clipboard"""
    pyperclip.copy(text)


def generate_tweet_share(text: str) -> None:
    """Generate twitter share button"""

    html_str = f"""<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
        data-text="'{text}' - Speak like Stuart the Minion" 
        data-url="https://www.minions.fun"
        data-show-count="false">
        data-size="Large" 
        data-hashtags="minions, translate, streamlit"
        Tweet
        </a>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""
    components.html(html_str)
