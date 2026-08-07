FROM python:3.12-slim

WORKDIR /app

COPY requirements-py312.txt /tmp/requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["bash"]
