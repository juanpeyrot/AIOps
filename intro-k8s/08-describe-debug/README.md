# kubectl describe como herramienta de debugging

```bash
kubectl apply -f pod.yaml
```

## describe de un pod sano
```bash
kubectl describe pod nginx-healthy
```

Revisar secciones:
- **Events** — qué hizo el scheduler, kubelet, etc.
- **Conditions** — Ready, ContainersReady
- **State** — Running, Waiting, Terminated

## Probar describe con un pod problemático
```bash
kubectl apply -f pod-pending.yaml
kubectl describe pod pod-pending
```

En **Events** verás el motivo del Pending (p. ej. "Insufficient cpu", "Insufficient memory").

## Comandos útiles para debugging
```bash
# Eventos del namespace
kubectl get events --sort-by='.lastTimestamp'

# Describe de un pod que falla
kubectl describe pod -l app=crash
```

## Limpieza
```bash
kubectl delete -f pod.yaml -f pod-pending.yaml
```
