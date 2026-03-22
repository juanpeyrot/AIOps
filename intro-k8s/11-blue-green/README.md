# Blue/Green a mano (primitives nativos)

Blue/Green **no** viene built-in en Kubernetes. Se implementa con dos Deployments + un Service. El Service decide cuál recibe tráfico mediante su selector.

```bash
kubectl apply -f deployment-blue.yaml
kubectl apply -f deployment-green.yaml
kubectl apply -f service.yaml
```

## Observar
```bash
# Ambos entornos existen al mismo tiempo
kubectl get pods --show-labels

# El Service apunta a blue por su selector
kubectl get svc
kubectl describe svc demo-service
```

## Verificar tráfico a Blue
```bash
# En una terminal
kubectl port-forward service/demo-service 8080:80
```

En otra: `curl localhost:8080` → debe responder `BLUE`

## Cambiar tráfico a Green
```bash
# Cambiar el selector del Service (sin tocar los Deployments)
kubectl patch service demo-service -p '{"spec":{"selector":{"app":"demo","version":"green"}}}'
```

## Verificar tráfico a Green
```bash
curl localhost:8080
```
→ debe responder `GREEN`

## Volver a Blue
```bash
kubectl patch service demo-service -p '{"spec":{"selector":{"app":"demo","version":"blue"}}}'
curl localhost:8080
```

## Resumen
- Blue y Green existen en paralelo (no es rolling update)
- El cambio es lógico: solo se cambia el selector del Service
- Sin downtime: el switch es instantáneo

## Limpieza
```bash
kubectl delete -f deployment-blue.yaml -f deployment-green.yaml -f service.yaml
# O: Ctrl+C en el port-forward
```
