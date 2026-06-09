import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a self-contained server bundle (.next/standalone) so the Docker image can run
  // `node server.js` without node_modules. Required by the Dockerfile's runner stage.
  output: "standalone",
};

export default nextConfig;
