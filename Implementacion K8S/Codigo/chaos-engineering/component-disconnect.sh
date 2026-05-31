#!/bin/sh
# Chaos: desconexion de un componente interno de la aplicacion.
# Simula la caida total de un microservicio escalando su Deployment a 0 replicas.
# Uso: ./component-disconnect.sh [deployment] [segundos-caida]
# Ejemplo: ./component-disconnect.sh pharmago-pharmacy-service 30
#
# Observar en Grafana:
#   - Pods disponibles del servicio cae a 0
#   - pharmago_http_errors_total sube en el servicio dependiente
#   - El Circuit Breaker (Polly) abre el circuito en UsersService
#   - Al restaurar, K8s levanta las replicas automaticamente (self-healing)

DEPLOY="${1:-pharmago-pharmacy-service}"
SECS="${2:-30}"
ORIGINAL_REPLICAS="${3:-1}"

echo "=== Chaos: Component disconnect ==="
echo "  Deployment:   $DEPLOY"
echo "  Duracion:     ${SECS}s"
echo ""
echo "  Observar en Grafana: pods disponibles, tasa de errores HTTP"
echo "  Observar en Kibana:  logs de 'circuit breaker' en UsersService"
echo ""

echo "[1/3] Escalando $DEPLOY a 0 replicas..."
kubectl scale deployment "$DEPLOY" --replicas=0 -n pharmago

echo "[2/3] Esperando ${SECS}s para observar el comportamiento..."
sleep "$SECS"

echo "[3/3] Restaurando $DEPLOY a $ORIGINAL_REPLICAS replica(s)..."
kubectl scale deployment "$DEPLOY" --replicas="$ORIGINAL_REPLICAS" -n pharmago
kubectl rollout status deployment/"$DEPLOY" -n pharmago

echo ""
echo "Servicio restaurado. Verificar en Grafana que las metricas vuelven a valores normales."
