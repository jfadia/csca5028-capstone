FROM ghcr.io/astral-sh/uv:0.10.4-python3.12-trixie

COPY src/ /src/
WORKDIR /src

RUN uv sync --locked
ENV PATH=".venv/bin:$PATH"

CMD ["uv", "run", "python", "app.py"]