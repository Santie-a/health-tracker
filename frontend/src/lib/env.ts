import "server-only";

/**
 * Server-only environment access. The gateway URL and token live here and must
 * never reach the client bundle — importing this module from a Client Component
 * is a build error (`server-only`).
 *
 * Resilience: misconfiguration should be obvious. `gatewayUrl()` throws a clear
 * error if unset (fail fast), mirroring the gateway's "fail fast at startup"
 * stance. The token is allowed to be empty (gateway auth disabled in dev).
 */

export function gatewayUrl(): string {
  const url = process.env.GATEWAY_URL?.trim();
  if (!url) {
    throw new Error(
      "GATEWAY_URL is not set. Copy .env.example to .env.local and point it at the gateway.",
    );
  }
  return url.replace(/\/+$/, ""); // no trailing slash
}

export function gatewayToken(): string {
  return process.env.GATEWAY_TOKEN?.trim() ?? "";
}
