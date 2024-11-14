# Commands

## Running venv

Reference: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

venvdir: Directory where venv is located.
botdir: Directory where the bot entry point is located.

### Commands

Load environment:
```
.\<venvdir>/Scripts/Activate.ps1
cd <botdir> python bot.py
```

## Running uvicorn

How to run uvicorn (locally):

```
uvicorn main:app --reload --env-file config.env
```

How to run uvicorn (remotely):

```
uvicorn main:app --env-file config.env
```

## Running ngrok

How to run ngrok:

```
ngrok http 8000
```

## Create requirements list

```
pip install pipreqs
pipreqs --force --ignore ".venv, .vscode, __pycache__"
```