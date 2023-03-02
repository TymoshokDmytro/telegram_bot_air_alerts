FROM python:3.8-buster as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

FROM python:3.8-slim-buster
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app /app_workdir/app
WORKDIR /app_workdir

CMD ["python", "-m", "app.main"]
