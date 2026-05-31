# Diagrama de Despliegue — PharmaGo en Kubernetes

## Arquitectura de componentes

```mermaid
graph TD
    Browser["Browser\nhttp://localhost:30080"] --> Frontend["Deployment: pharmago-ui\nAngular + nginx\nNodePort 30080"]

    Frontend --> ApiGateway["Deployment: pharmago-api-gateway\nYARP Reverse Proxy\nNodePort 30000"]

    ApiGateway -->|/api/users/**| UsersService["Deployment: pharmago-users-service\n.NET 6 · replicas: 1\nClusterIP :80"]
    ApiGateway -->|/api/drug/**\n/api/pharmacy/**| PharmacyService["Deployment: pharmago-pharmacy-service\n.NET 6 · replicas: 1\nClusterIP :80"]

    UsersService -->|HTTP + Circuit Breaker| PharmacyService
    PharmacyService -->|HTTP + Circuit Breaker| UsersService

    UsersService --> DB["StatefulSet: pharmago-db\nSQL Server 2019\nClusterIP :1433"]
    PharmacyService --> DB

    subgraph Observabilidad
        UsersService -->|OTLP gRPC| OTelCollector["Deployment: otlp-collector\nClusterIP :4317"]
        PharmacyService -->|OTLP gRPC| OTelCollector
        ApiGateway -->|OTLP gRPC| OTelCollector

        OTelCollector -->|métricas| Prometheus["Deployment: pharmago-prometheus\nClusterIP :9090\nNodePort 30900"]
        OTelCollector -->|trazas| Jaeger["Deployment: pharmago-jaeger\nClusterIP :4317\nNodePort 30686 (UI)"]

        Prometheus --> Grafana["Deployment: pharmago-grafana\nNodePort 30300"]

        NodeExporter["DaemonSet: node-exporter\nnodo físico: CPU, RAM, disco, red"] --> Prometheus
    end

    subgraph Logging
        FluentBit["DaemonSet: fluent-bit\nlee /var/log/containers/"] -->|logs JSON| Elasticsearch["Deployment: pharmago-elasticsearch\nClusterIP :9200"]
        Elasticsearch --> Kibana["Deployment: pharmago-kibana\nNodePort 30601"]
    end
```

## Namespace

Todos los componentes corren en el namespace `pharmago`.

## Tabla de servicios y puertos

| Componente | Tipo K8s | Puerto interno | Puerto externo (NodePort) |
|---|---|---|---|
| pharmago-ui | Deployment | 80 | 30080 |
| pharmago-api-gateway | Deployment | 80 | 30000 |
| pharmago-users-service | Deployment | 80 | — (ClusterIP) |
| pharmago-pharmacy-service | Deployment | 80 | — (ClusterIP) |
| pharmago-db | StatefulSet | 1433 | — (ClusterIP) |
| otlp-collector | Deployment | 4317, 8889 | — (ClusterIP) |
| pharmago-prometheus | Deployment | 9090 | 30900 |
| pharmago-grafana | Deployment | 3000 | 30300 |
| pharmago-jaeger | Deployment | 4317, 16686 | 30686 (UI) |
| pharmago-elasticsearch | Deployment | 9200 | — (ClusterIP) |
| pharmago-kibana | Deployment | 5601 | 30601 |
| node-exporter | DaemonSet | 9100 | — (ClusterIP) |
| fluent-bit | DaemonSet | — | — |

## Flujo de datos

### Métricas
```
Servicios .NET → OTLP gRPC → otlp-collector → Prometheus scrape :8889 → Grafana
Node Exporter → Prometheus scrape :9100 → Grafana
```

### Trazas
```
Servicios .NET → OTLP gRPC → otlp-collector → Jaeger (UI: puerto 30686)
```

### Logs
```
Servicios .NET → stdout (JSON) → Fluent Bit (DaemonSet) → Elasticsearch → Kibana (puerto 30601)
```

## Estrategia de despliegue

Todos los Deployments de microservicios usan **Rolling Update** con:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```
Esto garantiza 0% de downtime durante actualizaciones: K8s levanta el pod nuevo antes de bajar el viejo.

## Resiliencia

- **Health probes**: todos los pods tienen `startupProbe`, `readinessProbe` y `livenessProbe` en `/health`
- **Self-healing**: si un pod falla, el Deployment controller lo reinicia automáticamente
- **Circuit Breaker**: UsersService y PharmacyService usan Polly para cortar llamadas tras 5 fallas, evitando cascading failures
