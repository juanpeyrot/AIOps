#!/bin/sh
# Chaos: inyección de carga masiva al endpoint de login (users-service).
# Uso: ./load-requests.sh [cantidad] [url]
# Requiere: kubectl port-forward -n pharmago svc/pharmago-api-gateway 8080:80
# Ver en Grafana Overview: "Peticiones por Segundo" y "Throughput Total" suben en pico.
URL="${2:-http://127.0.0.1:8080/api/login}"
N="${1:-500}"
echo "Load: $N requests a $URL"
i=0
while [ $i -lt $N ]; do
  curl -s -o /dev/null -w "" -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d '{"userName":"admin","password":"Abcdef12."}' &
  i=$((i+1))
done
wait
echo "Done ($N requests enviadas)"
