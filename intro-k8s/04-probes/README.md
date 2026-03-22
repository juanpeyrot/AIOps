# Pod con Liveness y Readiness Probes

```bash
kubectl apply -f pod.yaml
```

## Observar el ciclo de vida
- `kubectl get pods -w` — ver pasar de `ContainerCreating` a `Running`
- `kubectl describe pod nginx-probes` — ver las condiciones de readiness/liveness

## Probar el livenessProbe (simular fallo)
```bash
# Borrar el index de nginx → el liveness falla → K8s reinicia el contenedor
kubectl exec -it nginx-probes -- sh -c "rm /usr/share/nginx/html/index.html"
```

**En Windows (Git Bash)**: Si la ruta se interpreta mal, usa antes `MSYS_NO_PATHCONV=1` o ejecuta el comando con `sh -c "..."` como arriba (evita la conversión de rutas de MSYS).

Observar: `kubectl get pods -w` — el pod se reinicia cuando falla el liveness.

## Limpieza
```bash
kubectl delete -f pod.yaml
```
