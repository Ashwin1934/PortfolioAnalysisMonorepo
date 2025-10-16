# Valuation Dashboard - React Frontend

## October 16, 2025

- **Built with React 18** - Two buttons with click handlers that log to console (ready for future FastAPI integration)
- **Dockerized deployment** - Multi-stage build (Node for building, Nginx for serving) on port 3000
- **Apache reverse proxy** - Accessible at `http://[server-ip]/valuation-dashboard` from any device on local network
- **Subpath configuration** - `package.json` includes `"homepage": "/valuation-dashboard"` for proper asset loading
- **Network path** - Laptop → Router → Windows Server (Apache port 80) → Docker container (port 3000) → Nginx → React app

## Build

```bash
docker build -t home-server-ui .
```