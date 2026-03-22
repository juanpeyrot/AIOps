# kubectl port-forward

```bash
kubectl apply -f deployment.yaml
```

## Port-forward a un Service
```bash
# localhost:8080 → nginx-svc:80
kubectl port-forward svc/nginx-svc 8080:80
```

En otra terminal o en el navegador: `curl http://localhost:8080` (o abrir http://localhost:8080)

## Port-forward directo a un Pod
```bash
# Obtener nombre del pod
kubectl get pods -l app=nginx

# localhost:9090 → pod:80 (reemplazar NOMBRE-POD por el nombre real)
kubectl port-forward pod/NOMBRE-POD 9090:80
```

## Detener port-forward
`Ctrl+C` en la terminal donde corre `port-forward`

## Limpieza
```bash
kubectl delete -f deployment.yaml
```
