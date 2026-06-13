#!/bin/sh
# Chaos: CPU spike en pod. Uso: ./cpu-spike.sh [deployment] [segundos]
DEPLOY="${1:-pharmago-api-gateway}"
SECS="${2:-90}"
POD=$(kubectl get pod -n pharmago -l app="$DEPLOY" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POD" ]; then
  echo "Error: no hay pods con app=$DEPLOY en el namespace pharmago."
  echo "  Verifica el nombre (ej: pharmago-api-gateway, pharmago-users-service)"
  exit 1
fi
echo "CPU spike: $POD (${SECS}s)"
kubectl exec -n pharmago "$POD" -- sh -c "
  (while :;do :;done)& P1=\$!
  (while :;do :;done)& P2=\$!
  (while :;do :;done)& P3=\$!
  (while :;do :;done)& P4=\$!
  sleep $SECS
  kill \$P1 \$P2 \$P3 \$P4 2>/dev/null
  echo 'CPU spike finalizado.'
"
