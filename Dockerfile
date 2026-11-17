FROM node:24-bookworm-slim AS webui-builder

WORKDIR /app
COPY webui/package.json webui/package-lock.json ./webui/
WORKDIR /app/webui
RUN npm ci
COPY webui/ ./
COPY packages/client-events/ /app/packages/client-events/
COPY nujinagent/channels/ /app/nujinagent/channels/
RUN mkdir -p /app/nujinagent/web && npm run build

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl git bubblewrap openssh-client libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Keep the runtime environment writable by the non-root nujinagent user. Enabled
# channels may install their manifest-declared dependencies at startup.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv venv --seed "$VIRTUAL_ENV"

ARG NUJINAGENT_EXTRAS=
COPY pyproject.toml ./
RUN set -- && \
    for extra in $(printf '%s' "$NUJINAGENT_EXTRAS" | tr ',' ' '); do \
        set -- "$@" --extra "$extra"; \
    done && \
    uv pip install --python "$VIRTUAL_ENV/bin/python" --no-cache -r pyproject.toml "$@"

COPY README.md LICENSE THIRD_PARTY_NOTICES.md hatch_build.py ./
COPY docs/ docs/
COPY nujinagent/ nujinagent/
COPY scripts/install_channel_dependencies.py scripts/
COPY --from=webui-builder /app/nujinagent/web/dist/ nujinagent/web/dist/
RUN NUJINAGENT_SKIP_WEBUI_BUILD=1 uv pip install --python "$VIRTUAL_ENV/bin/python" --no-cache --no-deps .

ARG NUJINAGENT_CHANNELS=whatsapp
RUN for channel in $(printf '%s' "$NUJINAGENT_CHANNELS" | tr ',' ' '); do \
        python -m scripts.install_channel_dependencies "$channel"; \
    done

# Render deploy template (see render.yaml): committed gateway config that wires
# secrets through ${ANTHROPIC_API_KEY} / ${NUJINAGENT_WEB_TOKEN} env vars (resolved
# at startup). Lives in the code dir (/app), not the data dir, so a mounted disk
# won't shadow it. Only used when RENDER=true; ignored by local runs.
COPY render-config.json ./

RUN useradd -m -u 1000 -s /bin/bash nujinagent && \
    mkdir -p /home/nujinagent/.nujinagent && \
    chown -R nujinagent:nujinagent /home/nujinagent /app/.venv

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

# Start as root so the entrypoint can chown the data dir (on Render, the
# freshly-mounted root-owned persistent disk) before dropping to the non-root
# nujinagent user via setpriv. The entrypoint drops privileges on every root start
# and fails closed if it cannot, so the agent never runs as root (see
# entrypoint.sh).
USER root
ENV HOME=/home/nujinagent
# Ensure crash output reaches Render logs (app output is otherwise swallowed on
# non-graceful exit).
ENV PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1

EXPOSE 18790 8765

ENTRYPOINT ["entrypoint.sh"]
CMD ["status"]
