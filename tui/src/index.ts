import type { NujinAgentTui as App, AppOptions } from "./app"
import { desktopConnectionSource } from "./platform/desktop"

if (process.argv.slice(2).join(" ") === "--render-mermaid") {
  const { runDiagramWorker } = await import("./rendering/mermaid/worker")
  await runDiagramWorker()
  process.exit(0)
}
if (process.argv.slice(2).join(" ") === "--desktop-protocol") {
  process.stdout.write("1\n")
  process.exit(0)
}
// Initialize OpenTUI before the UI graph: compiled async cycles otherwise expose an
// uninitialized CliRenderer binding. Raster children never enter this graph.
await import("@opentui/core")
const { NujinAgentTui, sessionExitMessage } = await import("./app")
const desktop = desktopConnectionSource()

// Keep in sync with _TUI_DETACH_EXIT_CODE in nujinagent/cli/tui_launcher.py.
const TUI_DETACH_EXIT_CODE = 90

function themePreference(): AppOptions["theme"] {
  const value = process.env.NUJINAGENT_TUI_THEME?.trim() || "auto"
  if (value === "auto" || value === "dark" || value === "light") return value
  throw new Error("NUJINAGENT_TUI_THEME must be auto, dark, or light")
}

const workspace = process.env.NUJINAGENT_TUI_WORKSPACE?.trim() || ""
const bootstrapUrl = process.env.NUJINAGENT_TUI_BOOTSTRAP_URL?.trim() || ""
const wsUrl = process.env.NUJINAGENT_TUI_WS_URL?.trim() || ""
const healthUrl = process.env.NUJINAGENT_TUI_HEALTH_URL?.trim() || ""
const gatewayStopCommand = process.env.NUJINAGENT_TUI_GATEWAY_STOP_COMMAND?.trim()
  || "nujinagent gateway stop"
if (!desktop && !bootstrapUrl && !wsUrl) {
  throw new Error("NUJINAGENT_TUI_BOOTSTRAP_URL or NUJINAGENT_TUI_WS_URL is required")
}
const options: AppOptions = {
  ...(desktop ? { resolveConnection: desktop.resolve, desktopGatewayId: desktop.gatewayId } : bootstrapUrl
    ? {
        bootstrapUrl,
        bootstrapSecret: process.env.NUJINAGENT_TUI_BOOTSTRAP_SECRET?.trim() || "",
        healthUrl: healthUrl || undefined,
      }
    : { wsUrl }),
  apiUrl: process.env.NUJINAGENT_TUI_API_URL?.trim() || "",
  apiToken: process.env.NUJINAGENT_TUI_API_TOKEN?.trim() || "",
  chatId: process.env.NUJINAGENT_TUI_CHAT_ID?.trim() || undefined,
  model: process.env.NUJINAGENT_TUI_MODEL?.trim() || "unknown model",
  modelPreset: process.env.NUJINAGENT_TUI_MODEL_PRESET?.trim() || "default",
  workspace,
  version: process.env.NUJINAGENT_TUI_VERSION?.trim() || "dev",
  access: process.env.NUJINAGENT_TUI_ACCESS?.trim() || "workspace access",
  theme: themePreference(),
  onDetach: (chatId) => {
    process.exitCode = TUI_DETACH_EXIT_CODE
    process.stdout.write("Detached; the agent continues in the background.\n")
    if (!desktop && chatId) process.stdout.write(sessionExitMessage(chatId))
    process.stdout.write(desktop ? "Desktop remains running. Reconnect with nujinagent.\n" : `Stop it with: ${gatewayStopCommand}\n`)
  },
  onExit: (chatId) => {
    process.stdout.write(desktop ? "Disconnected from Desktop; its backend remains running.\n" : sessionExitMessage(chatId))
  },
}

let app: App | undefined
let shuttingDown = false

const shutdown = (code = 0) => {
  if (shuttingDown) return
  shuttingDown = true
  app?.stop()
  process.exitCode = code
}

for (const signal of ["SIGHUP", "SIGINT", "SIGTERM"] as const) {
  process.once(signal, () => shutdown())
}
process.once("exit", () => app?.stop())
process.once("uncaughtException", (error) => {
  shutdown(1)
  process.stderr.write(desktop ? "Desktop terminal connection failed. No backend was started.\n" : `${error instanceof Error ? error.stack || error.message : String(error)}\n`)
})
process.once("unhandledRejection", (error) => {
  shutdown(1)
  process.stderr.write(desktop ? "Desktop terminal connection failed. No backend was started.\n" : `${error instanceof Error ? error.stack || error.message : String(error)}\n`)
})

app = await NujinAgentTui.create(options)
if (shuttingDown) app.stop()
else await app.start()
