# PharmaGo — AIOps

Sistema de gestión de farmacias desplegado sobre Kubernetes con observabilidad completa (métricas, trazas y logs).

## Prerrequisitos

- Docker 24.x+
- kubectl 1.28+
- Minikube 1.32+ con driver **qemu2**
- .NET 8 SDK (solo si se recompila el backend)

## Levantar el proyecto

### 1. Iniciar el cluster

```bash
minikube start --cpus=4 --memory=6144 --disk-size=25g --driver=qemu2
minikube addons enable metrics-server
```

> Con menos de 4 CPUs o 6 GB de RAM los pods quedan en `Pending`.

### 2. Construir las imágenes

```bash
cd "Implementacion K8S/Codigo/k8s"
bash build-images.sh
```

Construye y carga en Minikube: `pharmago-users-service`, `pharmago-pharmacy-service`, `pharmago-api-gateway` y `pharmago-ui`.

### 3. Desplegar

```bash
bash apply-k8s.sh
```

Despliega en orden: namespace → secrets → configmaps → volúmenes → base de datos → observabilidad → backend → frontend. El script espera automáticamente a que la base de datos y Elasticsearch estén listos.

### 4. Esperar a que todo esté listo

```bash
kubectl get pods -n pharmago -w
```

Esperar hasta que los 13 pods estén en estado `1/1 Running`. Tarda entre 2 y 5 minutos en el primer arranque.

### 5. Exponer los servicios

```bash
# Si el puerto 9200 está ocupado (Docker Compose u otro Elasticsearch):
ES_LOCAL_PORT=19200 bash port-forward.sh

# En caso contrario:
bash port-forward.sh

# Para detener todos los port-forwards:
bash port-forward.sh --stop
```

## URLs de acceso

| Servicio      | URL                              | Credenciales         |
|---------------|----------------------------------|----------------------|
| Frontend      | <http://127.0.0.1:4200>          | —                    |
| API Gateway   | <http://127.0.0.1:5000>          | —                    |
| Grafana       | <http://127.0.0.1:3000>          | admin / admin        |
| Prometheus    | <http://127.0.0.1:9090>          | —                    |
| Jaeger        | <http://127.0.0.1:16686>         | —                    |
| Kibana        | <http://127.0.0.1:5601>          | —                    |
| Elasticsearch | <http://127.0.0.1:9200>          | —                    |
| SQL Server    | 127.0.0.1,11433                  | sa / Str0ngP@ssword! |

## Apagar el cluster

```bash
minikube stop
```

Para eliminarlo por completo:

```bash
minikube delete
```
