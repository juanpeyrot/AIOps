# Despliegues Seguros — Rolling Update

## Técnica elegida: Rolling Update

### Por qué Rolling Update y no Blue-Green o Canary

| Técnica | Ventajas | Desventajas | ¿Por qué no? |
|---|---|---|---|
| **Rolling Update** | Nativa de K8s, sin infraestructura extra, fácil rollback | Tráfico dividido brevemente entre versiones | — Elegida |
| Blue-Green | Rollback instantáneo, sin mezcla de versiones | Duplica recursos (costo) | Requiere el doble de pods activos |
| Canary | Control fino de porcentaje de tráfico | Requiere ingress avanzado (Nginx/Istio) | Complejidad innecesaria para el alcance |

**Rolling Update con `maxUnavailable: 0` es equivalente a Blue-Green** en términos de disponibilidad, sin el costo extra de recursos.

## Configuración en los Deployments

Todos los microservicios de backend tienen esta estrategia:

```yaml
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0   # Nunca hay menos pods Ready que las réplicas configuradas
      maxSurge: 1         # K8s puede crear 1 pod extra durante el rollout
```

### Cómo funciona paso a paso

Con `replicas: 1`, `maxUnavailable: 0`, `maxSurge: 1`:

```
Estado inicial:   [pod-v1 READY]

Paso 1 (surge):   [pod-v1 READY] [pod-v2 Starting]   ← se crea el pod nuevo

Paso 2 (wait):    [pod-v1 READY] [pod-v2 READY]       ← se espera que pase readinessProbe

Paso 3 (remove):  [pod-v2 READY]                      ← se baja el pod viejo

En ningún momento hay 0 pods Ready → 100% de disponibilidad garantizada.
```

## Cómo hacer un deploy

```bash
# Opción A: cambiar la imagen (deploy de nueva versión)
kubectl set image deployment/pharmago-users-service \
  pharmago-users-service=pharmago-users-service:v2 \
  -n pharmago

# Opción B: forzar reinicio (mismo image tag)
kubectl rollout restart deployment/pharmago-users-service -n pharmago

# Monitorear el progreso
kubectl rollout status deployment/pharmago-users-service -n pharmago
```

## Verificación de 0% downtime

Mientras se hace el rollout, ejecutar en una terminal separada:

```bash
GATEWAY_URL=$(minikube service pharmago-api-gateway -n pharmago --url)

while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/health" 2>/dev/null)
  echo "$(date '+%H:%M:%S') → HTTP $STATUS"
  sleep 0.5
done
```

Si todos los códigos son `200` durante el rollout, el despliegue fue sin downtime.

## Rollback

```bash
# Volver a la versión anterior inmediatamente
kubectl rollout undo deployment/pharmago-users-service -n pharmago

# Ver historial de versiones
kubectl rollout history deployment/pharmago-users-service -n pharmago

# Volver a una versión específica
kubectl rollout undo deployment/pharmago-users-service --to-revision=2 -n pharmago
```

## Comandos útiles durante un deploy

```bash
# Ver el estado de todos los pods en tiempo real
kubectl get pods -n pharmago -w

# Ver eventos del deployment
kubectl describe deployment pharmago-users-service -n pharmago | grep -A 10 Events

# Ver los logs del pod nuevo durante el arranque
kubectl logs -f -l app=pharmago-users-service -n pharmago
```
