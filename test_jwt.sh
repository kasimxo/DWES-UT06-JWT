#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"

echo "=== 1. Intentar acceder sin token ==="
curl -s $BASE_URL/users/ | jq .

echo -e "\n=== 2. Obtener tokens (login) ==="
# Podemos probar con email alumno1@alumno.com y contraseña 1234
TOKENS=$(curl -s -X POST $BASE_URL/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alumno1@alumno.com", "password": "1234"}')

echo $TOKENS | jq .
ACCESS=$(echo $TOKENS | jq -r '.access')
REFRESH=$(echo $TOKENS | jq -r '.refresh')

echo -e "\n=== 3. Acceder con token ==="
echo -e "Obtenemos el listado de usuarios y mostramos el primero"
# Aquí mostramos únicamente el primer resultado
curl -s $BASE_URL/users/ \
  -H "Authorization: Bearer $ACCESS" | jq '.[0]'

echo -e "\n=== 4. Logout (invalidar refresh) ==="
curl -s -X POST $BASE_URL/users/auth/logout/ \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .

echo -e "\n=== 5. Intentar usar refresh token invalidado ==="
curl -s -X POST $BASE_URL/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .