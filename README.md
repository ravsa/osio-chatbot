# osio-chatbot

## Create a virtualenv
```bash
    virtualenv -p python3 --no-site-packages --clear venv
```

## Install the requirements
```bash
    pip install -r requirements.txt
```
```bash
    python -m spacy download en_core_web_md
    python -m spacy link en_core_web_md en
    python -m spacy download en
```

## tool for generate training data

```bash
    npm i -g rasa-nlu-trainer
    rasa-nlu-trainer -v <path to the training data file>
```
