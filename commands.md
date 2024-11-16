# Commands

## venv

Referencia: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

venvdir: Folder donde .venv se encuentra.
### Commands

Load environment:
```
.\<venvdir>/Scripts/Activate.ps1
cd <botdir> python bot.py
```

## Uvicorn

¿Cómo correr uvicorn (y el API) localmente?:

```
uvicorn main:app --reload --env-file .env
```

¿Cómo correr uvicorn en Heroku?:

En Procfile:

```
web: uvicorn main:app --host=0.0.0.0 --port=${PORT}
```

## ngrok (pruebas locales)

¿Cómo ejecutar ngrok?

```
ngrok http 8000
```

## Crear lista de requerimientos

```
pip install pipreqs
pipreqs --force --ignore ".venv, .vscode, __pycache__"
```

## Iniciar aplicación (Heroku)
```
 heroku ps:scale web=1 --app tango-bot
 heroku maintenance:off --app tango-bot
```

## Detener aplicación (Heroku)
```
 heroku ps:scale web=0 --app tango-bot
 heroku maintenance:on --app tango-bot
```