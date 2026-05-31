# Plan de Mitigación de Incidentes Operacionales — PharmaGo

Framework basado en Atlassian Incident Management.

---

## Severidades

| Nivel | Nombre | Criterio | Tiempo de respuesta |
|---|---|---|---|
| P1 | Crítico | Sistema completamente caído o breach de seguridad | < 5 min |
| P2 | Alto | Feature principal degradada, > 10% usuarios afectados | < 15 min |
| P3 | Medio | Feature secundaria degradada, < 10% usuarios afectados | < 1 hora |
| P4 | Bajo | Issue de rendimiento menor o cosmético | < 1 día |

---

## Fase 1: Detección

### Fuentes de detección

| Fuente | Señal | Herramienta |
|---|---|---|
| Métricas | Error rate > 5%, latencia p95 > 2s, CPU > 80% | Grafana (alertas automáticas) |
| Pods | CrashLoopBackOff, OOMKilled, pod no Ready | K8s eventos + Grafana |
| Logs | Excepciones no controladas, connection errors | Kibana → índice `pharmago-*` |
| Trazas | Spans con error, latencia anómala end-to-end | Jaeger UI |
| Usuarios | Reporte de error desde la aplicación | Canal de soporte |

### Alertas configuradas en Grafana

1. **CPU alta en pod**: `rate(container_cpu_usage_seconds_total{namespace="pharmago"}[5m]) > 0.8`
2. **Memoria alta**: `container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.85`
3. **Error rate HTTP**: `rate(pharmago_http_errors_total[2m]) / rate(pharmago_http_requests_total[2m]) > 0.05`
4. **Latencia p95 alta**: `histogram_quantile(0.95, rate(pharmago_http_request_duration_milliseconds_bucket[5m])) > 2000`
5. **Pod reiniciado**: `increase(kube_pod_container_status_restarts_total{namespace="pharmago"}[10m]) > 3`

---

## Fase 2: Respuesta

### Roles

| Rol | Responsabilidad |
|---|---|
| **Incident Commander (IC)** | Coordina la respuesta, comunica estado, toma decisiones |
| **Ingeniero de turno** | Diagnóstico técnico y aplicación de fixes |
| **Comunicaciones** | Notifica a usuarios y stakeholders si P1/P2 |

### Pasos inmediatos al detectar un incidente

```bash
# 1. Verificar el estado general del cluster
kubectl get pods -n pharmago

# 2. Identificar pods problemáticos
kubectl get pods -n pharmago | grep -v Running

# 3. Clasificar la severidad (P1–P4) según la tabla de arriba

# 4. Abrir canal de incidente (ej: Slack #incidents)
#    Template: "Incidente P[X]: [descripción breve]. IC: [nombre]. ETA diagnóstico: [tiempo]"
```

---

## Fase 3: Mitigación

### Runbooks por tipo de falla

#### CrashLoopBackOff

```bash
# Ver qué está fallando
kubectl describe pod <pod-name> -n pharmago
kubectl logs <pod-name> -n pharmago --previous --tail=50

# Causas comunes:
#   - SQL Server no disponible → verificar pharmago-db
#   - Variable de entorno faltante → revisar ConfigMap/Secret
#   - OOMKilled → incrementar memory limit

# Mitigación inmediata: escalar otras réplicas mientras se investiga
kubectl scale deployment <deployment> --replicas=2 -n pharmago
```

#### OOMKilled (Out of Memory)

```bash
# Confirmar causa
kubectl describe pod <pod-name> -n pharmago | grep -A 5 "OOMKilled"

# Mitigación inmediata: incrementar límite de memoria
kubectl patch deployment <deployment> -n pharmago \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"<container>","resources":{"limits":{"memory":"768Mi"}}}]}}}}'
```

#### Circuit Breaker abierto (Polly)

```bash
# Verificar en logs de Kibana:
# Buscar: "circuit breaker" O "BrokenCircuitException"

# El circuito se abre cuando el servicio destino falla 5 veces consecutivas.
# Espera 30 segundos y se cierra automáticamente (half-open).

# Si el servicio destino está caído:
kubectl get pods -n pharmago | grep <servicio-destino>
kubectl logs <pod-name> -n pharmago --previous
```

#### Base de datos no disponible

```bash
# Verificar estado del StatefulSet
kubectl get pods -n pharmago | grep pharmago-db
kubectl logs pharmago-db-0 -n pharmago

# Si el pod está caído, K8s lo reinicia automáticamente (liveness probe).
# Si el PVC tiene problemas:
kubectl get pvc -n pharmago
kubectl describe pvc pharmago-db-pvc -n pharmago
```

#### Pod no pasa readinessProbe

```bash
# Ver el endpoint de salud directamente
kubectl port-forward <pod-name> 8080:80 -n pharmago &
curl http://localhost:8080/health

# Ver eventos
kubectl describe pod <pod-name> -n pharmago | grep -A 20 Events
```

---

## Fase 4: Resolución

### Proceso estándar

1. **Fix** — aplicar el cambio en el código o configuración
2. **Build** — construir nueva imagen: `docker build -t pharmago-<servicio>:fix .`
3. **Deploy** — rolling update: `kubectl set image deployment/<deploy> <container>=pharmago-<servicio>:fix -n pharmago`
4. **Validación** — verificar en Grafana que métricas vuelven a valores normales
5. **Cierre** — actualizar el canal de incidente: "Incidente resuelto. Causa: [X]. Fix: [Y]."

### Rollback de emergencia

```bash
# Volver a la versión anterior inmediatamente
kubectl rollout undo deployment/<deployment> -n pharmago
kubectl rollout status deployment/<deployment> -n pharmago
```

---

## Fase 5: Post-mortem

### Plantilla de post-mortem

```markdown
## Post-mortem: [Título del incidente]

**Fecha:** [fecha]
**Severidad:** P[X]
**Duración:** [inicio] → [fin] ([total] minutos)
**IC:** [nombre]

### Impacto
[Qué funcionalidad se vio afectada y cuántos usuarios]

### Timeline
| Hora | Evento |
|------|--------|
| HH:MM | Alerta disparada en Grafana |
| HH:MM | IC asignado |
| HH:MM | Causa raíz identificada |
| HH:MM | Fix aplicado |
| HH:MM | Incidente resuelto |

### Causa raíz
[Descripción técnica detallada de qué falló y por qué]

### Qué funcionó bien
- [mecanismo que ayudó, ej: "Circuit Breaker evitó cascading failure"]
- [ej: "Alertas de Grafana detectaron el problema antes que los usuarios"]

### Qué falló
- [ej: "El runbook no tenía el comando para el caso de OOMKilled"]

### Acciones preventivas
| Acción | Responsable | Fecha límite |
|--------|-------------|--------------|
| [acción concreta] | [nombre] | [fecha] |
```

---

## URLs de herramientas en Minikube

| Herramienta | URL | Credenciales |
|---|---|---|
| Grafana | `http://$(minikube ip):30300` | admin / admin |
| Kibana | `http://$(minikube ip):30601` | — |
| Jaeger | `http://$(minikube ip):30686` | — |
| Prometheus | `http://$(minikube ip):30900` | — |
