# bot-tango

## Description

This Telegram bot was made as part of @fernanda-una and @fmadrian's ["Web-based application development (EIF509)" project (FlorArte)](https://www.github.com/fmadrian/florarte) and it allows clients to authenticate themselves, see their information, get suggestions about products, place orders, and search previous orders they made.

## What is it made with?

This Telegram bot was made with Python, python-telegram-bot, and MongoDB which helps to handle some of the user's information. The information stored in the database helps to determine if users are authenticated, and what they are trying to order.

## Features

- Login, logout, and check their authentication status.
- Ask an AI assistant about product suggestions based on tags or categories, and placing orders.
- Place and get a list of orders they have made.

## AI Assistant

The AI assistant is available in both [web client](https://github.com/una-eif509-desarrolloweb-24G01/frontend-tango) and Telegram bot. It uses [OpenAI's API](https://platform.openai.com/docs/overview) to help customers: 
- Get recommendations of what products (which are offered/available in the catalog) to buy according to their needs.
- Place orders.

## Requirements

Before running the bot, you **must have** the following requirements: 
1. Clone the [bot](https://github.com/fmadrian/bot-tango) repository.
2. Create a MongoDB database **named** **==sessions==**.
3. [Create a Telegram Bot and obtain a token](https://core.telegram.org/bots/tutorial).
4. Download and run ngrok **using the port 8000**.

#### Local deployment
1. Switch to the [main](https://github.com/una-eif509-desarrolloweb-24G01/frontend-tango/) branch.

2. Run the following command:
```
uvicorn main:app --env-file .env
```
3. Create an .env file and add the following variables:
```
UVICORN_TELEGRAM_BOT_TOKEN=<telegram_token>

UVICORN_WEBHOOK_HOST=<ngrok_host>

UVICORN_MONGODB_CONNECTION_STRING=<mongodb_connection_string>

UVICORN_API_URL=<tango_api_url>
```
#### Remote deployment using Heroku
1. Switch to [heroku](https://github.com/fmadrian/bot-tango/tree/heroku) branch.
2. Deploy this branch on [Heroku](https://www.heroku.com/python). 
3. **Take every variable defined in .env and add it as an environment variable in Heroku**.


## Screenshots

Getting a recommendation using the bot
![Getting a recommendation using the bot](https://raw.githubusercontent.com/fmadrian/florarte/refs/heads/main/images/8.png)
Placing an order using the bot.
![Placing an order using the bot](https://raw.githubusercontent.com/fmadrian/florarte/refs/heads/main/images/10.png)
Viewing order placed using the bot and AI assistant.
![Viewing order placed using bot and AI assistant](https://raw.githubusercontent.com/fmadrian/florarte/refs/heads/main/images/15.png)
