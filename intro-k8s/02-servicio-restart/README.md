# Service + Restart

```bash
kubectl apply -f deployment.yaml
```

## Matar pods → observar restart
```bash
kubectl delete pod -l app=ping
```

K8s recrea automáticamente. Observar: `kubectl get pods -w`
