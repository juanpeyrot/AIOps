# Informe Final — Obligatorio AIOps (PharmaGo)

**Equipo:** 275075 · 220264 · 270077
**Repositorio:** https://github.com/juanpeyrot/AIOps (rama `feature/obligatorio-aiops-275075-220264-270077`)

Este informe tiene una sección por cada elemento de la rúbrica, describiendo los
desafíos enfrentados y los resultados obtenidos. PharmaGo es una aplicación de
gestión de farmacias en .NET (UI Angular, API Gateway YARP, dos microservicios y
SQL Server) sobre la que se implementaron prácticas de SRE/AIOps.

---

## 1. Implementación de plataforma (Kubernetes)

**Qué se hizo.** Toda la aplicación corre sobre Kubernetes (Minikube). Cada
microservicio ejecuta en un **Deployment independiente**: `pharmago-ui`,
`pharmago-api-gateway`, `pharmago-users-service`, `pharmago-pharmacy-service`,
`pharmago-db`, más la pila de observabilidad (OTel Collector, Prometheus, Grafana,
Jaeger, Elasticsearch, Kibana, Fluent Bit, node-exporter). El diagrama de
despliegue está en `docs/deployment-diagram.md`.

**Desafíos.** El dimensionamiento del cluster: con 2 CPUs los pods quedaban en
`Pending` por *Insufficient cpu*. Se recreó Minikube con 4 CPUs / 6 GB.

**Resultado.** 13 pods en estado `Running`, cada microservicio aislado en su
Deployment, con sus Services y PersistentVolumes. Despliegue reproducible vía
`build-images.sh` + `apply-k8s.sh`.

## 2. Alta disponibilidad

**Qué se hizo.** Tres mecanismos combinados:
- **Auto-curación**: `startup`, `readiness` y `liveness probes` en todos los pods;
  el Deployment controller recrea cualquier réplica que falle, devolviéndola al
  estado `READY`.
- **Circuit Breaker** (Polly) en los HttpClients entre microservicios: abre el
  circuito tras 5 fallas consecutivas y espera 30 s, con 3 reintentos y backoff
  exponencial — mitiga el alto volumen de solicitudes fallidas.
- **Rate limiting** por IP/usuario en el API Gateway.

**Desafíos.** Elegir el patrón de resiliencia y aplicarlo solo a errores
transitorios (`HandleTransientHttpError`) para no enmascarar fallas reales.

**Resultado.** Ante la caída de un servicio dependiente, el circuito se abre y
evita el fallo en cascada; al restaurarse, K8s recupera las réplicas
automáticamente. Verificable con `chaos-engineering/component-disconnect.sh`.

## 3. Despliegues seguros

**Qué se hizo.** Estrategia **Rolling Update** con `maxUnavailable: 0` y
`maxSurge: 1` en los Deployments de backend: K8s levanta el pod nuevo y espera que
pase `readinessProbe` antes de bajar el viejo, garantizando 100 % de
disponibilidad. Documentado en `docs/safe-deployments.md` (incluye comparación con
Blue-Green/Canary y comandos de rollback).

**Desafíos.** Garantizar que nunca haya menos pods `READY` que las réplicas
configuradas durante una actualización.

**Resultado.** Un `kubectl rollout restart` con un loop de `curl` en paralelo
devuelve únicamente códigos `200`. Rollback inmediato con `kubectl rollout undo`.

## 4. Telemetría

**Qué se hizo.**
- **Logs estructurados en JSON** (`StructuredLogger`) → Fluent Bit → Elasticsearch
  (índice `pharmago-logs-*`) → consultables en Kibana.
- **Trazas OTLP**: se agregó el pipeline `WithTracing` (ASP.NET Core + HttpClient)
  en los tres servicios, exportando por OTLP al OTel Collector y de ahí a **Jaeger**.
- **Métricas** recolectadas vía OTLP hacia Prometheus y visualizadas en Grafana,
  con ≥5 métricas de cada tipo: 6 de aplicación, ≥5 de contenedor (cAdvisor) y ≥5
  de nodo físico (node-exporter: CPU, memoria, storage, red).
- **5 alertas en Grafana** provisionadas como código (`grafana-alerting.yaml`):
  CPU de contenedor, memoria de contenedor, error rate HTTP, latencia p95 y
  memoria de nodo.

**Desafíos.** (a) Construir el pipeline de trazas de punta a punta. (b) Prometheus
entró en `OOMKilled` tras horas de operación → se subió el límite de memoria a
1 Gi y se corrigió el RBAC (`watch`). (c) Un apagado sucio del VM corrompió la base
SQLite de Grafana; como datasources, dashboards y alertas están provisionados como
código, bastó eliminar `grafana.db` y Grafana se reconstruyó solo.

