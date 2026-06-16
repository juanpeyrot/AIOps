#!/bin/sh
# Genera tráfico continuo a endpoints de pharmacy-service via API Gateway.
# Usar junto con network-disruption.sh para ver impacto en Grafana Overview.
# Uso: ./pharmacy-load.sh [base-url] [intervalo-segundos]
#   base-url: URL del API Gateway con port-forward activo (default: http://localhost:8080)
#   intervalo: segundos entre cada ronda de requests (default: 1)
#
# Prerequisito: kubectl port-forward -n pharmago svc/pharmago-api-gateway 8080:80

BASE="${1:-http://localhost:8080}"
INTERVAL="${2:-1}"

echo "=== Pharmacy Load Generator ==="
echo "  Gateway: $BASE"
echo "  Intervalo: ${INTERVAL}s"
echo "  Ctrl+C para detener"
echo ""

echo "Obteniendo token..."
TOKEN=$(curl -s -X POST "$BASE/api/login" \
  -H "Content-Type: application/json" \
  -d '{"userName":"admin","password":"Abcdef12."}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Error: no se pudo obtener token."
  echo "  Verificá que el port-forward esté activo:"
  echo "  kubectl port-forward -n pharmago svc/pharmago-api-gateway 8080:80"
  exit 1
fi
echo "Token OK. Enviando requests a pharmacy-service..."
echo ""

i=0
while true; do
  i=$((i + 1))
  curl -s -o /dev/null -w "[$i] /api/drug      %{http_code}  %{time_total}s\n" \
    -H "Authorization: Bearer $TOKEN" "$BASE/api/drug" &
  curl -s -o /dev/null -w "[$i] /api/drug      %{http_code}  %{time_total}s\n" \
    -H "Authorization: Bearer $TOKEN" "$BASE/api/drug" &
  curl -s -o /dev/null -w "[$i] /api/pharmacy  %{http_code}  %{time_total}s\n" \
    -H "Authorization: Bearer $TOKEN" "$BASE/api/pharmacy" &
  curl -s -o /dev/null -w "[$i] /api/pharmacy  %{http_code}  %{time_total}s\n" \
    -H "Authorization: Bearer $TOKEN" "$BASE/api/pharmacy" &
  wait
  sleep "$INTERVAL"
done
