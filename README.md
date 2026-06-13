1. Levantar el cluster

```bash
minikube start --cpus=4 --memory=6144 --disk-size=25g --driver=qemu2
minikube addons enable metrics-server
```

2. Construir imágenes y desplegar

```bash
cd "{ruta}/Implementacion K8S/Codigo/k8s"
bash build-images.sh
bash apply-k8s.sh
kubectl wait --for=condition=Ready pod --all -n pharmago --timeout=300s
```

3. Exponer servicios

````bash
ES_LOCAL_PORT=19200 bash port-forward.sh
```bash

4. Verificar cada objetivo

Obj 1: kubectl get pods -n pharmago → 13 pods Running
Obj 2: kubectl delete pod -l app=pharmago-users-service -n pharmago → ver que se auto-recrea
Obj 3: Loop de curl + kubectl rollout restart → ningún 500
Obj 4: http://127.0.0.1:9090 (Prometheus), http://127.0.0.1:16686 (Jaeger), http://127.0.0.1:5601 (Kibana)
Obj 7: Ejecutar los 6 scripts de chaos-engineering/
````