**Resultado.** Métricas, trazas, logs y 5 alertas activas y verificadas (las
reglas evalúan y disparan correctamente).

## 5. Técnicas de detección de anomalías

**Qué se hizo.** Dos notebooks no supervisados en `notebooks/`:
`isolation_forest.ipynb` (**Isolation Forest**) y `svm_anomaly_detection.ipynb`
(**One-Class SVM**). Cada uno incluye EDA, preprocesamiento (`StandardScaler`),
entrenamiento, visualización (PCA 2D, distribución de scores) y evaluación
(precision/recall/F1, matriz de confusión, ROC AUC).

**Desafíos.** Los datasets son provistos por los docentes y aún no estaban
disponibles. Se construyó un **dataset sintético reproducible** de métricas
operacionales (CPU, memoria, latencia, error rate, red) con 5 % de anomalías
inyectadas; la celda de carga está aislada para swappear el dataset real sin tocar
el resto del pipeline.

**Resultado (dataset sintético).**

| Modelo | F1 (anomalía) | ROC AUC |
|--------|---------------|---------|
| Isolation Forest | 1.00 | 1.000 |
| One-Class SVM | 0.73 | 0.981 |

Isolation Forest separa mejor las anomalías en este dataset; One-Class SVM es más
sensible a la escala y a `nu`. Ambos se evalúan con las mismas métricas para
permitir la comparación.

## 6. Plan de contención de incidentes operacionales

**Qué se hizo.** `docs/incident-management-plan.md` implementa todas las fases del
**framework de Atlassian** (*Detect → Respond → Recover → Learn*, con comunicación
transversal): detección (alertas Grafana, Kibana, probes), respuesta (roles,
canal de incidente, severidades P1–P4 con SLAs), mitigación (runbooks para
CrashLoopBackOff, OOMKilled, circuit breaker abierto, DB caída), resolución y
post-mortem (plantilla con causa raíz, timeline y acciones preventivas).

**Desafíos.** Mapear las fases nombradas de Atlassian a runbooks accionables y
concretos del stack de PharmaGo.

**Resultado.** Plan completo y operativo, con comandos `kubectl` reales por tipo
de incidente.

## 7. Scripts de caos

**Qué se hizo.** Seis scripts en `chaos-engineering/` que cubren los seis tipos
requeridos: inyección de requests (`load-requests.sh`), sobrecarga de CPU
(`cpu-spike.sh`), de memoria (`ram-spike.sh`), de storage (`volume-spike.sh`),
interrupción de tráfico de red (`network-disruption.sh`) y desconexión de
componentes (`component-disconnect.sh`).

**Desafíos.** La imagen de runtime (`aspnet:6.0`) no incluye `tc` (iproute2), por
lo que el script de red fallaba. Se reescribió usando un **contenedor efímero
`netshoot`** (`kubectl debug --profile=netadmin`) que comparte el network
namespace del pod y aporta `tc` con capability `NET_ADMIN`, sin modificar la imagen
de producción.

**Resultado.** Los seis scripts ejecutan correctamente y su efecto es observable en
Grafana (CPU/memoria/latencia/errores) y en la respuesta del sistema.

## 8. Defensa (war-room)

**Preparación.** Guión de demostración: (1) sistema sano en Grafana →
(2) `component-disconnect.sh` apaga PharmacyService y se observa el Circuit Breaker
en los logs → (3) restauración y auto-curación de K8s → (4) `cpu-spike.sh` dispara
el spike y la alerta de CPU → (5) Rolling Update en vivo con loop de `curl`
mostrando solo `200`. Telemetría lista: Grafana (métricas + alertas), Kibana
(logs), Jaeger (trazas).

**Cómo los mecanismos garantizan el comportamiento.** Probes + Deployment ⇒
auto-curación; Circuit Breaker ⇒ contención de fallas en cascada; Rolling Update ⇒
cero downtime; telemetría ⇒ visibilidad del incidente en tiempo real.

---

## Reflexión sobre prácticas ágiles

El trabajo se realizó de forma incremental, con commits pequeños y verificables por
objetivo y todo versionado en GitHub (fork del proyecto base). Cada cambio se
validó end-to-end contra el cluster antes de avanzar, lo que permitió detectar
temprano problemas operativos reales (OOMKilled de Prometheus, corrupción de
Grafana) y resolverlos como incidentes — el mismo ciclo *detectar → mitigar →
aprender* que documenta el plan de incidentes. La infraestructura como código
(manifests K8s, alertas y provisioning de Grafana) hizo que el entorno fuera
reproducible y resiliente a fallas.
