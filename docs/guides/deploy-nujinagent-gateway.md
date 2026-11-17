# How to Deploy a Long-Running nujinagent AI Agent Gateway

The nujinagent gateway is the long-running self-hosted AI agent process that keeps WebUI sessions, chat apps, automations, local triggers, heartbeat jobs, Dream, and WebSocket delivery online.

## What you will build

- a verified nujinagent config
- a gateway process
- a service or container deployment path with Docker, systemd, or macOS LaunchAgent

## When to use this

Use this when nujinagent should keep running after a single CLI turn. Chat apps, browser sessions, background automations, local triggers, and server-side integrations all depend on a live gateway.

## Start from your current setup

If nujinagent already replies in the WebUI, its gateway is already running. To keep it alive after closing the launcher, close the foreground launcher and start the same instance in background mode:

```bash
nujinagent gateway --background
nujinagent gateway status
nujinagent gateway logs
```

Run `nujinagent webui` when you need to return to the browser; it attaches to the running gateway. Do not run a second foreground gateway for the same instance.

For a new host, choose one setup path:

- **Docker:** follow [container initialization and verification](../deployment.md#docker-compose). It creates the config and checks the model inside the container; a host nujinagent installation is unnecessary.
- **Host installation:** follow the [quick start](../quick-start.md). On a headless machine, use `nujinagent onboard --wizard`, then `nujinagent agent -m "Hello!"` to check the selected model.

## Keep the gateway running

Background mode keeps the current process alive; for automatic startup after reboot and restart on failure, choose [Docker Compose](../deployment.md#docker-compose), a [systemd user service](../deployment.md#linux-service), or a [macOS LaunchAgent](../deployment.md#macos-launchagent). Use the same config and workspace as the successful model check. Stop a manually managed gateway before starting a service for that instance.

For foreground diagnosis only:

```bash
nujinagent gateway --verbose
```

## Production notes

- Docker Compose is the most repeatable Linux container path.
- systemd user services are useful for Linux user-level gateway deployments.
- macOS LaunchAgent keeps the gateway alive after login.
- Persist the active config directory's `sessions/` folder together with the workspace (including `.nujinagent/workspace-id`), memory files, channel login state, and generated artifacts.
- Restart the gateway after editing `config.json`.

## Security notes

- Plan ports before exposing services. Gateway health defaults to `18790`, and WebUI/WebSocket defaults to `8765`.
- Protect shared WebUI access with a WebSocket token. The health endpoint has no authentication; keep its published port on loopback or behind a restricted monitoring interface.
- Keep chat access control intentional before deploying.
- Use Docker or Linux sandboxing when shell tools are enabled for unattended work.

## Troubleshooting

- Use the same `--config` and `--workspace` flags for status checks and service startup.
- Check logs with `docker compose logs`, `journalctl`, LaunchAgent logs, or `nujinagent gateway --verbose`.
- If Docker port publishing does not work, confirm the service is not bound only to container loopback.

## Related nujinagent docs

- [Deployment](../deployment.md)
- [Multiple Instances](../multiple-instances.md)
- [Configuration](../configuration.md)
