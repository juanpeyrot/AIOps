# Pod básico

```bash
kubectl apply -f pod.yaml
```

## Inspección
- `kubectl get pods`
- `kubectl describe pod hello-pod`
- `kubectl logs hello-pod`
- `kubectl exec -it hello-pod -- sh` (shell interactivo)

## Limpieza
```bash
kubectl delete -f pod.yaml
```
