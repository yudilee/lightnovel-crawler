##
# Web assets
##
FROM node:alpine AS node

WORKDIR /app/lncrawl-web
COPY lncrawl-web/package.json package.json
COPY lncrawl-web/yarn.lock yarn.lock
RUN yarn

RUN mkdir -p ../lncrawl
COPY lncrawl-web .
RUN yarn build

##
# Application
##
FROM python:3.10-slim-bookworm AS runner

# Install general dependencies
RUN apt-get update -yq \
    && apt-get install -yq \
    wget tar xz-utils make cmake g++ libffi-dev libegl1 libopengl0 libxcb-cursor0 \
    libnss3 libgl1-mesa-glx libxcomposite1 libxrandr2 libxi6 fontconfig \
    libxkbcommon-x11-0 libxtst6 libxkbfile1 libxcomposite-dev libxdamage-dev \
    && apt-get clean autoclean \
    && apt-get autoremove -yq \
    && rm -rf /var/lib/apt/lists/*

# Install calibre
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin \
    && ln -s /opt/calibre/ebook-convert /usr/local/bin/ebook-convert

# Install uv and upgrade pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv pip install --system -U pip

WORKDIR /app

# Install requirements
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Copy sources
COPY sources sources
COPY lncrawl lncrawl

# Copy web assets
COPY --from=node /app/lncrawl/server/web lncrawl/server/web

# Custom data path
ENV LNCRAWL_DATA_PATH=/data

ENTRYPOINT [ "python", "-m", "lncrawl" ]
