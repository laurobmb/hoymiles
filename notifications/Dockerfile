FROM python:3.12-bookworm

RUN pip install playwright && \
    playwright install --with-deps

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

ENV USUARIO='user1'
ENV SENHA='pass123'
ENV CHAT_ID='-xxxxx'
ENV DEBUG=0
ENV TOKEN='TOKEN'
ENV STATUS_COLETA_LOCAL=0

CMD ["python", "app.py"]
