---
name: docker-compose-monitoring-stack
description: "Deploys a complete monitoring stack with Prometheus, Grafana, and Node Exporter using Docker Compose."
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---

# Docker Compose Monitoring Stack

Deploys a complete monitoring stack with Prometheus, Grafana, and Node Exporter using Docker Compose.

## Execution Context

This skill runs inside **Deep Agents CLI** (v0.0.34+). Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `write_file` | Create docker-compose.yml, prometheus.yml, Grafana provisioning files, .env, .gitignore |
| `execute` | Run Docker Compose commands, verify services, run health checks |
| `read_file` | Read configuration files to verify content |
| `write_todos` | Track execution plan progress |
| `http_request` | Test service health endpoints |

**Critical execution rules:**
1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never try to generate everything at once.
3. Test each service via `execute` immediately after starting it.
4. Use `task` to delegate long or parallel subtasks to sub-agents.

## Execution Plan (use with `write_todos`)

When receiving the request, run `write_todos` with:

- [ ] 1. Verify Docker and Docker Compose are installed
- [ ] 2. Check and set required environment variables
- [ ] 3. Create project directory structure
- [ ] 4. Create docker-compose.yml
- [ ] 5. Create Prometheus configuration
- [ ] 6. Create Grafana datasource provisioning
- [ ] 7. Create Grafana dashboard provisioning and dashboard JSON
- [ ] 8. Create .env and .gitignore files
- [ ] 9. Create AGENTS.md with stack documentation
- [ ] 10. Start the stack with Docker Compose
- [ ] 11. Run health checks on all services

## When to Use

Use this skill when the user asks to:
- Set up monitoring or observability
- Deploy Prometheus and Grafana
- Create a monitoring stack
- Set up metrics collection
- Create a Grafana dashboard for infrastructure

## Prerequisites Check

Before creating any files, use `execute` to verify:

```bash
# Check Docker
docker --version || { echo "ERROR: Docker not found. Install from https://docs.docker.com/get-docker/"; exit 1; }

# Check Docker Compose
docker compose version || { echo "ERROR: Docker Compose not found"; exit 1; }

# Check if Docker daemon is running
docker info >/dev/null 2>&1 || { echo "ERROR: Docker daemon is not running"; exit 1; }

echo "All prerequisites OK"
```

If Docker is not installed, advise the user to follow the official installation guide at https://docs.docker.com/get-docker/.

## Environment Setup

Before execution, verify required environment variables via `execute`:

```bash
# Check required variables
for var in GRAFANA_ADMIN_PASSWORD; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

# Check optional variables (with defaults)
echo "PROMETHEUS_RETENTION=${PROMETHEUS_RETENTION:-15d} (default: 15d)"

echo "All environment variables OK"
```

If using a `.env` file, load it via `execute`:

```bash
set -a && source .env && set +a
```

**Security note:** Never hardcode secrets in the SKILL.md. Use environment variables or a `.env` file (added to `.gitignore`).

## Steps

### 1. Create Project Structure

Use `execute` to create the directory structure:

```bash
mkdir -p monitoring/{prometheus,grafana/provisioning/datasources,grafana/provisioning/dashboards,grafana/dashboards}
```

Test via `execute`:

```bash
ls -R monitoring/ && echo "Directory structure OK"
```

### 2. Create Docker Compose File

Use `write_file` to create `monitoring/docker-compose.yml`:

```yaml
version: "3.8"
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION:-15d}'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro

volumes:
  prometheus_data:
  grafana_data:
```

Test via `execute`:

```bash
cd monitoring && docker compose config --quiet && echo "docker-compose.yml syntax OK"
```

### 3. Create Prometheus Configuration

Use `write_file` to create `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 4. Create Grafana Datasource Provisioning

Use `write_file` to create `monitoring/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

### 5. Create Grafana Dashboard Provisioning

Use `write_file` to create `monitoring/grafana/provisioning/dashboards/dashboards.yml`:

```yaml
apiVersion: 1
providers:
  - name: 'default'
    folder: ''
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

Use `write_file` to create `monitoring/grafana/dashboards/node-exporter.json`:

Create a basic Node Exporter dashboard JSON. Use the official Grafana dashboard ID 1860 as reference.

### 6. Create Environment and Ignore Files

Use `write_file` to create `monitoring/.env`:

```
GRAFANA_ADMIN_PASSWORD=changeme
PROMETHEUS_RETENTION=15d
```

Use `write_file` to create `monitoring/.gitignore`:

```
.env
*_data/
```

### 7. Add Project Notes

Use `write_file` to create `monitoring/AGENTS.md`:

```markdown
# Monitoring Stack — Project Notes

