#!/bin/sh
# Chaos: llenar disco del nodo visible en Grafana. Uso: ./volume-spike.sh [MB] [segundos]
# Escribe en /mnt/data/ del host minikube (fstype ext4, visible en panel "Disco disponible %")
MB="${1:-1000}"
SECS="${2:-90}"

echo "Volume spike: ${MB}MB en /mnt/sda1/chaos_fill del nodo (${SECS}s)"
minikube ssh "sudo rm -f /mnt/sda1/chaos_fill && sudo dd if=/dev/zero of=/mnt/sda1/chaos_fill bs=1M count=$MB"
echo "Disco ocupado. Esperando ${SECS}s..."
sleep "$SECS"
minikube ssh "sudo rm -f /mnt/sda1/chaos_fill"
echo "Volume spike finalizado."
