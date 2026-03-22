# Métricas con kubectl top

## Requisito previo: Metrics Server

Sin metrics-server, `kubectl top` da: `error: Metrics API not available`

**En Minikube** — ejecutar primero:
```bash
minikube addons enable metrics-server
```

Verificar que esté listo (puede tardar 1-2 min):
```bash
kubectl get pods -n kube-system -l k8s-app=metrics-server
kubectl top nodes   # si funciona, metrics-server está OK
```

**En otros clusters** (kind, k3d): instalar metrics-server manualmente o ver la documentación del cluster.

---

```bash
kubectl apply -f deployment.yaml
```

## Ver consumo de recursos de pods
```bash
kubectl top pods
kubectl top pods -l app=stress
kubectl top pod -l app=stress --sort-by=memory
```

## Ver consumo de nodos
```bash
kubectl top nodes
```

## Troubleshooting

| Error | Solución |
|-------|----------|
| `Metrics API not available` | `minikube addons enable metrics-server` y esperar 1-2 min |
| `metrics-server` en CrashLoopBackOff | En algunos minikube: `minikube addons disable metrics-server` luego `enable` de nuevo, o reiniciar minikube |

## Limpieza
```bash
kubectl delete -f deployment.yaml
```
