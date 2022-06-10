FROM python:3

WORKDIR /usr/src/app

RUN pip install python-telegram-bot
RUN pip install pymongo


COPY . .
COPY primerpdf.pdf .
CMD [ "python", "./bot_nike.py" ]