## Architecture
- **Prometheus** (port 9090): Metrics collection and storage
- **Grafana** (port 3000): Visualization and dashboards
- **Node Exporter** (port 9100): Host-level metrics

## Credentials
- Grafana login: admin / value of $GRAFANA_ADMIN_PASSWORD

## Data Persistence
- Data persists in Docker volumes even after `docker compose down`
- To fully reset: `docker compose down -v`

## Platform Notes
- On macOS, Node Exporter has limited metrics (/proc and /sys are not real Linux filesystems)
- On Linux, Node Exporter works fully
```

### 8. Start the Stack

Use `execute` to start all services:

```bash
cd monitoring
set -a && source .env && set +a
docker compose up -d
```

Use `execute` to verify all containers are running:

```bash
cd monitoring && docker compose ps
```

### 9. Run Health Checks

### Platform-specific execution

Use `execute` to detect the platform and warn about limitations:

```bash
OS=$(uname -s)
case "$OS" in
  Darwin) echo "WARNING: macOS detected — Node Exporter metrics will be limited (/proc and /sys are not real Linux filesystems)" ;;
  Linux)  echo "Linux detected — all metrics available" ;;
  *)      echo "WARNING: Unsupported OS: $OS — Node Exporter may not work correctly" ;;
esac
```

Use `execute` to test each service:

```bash
echo "=== Prometheus Health ==="
curl -sf http://localhost:9090/-/healthy && echo " OK" || echo " FAILED"

echo "=== Grafana Health ==="
curl -sf http://localhost:3000/api/health && echo " OK" || echo " FAILED"

echo "=== Node Exporter Metrics ==="
curl -sf http://localhost:9100/metrics | head -5 && echo "... OK" || echo " FAILED"

echo "=== All health checks complete ==="
```

For each service that fails the health check, use `execute` to inspect logs:

```bash
cd monitoring && docker compose logs <service-name>
```

## Notes

- Grafana default login: admin / value of `$GRAFANA_ADMIN_PASSWORD`
- Prometheus UI: http://localhost:9090
- Grafana UI: http://localhost:3000
- Data persists in Docker volumes even after `docker compose down`
- To fully reset: `docker compose down -v`

## Usage with Deep Agents CLI

### Mode 1 — Build (one-shot)
```bash
deepagents -y "Deploy a monitoring stack with Prometheus and Grafana following the docker-compose-monitoring-stack skill"
```

### Mode 2 — Interactive
```bash
deepagents
> Set up a monitoring stack with Prometheus, Grafana, and Node Exporter
```

### Mode 3 — Non-interactive (CI/CD)
```bash
deepagents -n -y -S "docker,curl,mkdir" "Deploy monitoring stack with Prometheus, Grafana, and Node Exporter"
```

## Troubleshooting

### Docker not found
```bash
# Check:
docker --version
# Install: follow https://docs.docker.com/get-docker/
```

### Docker Compose not found
```bash
# Check:
docker compose version
# If using older Docker, install compose plugin:
sudo apt-get install docker-compose-plugin
```

### Docker daemon not running
```bash
# Check:
docker info
# Start (Linux):
sudo systemctl start docker
# Start (macOS): open Docker Desktop app
```

### Grafana fails health check
```bash
# Check logs:
cd monitoring && docker compose logs grafana
# Verify password is set:
echo $GRAFANA_ADMIN_PASSWORD
# Restart:
docker compose restart grafana
```

### Prometheus fails health check
```bash
# Check logs:
cd monitoring && docker compose logs prometheus
# Validate config syntax:
docker run --rm -v $(pwd)/prometheus:/etc/prometheus prom/prometheus promtool check config /etc/prometheus/prometheus.yml
```

### Node Exporter metrics incomplete on macOS
```
This is expected. On macOS, /proc and /sys are not real Linux filesystems,
so Node Exporter cannot collect full host metrics. For full metrics,
deploy on a Linux host or use Docker Desktop's VM metrics.
```

### Environment variable not set
```bash
# Check what's set:
env | grep -E "GRAFANA|PROMETHEUS"
# Set manually:
export GRAFANA_ADMIN_PASSWORD="your-secure-password"
export PROMETHEUS_RETENTION="15d"
# Or load from .env:
set -a && source .env && set +a
```

### Context window overflow
```
Use /compact to force compaction before continuing.
Consider splitting the task with `task` sub-agents.
```
