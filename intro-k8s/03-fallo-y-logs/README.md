# Deployment que falla

```bash
kubectl apply -f deployment.yaml
```

El pod crashea → K8s reintenta (backoff exponencial)

## Ver fallo y logs
- `kubectl get pods` (ver estado CrashLoopBackOff)
- `kubectl describe pod -l app=crash`
- `kubectl logs -l app=crash --previous` (logs del intento anterior)
