FROM python:3.9

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r /requirements.txt


COPY ./minion_translate /minion_translate
RUN mkdir -p /minion_translate/.streamlit
COPY .streamlit/config.toml /minion_translate/.streamlit/config.toml
COPY .streamlit/secrets.toml /minion_translate/.streamlit/secrets.toml

WORKDIR /minion_translate
EXPOSE 8501

CMD streamlit run app.py