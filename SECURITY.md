# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.1.x   | Yes       |
| 2.0.x   | Security patches only |
| < 2.0   | No        |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

If you discover a security vulnerability in this project (e.g., the installer downloading from a compromised source, secrets leaking through converted skills, or shell injection in `install.sh`), please report it responsibly:

1. **Email:** Send details to the maintainer via GitHub private messaging or the email listed on the [@andersonamaral2](https://github.com/andersonamaral2) profile.
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 7 days
- **Fix or mitigation:** Within 30 days for critical issues

## Scope

This policy covers:
- `install.sh` — shell injection, insecure downloads, path traversal
- `SKILL.en.md` / `SKILL.pt.md` — conversion rules that could produce insecure output
- Example files — hardcoded secrets or credentials

## Secure Practices in This Project

- `install.sh` uses `set -euo pipefail` (strict bash mode)
- All downloads use HTTPS
- No secrets are hardcoded in any tracked file
- Example `.env` files contain only placeholder values
- Converted skills include security notes about never hardcoding secrets
