export function linearManifestUrl(
  publicBaseUrl: string,
  webhookPath: string,
  callbackPath: string,
): string {
  const manifest = {
    $schema: "https://linear.app/.well-known/oauth-app-manifest.schema.json",
    schemaVersion: "1.0.0",
    distribution: "private",
    display: {
      description: "Mention or delegate issues to nujinagent as a native Linear agent.",
      iconUrl: "https://raw.githubusercontent.com/HKUDS/nujinagent/main/images/nujinagent_logo.png",
    },
    developer: { name: "nujinagent" },
    oauth: {
      client_name: "nujinagent Agent",
      client_uri: "https://github.com/HKUDS/nujinagent",
      redirect_uris: [`${publicBaseUrl}${callbackPath}`],
      grant_types: ["authorization_code"],
    },
    webhook: {
      enabled: true,
      url: `${publicBaseUrl}${webhookPath}`,
      resourceTypes: [
        "AgentSessionEvent",
        "PermissionChange",
        "OAuthAuthorization",
      ],
    },
  };
  return `https://linear.app/settings/api/applications/new?${new URLSearchParams({
    manifest: JSON.stringify(manifest),
  })}`;
}
