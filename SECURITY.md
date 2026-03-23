# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly via
[GitHub Security Advisories](https://github.com/osisdie/codedrill-mock-interview/security/advisories/new).

**Please do not open a public issue for security concerns.**

We will acknowledge your report within 48 hours and aim to provide a fix or
mitigation within 7 days for confirmed issues.

## Security Model

### Code Execution Sandbox

User-submitted code runs in an isolated environment with:

- **Process isolation** — each execution runs in a separate subprocess
- **Resource limits** — configurable timeout (default 10s) and memory cap (default 256 MB)
- **No network access** — sandboxed code cannot make outbound connections
- **No filesystem writes** — execution environment is read-only

### API Security

- CORS is restricted to configured origins
- API keys are stored server-side only and never exposed to the frontend
- No user authentication data is stored (stateless sessions)
