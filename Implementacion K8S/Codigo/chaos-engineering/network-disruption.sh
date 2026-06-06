#!/bin/sh
# Chaos: interrupción de tráfico de red en un pod.
# Uso: ./network-disruption.sh [deployment] [porcentaje-perdida] [delay-ms] [segundos]
# Ejemplo: ./network-disruption.sh pharmago-pharmacy-service 50 200 60
#
# Observar en Grafana: latencia p95 sube, tasa de errores aumenta.
# El Circuit Breaker en UsersService debería abrirse tras 5 fallas consecutivas.
#
# Cómo funciona: la imagen de la app (aspnet:6.0) no trae `tc` (iproute2).
# En vez de exec dentro del pod, se inyecta un contenedor EFÍMERO `netshoot`
# con el perfil `netadmin` (capability NET_ADMIN). El contenedor efímero
# comparte el network namespace del pod, así que el netem sobre eth0 afecta
# el tráfico real del pod sin modificar la imagen de producción.
#
# Requiere: Kubernetes >= 1.27 (kubectl debug --profile netadmin).
# La primera ejecución descarga la imagen nicolaka/netshoot (puede tardar).

DEPLOY="${1:-pharmago-pharmacy-service}"
LOSS="${2:-50}"
DELAY="${3:-200}"
SECS="${4:-60}"

POD=$(kubectl get pod -n pharmago -l app="$DEPLOY" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POD" ]; then
  echo "Error: no hay pods con app=$DEPLOY en el namespace pharmago."
  echo "  Ejemplo de valores: pharmago-pharmacy-service, pharmago-users-service"
  exit 1
fi

echo "=== Chaos: Network disruption ==="
echo "  Pod:          $POD"
echo "  Perdida:      ${LOSS}%"
echo "  Delay:        ${DELAY}ms"
echo "  Duracion:     ${SECS}s"
echo ""
echo "  Observar en Grafana: pharmago_http_errors_total, request_duration"
echo "  Si el Circuit Breaker esta activo, UsersService dejara de llamar a PharmacyService"
echo ""

kubectl debug -n pharmago "$POD" \
  --image=nicolaka/netshoot \
  --profile=netadmin \
  -q -- sh -c "
    tc qdisc add dev eth0 root netem loss ${LOSS}% delay ${DELAY}ms 2>/dev/null || \
    tc qdisc change dev eth0 root netem loss ${LOSS}% delay ${DELAY}ms
    echo 'Disrupcion de red activa...'
    sleep ${SECS}
    tc qdisc del dev eth0 root 2>/dev/null
    echo 'Red restaurada.'
  "
