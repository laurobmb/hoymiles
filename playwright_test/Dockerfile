FROM python:3.12-bookworm

RUN pip install playwright==@1.42.0 && \
    playwright install --with-deps

WORKDIR /app
COPY . .
ENV USUARIO=user
ENV SENHA=1qasdcz

CMD ["python", "app.py"]
