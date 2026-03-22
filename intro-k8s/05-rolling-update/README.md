# Rolling Update y Rollback

```bash
kubectl apply -f deployment.yaml
```

## Estrategia de rollout
El deployment usa `strategy.rollingUpdate` con:
- **maxSurge: 1** — máximo 1 pod extra sobre el deseado (crea uno nuevo antes de borrar)
- **maxUnavailable: 0** — no derriba pods hasta que el nuevo esté Ready (cero downtime)

## Observar estado inicial
```bash
kubectl get pods -l app=nginx -o wide
kubectl rollout status deployment/nginx-deploy
```

## Hacer rolling update (cambiar imagen)

**Terminal 1** — dejar el watch corriendo:
```bash
kubectl get pods -l app=nginx -w
```

**Terminal 2** — ejecutar el cambio:
```bash
kubectl set image deployment/nginx-deploy nginx=nginx:1.25
```

En la terminal 1 verás cómo los pods se reemplazan uno a uno (Terminating → ContainerCreating → Running) sin downtime.

## Ver historial de revisiones
```bash
kubectl rollout history deployment/nginx-deploy
kubectl rollout history deployment/nginx-deploy --revision=2
```

## Rollback a la revisión anterior
```bash
kubectl rollout undo deployment/nginx-deploy
```

Verificar: `kubectl get pods -l app=nginx` — vuelven a nginx:1.24

## Limpieza
```bash
kubectl delete -f deployment.yaml
```
