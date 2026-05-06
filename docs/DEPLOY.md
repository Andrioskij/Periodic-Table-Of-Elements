# Deploying the web app

The browser version under `web/` is a Reflex app. The Python backend
serves the WebSocket connection that drives the UI; the Next.js
frontend bundle (produced by `reflex export`) is statically served
from `:3000`. Any host that can run a long-lived Python process and
expose two ports — or a single Docker container — is a valid target.

Three deploy targets are documented below, in recommended order. If
you only want the short version: **use Reflex Hosting** unless you
already operate the alternative.

## 1. Reflex Hosting (recommended)

Operated by the Reflex team. Bundles backend and frontend as one app
and handles SSL, custom domains, and rolling deploys.

- Free tier: yes (single small app, no credit card required at sign-up).
- Setup time: ~5 minutes.
- Vendor lock-in: low — you can migrate to fly.io / Render any time
  by reusing `web/Dockerfile`.

```bash
cd web
reflex login                                  # opens browser, OAuth via GitHub
reflex deploy --project periodic-table-web    # first run: choose region
```

After the first deploy, subsequent updates are `reflex deploy` from
the same directory. The CLI reads `rxconfig.py` and uploads the
project tree, so make sure `.dockerignore` (in repo root) is up to
date — Reflex Hosting honours the same exclude list.

Docs: <https://reflex.dev/docs/hosting/deploy-quick-start/>

## 2. fly.io

Container host with a generous free allowance and a single config
file. Reuses `web/Dockerfile` directly — no separate build pipeline.

- Free tier: yes (3 shared-cpu-1x machines, 3 GB volume).
  Requires a payment method on file even for the free allowance.
- Setup time: ~15 minutes (DNS + first deploy).
- Vendor lock-in: low — the image is portable.

```bash
# from repo root, not from web/ — the Dockerfile expects the repo
# context (it copies src/ and data/ at build time).
fly launch --no-deploy --copy-config --dockerfile web/Dockerfile
fly deploy
```

Sample `fly.toml` (place in repo root):

```toml
app = "periodic-table-web"
primary_region = "ams"

[build]
  dockerfile = "web/Dockerfile"

[[services]]
  internal_port = 3000
  protocol = "tcp"
  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[services]]
  internal_port = 8000
  protocol = "tcp"
  [[services.ports]]
    port = 8000
    handlers = ["tls"]
```

The two services are required because Reflex serves the prerendered
frontend on `:3000` and the WebSocket backend on `:8000`. Both must
be reachable from the visitor's browser; if you front fly with a CDN
that only forwards 443, set `API_URL` in the build args (see
`web/Dockerfile`) to the public hostname so the frontend connects to
the backend correctly.

Docs: <https://fly.io/docs/launch/>

## 3. Render

Web-service host with GitHub integration and one-click redeploys on
push. Reuses `web/Dockerfile`.

- Free tier: yes for static sites; the Reflex backend needs a paid
  service (~$7/month for the cheapest tier as of 2026).
- Setup time: ~10 minutes (connect repo + first build).
- Vendor lock-in: low.

In the Render dashboard:

1. **New → Web Service**, point at this repository.
2. **Runtime**: Docker.
3. **Dockerfile path**: `web/Dockerfile`.
4. **Docker context**: `.` (repo root — same constraint as fly).
5. **Health check path**: `/`.
6. **Plan**: Starter ($7/month) for the backend.

Optional: pair with a free Render static site that serves the
exported frontend bundle (`reflex export --frontend-only --no-zip`)
and a separate small Render service for the backend, but that
doubles the moving parts and is rarely worth it.

Docs: <https://render.com/docs/web-services>

## Choosing between them

| Concern | Reflex Hosting | fly.io | Render |
|---|---|---|---|
| Free tier covers the app | Yes | Yes (with CC on file) | No (paid backend) |
| Steps to first deploy | 2 commands | 4 commands + DNS | UI clicks + first build |
| You own the container | No | Yes | Yes |
| Vendor lock-in | Low (still portable) | None | None |
| Best for | Quickest path to a public URL | Self-hosters who already use fly | Teams already on Render |

If you have no preference and want the public URL today, go with
Reflex Hosting. Switch later if the app grows or you want to
co-locate it with other infrastructure.

## Common snags

- **Build context** — the Dockerfile assumes the repo root, not
  `web/`, because it copies `src/` and `data/` at build time. Always
  build/deploy from the repo root or pass an explicit context.
- **Two ports** — :3000 (frontend) and :8000 (backend WebSocket).
  Hosts that expose only one port (e.g. naive Cloud Run) need extra
  routing; Reflex Hosting and fly handle both out of the box.
- **`API_URL`** — when frontend and backend are on different
  hostnames (CDN in front, custom domain), set `API_URL` at build
  time so the frontend code knows where to open the WebSocket.
  Default is `http://localhost:8000` which only works in dev.
- **Cold starts** — Render's free tier sleeps after 15 minutes of
  inactivity; first request after that takes ~30 seconds. Reflex
  Hosting and fly do not sleep on the free tier as of writing.
