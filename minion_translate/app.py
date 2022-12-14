import datetime
import hashlib
import logging
import pickle
import re
import string
from fnmatch import translate
from pathlib import Path
from typing import Dict, Tuple

import nltk
import numpy as np
import streamlit as st
from google.cloud import firestore
from nltk.tokenize import word_tokenize
from PIL import Image
from utils import auto_copy, generate_tweet_share, local_css


logging.basicConfig(filename="translate.log")


css_path = Path(__file__).parent.resolve() / "style.css"
minion_image_path = Path(__file__).parent.resolve() / "images" / "minions.png"
gru_image_path = Path(__file__).parent.resolve() / "images" / "gru.png"
min2eng_path = Path(__file__).parent.resolve() / "data" / "min2eng_lower.pkl"
eng2min_path = Path(__file__).parent.resolve() / "data" / "eng2min_lower.pkl"
nltk_path = Path(__file__).parent.resolve() / "data" / "nltk_data"
nltk.data.path.append(str(nltk_path))
local_css(css_path)

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_info(st.secrets["firestore_key"])


# Create a reference to the Google post.
eng2min_collection = db.collection("eng2min")
min2eng_collection = db.collection("min2eng")
count_eng2min_doc = db.collection("count").document("eng2min")
count_min2eng_doc = db.collection("count").document("min2eng")

# Then get the data at that reference.
st.markdown("<h1 style='text-align: center; color: white;'>Minion Translator</h1>", unsafe_allow_html=True)
# st.title("Minion Translator")
tab1, tab2 = st.tabs(["Minionize", "Humanize"])


@st.cache(persist=True)
def load_images(gru_image_path, minion_image_path):
    gru_image = Image.open(str(gru_image_path))
    minion_image = Image.open(str(minion_image_path))
    return minion_image, gru_image


@st.cache(persist=True)
def load_data(min2eng_path: Path, eng2min_path: Path) -> Tuple[Dict, Dict]:
    """_summary_

    Args:
        min2eng_path (str): _description_
        eng2min_path (str): _description_

    Returns:
        _type_: _description_
    """
    with open(str(min2eng_path), "rb") as f:
        min2eng = pickle.load(f)
    with open(str(eng2min_path), "rb") as f:
        eng2min = pickle.load(f)

    return eng2min, min2eng


eng2min, min2eng = load_data(min2eng_path=min2eng_path, eng2min_path=eng2min_path)
minion_image, gru_image = load_images(minion_image_path=minion_image_path, gru_image_path=gru_image_path)


def translate(text: str, oracle: Dict, use_nltk=False) -> str:
    """Function to translate english to minion language

    Args:
        text (str): text to be translated
        oracle (Dict): Oracle Dictionary

    Returns:
        _type_: _description_
    """
    if use_nltk:
        words = word_tokenize(text.lower().strip())
    else:
        words = re.findall(r"[\w']+|[.,!?;]", text.lower().strip())
    translated = []
    for word in words:
        if word in oracle:
            translated.append(oracle[word])
        else:
            translated.append(word)
    translated_text = "".join(
        [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in translated]
    ).strip()

    return translated_text


if "minionize_count" not in st.session_state:
    st.session_state.minionize_count = count_eng2min_doc.get().get("num")
    st.session_state.min_count_delta = 0
if "humanize_count" not in st.session_state:
    st.session_state.humanize_count = count_min2eng_doc.get().get("num")
    st.session_state.hum_count_delta = 0
if "output_text_min" not in st.session_state:
    st.session_state.output_text_min = ""
if "output_text_eng" not in st.session_state:
    st.session_state.output_text_eng = ""


