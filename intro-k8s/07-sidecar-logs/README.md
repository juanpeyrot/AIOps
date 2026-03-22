# Logs multi-contenedor / Sidecar

```bash
kubectl apply -f pod.yaml
```

## Ver logs de un contenedor específico
```bash
# Logs del contenedor main
kubectl logs sidecar-pod -c main

# Logs del contenedor sidecar
kubectl logs sidecar-pod -c sidecar
```

## Logs por defecto (sin -c)
```bash
# Sin -c → muestra logs del primer contenedor
kubectl logs sidecar-pod
```

## Seguir logs en vivo
```bash
kubectl logs -f sidecar-pod -c main
```

## Listar contenedores del pod
```bash
kubectl get pod sidecar-pod -o jsonpath='{.spec.containers[*].name}'
```

## Limpieza
```bash
kubectl delete -f pod.yaml
```
