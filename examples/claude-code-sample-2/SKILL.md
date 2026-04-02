# Skill: Docker Compose Monitoring Stack

> Deploys a complete monitoring stack with Prometheus, Grafana, and Node Exporter using Docker Compose.

---

## When to use

When the user asks to set up monitoring, observability, metrics collection, or a Grafana dashboard for their infrastructure.

---

## Steps

Check if Docker and Docker Compose are installed. If not, install Docker following the official docs.

Set the following environment variables:
- `$GRAFANA_ADMIN_PASSWORD` — admin password for Grafana
- `$PROMETHEUS_RETENTION` — how long to keep metrics (default: 15d)

Create the project structure:

```bash
mkdir -p monitoring/{prometheus,grafana/provisioning/datasources,grafana/provisioning/dashboards,grafana/dashboards}
```

Create the file `monitoring/docker-compose.yml`:

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

Create `monitoring/prometheus/prometheus.yml`:

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

Create the Grafana datasource provisioning file `monitoring/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

Create a basic Node Exporter dashboard JSON at `monitoring/grafana/dashboards/node-exporter.json`. Use the official Grafana dashboard ID 1860 as reference.

Create the Grafana dashboard provisioning file `monitoring/grafana/provisioning/dashboards/dashboards.yml`:

```yaml
apiVersion: 1
providers:
  - name: 'default'
    folder: ''
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

Add a `.env` file with:
```
GRAFANA_ADMIN_PASSWORD=changeme
PROMETHEUS_RETENTION=15d
```

Add project notes to `CLAUDE.md` documenting the stack architecture.

Start everything:

```bash
cd monitoring
docker compose up -d
```

Verify all containers are running: `docker compose ps`

Test each service:

```bash
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:3000/api/health
curl -s http://localhost:9100/metrics | head -5
```

If on macOS, note that Node Exporter has limited metrics because `/proc` and `/sys` are not real Linux filesystems. On Linux it works fully.

For each service that fails the health check, check the logs with `docker compose logs {service}` and fix the issue.

---

## Notes

- Grafana default login: admin / value of `$GRAFANA_ADMIN_PASSWORD`
- Prometheus UI: http://localhost:9090
- Grafana UI: http://localhost:3000
- Data persists in Docker volumes even after `docker compose down`
- To fully reset: `docker compose down -v`