def on_input_text_eng_change() -> None:
    translated = ""
    eng_text = st.session_state["input_text_eng"].lower().strip()
    logging.debug(f"input:eng2min:: {eng_text}")
    translated = translate(eng_text, eng2min)
    # auto_copy(translated)
    logging.debug(f"translated:eng2min:: {translated}")
    st.session_state["output_text_min"] = translated
    doc_name = hashlib.sha1(translated.encode("utf-8")).hexdigest()
    doc = eng2min_collection.document(doc_name)
    data = {"eng": eng_text, "min": translated, "created": datetime.datetime.now()}
    doc.set(data)
    st.session_state.minionize_count += 1
    st.session_state.min_count_delta += 1
    count_eng2min_doc.set({"num": st.session_state.minionize_count, "updated": datetime.datetime.now()})


def on_input_text_min_change() -> None:
    """callback function for translating minion language to english"""

    translated = ""
    min_text = st.session_state["input_text_min"]
    hashed_input = hashlib.sha1(min_text.encode("utf-8")).hexdigest()
    if eng2min_collection.document(hashed_input).get().exists:
        translated = eng2min_collection.document(hashed_input).get().get("eng")
    else:
        translated = translate(min_text, min2eng)
    # auto_copy(translated)
    logging.debug(f"input:min2eng:: {min_text}")
    logging.debug(f"translated:min2eng:: {translated}")
    st.session_state["output_text_eng"] = translated
    doc_name = hashlib.sha1(translated.encode("utf-8")).hexdigest()
    doc = min2eng_collection.document(doc_name)
    data = {"eng": translated, "min": input_text_stuart, "created": datetime.datetime.now()}
    doc.set(data)
    st.session_state.humanize_count += 1
    st.session_state.hum_count_delta += 1
    count_min2eng_doc.set({"num": st.session_state.humanize_count, "updated": datetime.datetime.now()})


with tab1:
    st.image(
        minion_image,
        caption=None,
        width=300,
        use_column_width=None,
        clamp=False,
        channels="RGB",
        output_format="auto",
    )
    minion_names = ["Bob", "Kevin", "Stuart", "Dave", "Jerry"]
    input_text_eng = st.text_area(
        f" Gru Says",
        value="",
        height=None,
        max_chars=200,
        key="input_text_eng",
        help="English text to be translated",
        on_change=None,
    )

    translate_button = st.button(
        f"Minionize",
        key="minionize_button",
        help=None,
        on_click=on_input_text_eng_change,
        args=None,
    )

    output_text_min = st.text_area(
        f"{minion_names[np.random.randint(5)]} Says",
        value="",
        height=None,
        max_chars=200,
        key="output_text_min",
        help="Minioniized text",
        on_change=None,
        args=None,
    )

    # if translate_button:
    #   st.caption("Output copied, please paste and share!", unsafe_allow_html=False)
    if "output_text_min" in st.session_state:
        generate_tweet_share(st.session_state.output_text_min)
    else:
        generate_tweet_share("Bello!")

    st.metric(label="Minionize Stats", value=st.session_state.minionize_count, delta=st.session_state.min_count_delta)

with tab2:
    st.image(
        gru_image,
        caption=None,
        width=200,
        use_column_width=None,
        clamp=False,
        channels="RGB",
        output_format="auto",
    )

    input_text_stuart = st.text_area(
        "Stuart Says",
        value="",
        height=None,
        max_chars=200,
        key="input_text_min",
        help="Minionized text",
        on_change=None,
    )

    translate_button = st.button(
        "Humanize", key="humanize_button", help=None, on_click=on_input_text_min_change, args=None
    )

    output_text_eng = st.text_area(
        f" Gru Says",
        value="",
        height=None,
        max_chars=200,
        key="output_text_eng",
        help="English text",
        on_change=None,
        args=None,
    )
    # if translate_button:
    #   st.caption("Output copied, please paste and share!", unsafe_allow_html=False)
    if "input_text_min" in st.session_state:
        generate_tweet_share(st.session_state.input_text_min)
    else:
        generate_tweet_share("Bello!")

    st.metric(label="Humanize Stats", value=st.session_state.humanize_count, delta=st.session_state.hum_count_delta)
