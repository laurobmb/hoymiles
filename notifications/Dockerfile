FROM python:3.12-bookworm

RUN pip install playwright && \
    playwright install --with-deps
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV USUARIO=user
ENV SENHA=1qasdcz

CMD ["python", "app.py"]
