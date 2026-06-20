#!/usr/bin/env bash
# deploy.sh — sestaví Docker obrazy, nahraje do k3s a nasadí manifesty.
# Spusť na serveru z kořene repozitáře.
set -euo pipefail

NAMESPACE="bankovni-kurzy"
BACKEND_IMAGE="bankovni-kurzy/backend:latest"
FRONTEND_IMAGE="bankovni-kurzy/frontend:latest"

echo "=== Sestavuji backend ==="
docker build -t "$BACKEND_IMAGE" ./backend

echo "=== Sestavuji frontend ==="
docker build -t "$FRONTEND_IMAGE" ./frontend

echo "=== Nahrávám obrazy do k3s ==="
docker save "$BACKEND_IMAGE" | sudo k3s ctr images import -
docker save "$FRONTEND_IMAGE" | sudo k3s ctr images import -

echo "=== Vytvářím namespace ==="
sudo k3s kubectl apply -f k8s/namespace.yaml

# Vytvoření Secret (pouze pokud ještě neexistuje)
if ! sudo k3s kubectl -n "$NAMESPACE" get secret backend-secret &>/dev/null; then
  echo "=== Vytvářím backend-secret ==="
  echo "Zadej hodnoty pro produkční prostředí:"
  read -rp "SECRET_KEY: " SECRET_KEY
  read -rp "DB_PASSWORD: " DB_PASSWORD
  sudo k3s kubectl -n "$NAMESPACE" create secret generic backend-secret \
    --from-literal=SECRET_KEY="$SECRET_KEY" \
    --from-literal=DB_NAME="bankovni_kurzy" \
    --from-literal=DB_USER="bankovni_kurzy" \
    --from-literal=DB_PASSWORD="$DB_PASSWORD"
fi

echo "=== Nasazuji manifesty ==="
sudo k3s kubectl apply -f k8s/postgres.yaml
sudo k3s kubectl apply -f k8s/backend.yaml
sudo k3s kubectl apply -f k8s/frontend.yaml
sudo k3s kubectl apply -f k8s/cronjob.yaml
sudo k3s kubectl apply -f k8s/ingress.yaml

echo ""
echo "=== Hotovo! ==="
echo "Stav podů:"
sudo k3s kubectl -n "$NAMESPACE" get pods
echo ""
echo "Web bude dostupný na: https://kurzy.frapa.eu"
echo "(DNS musí ukazovat na IP tohoto serveru)"
