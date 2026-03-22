# ConfigMap

```bash
kubectl apply -f configmap.yaml
```

## Verificar que el Pod usa las variables
```bash
kubectl logs configmap-pod
```

Deberías ver: `Hola desde ConfigMap` y `debug`

## Inspeccionar el ConfigMap
```bash
kubectl get configmap app-config
kubectl describe configmap app-config
```

## Editar ConfigMap en vivo (opcional)
```bash
kubectl edit configmap app-config
# Cambiar GREETING a otro valor → el pod NO se actualiza automáticamente
# Para que tome el cambio, recrear el pod: kubectl delete pod configmap-pod
```

## Limpieza
```bash
kubectl delete -f configmap.yaml
```
