#!/bin/bash

echo "=== ROYAL TAXI API COMPREHENSIVE TEST ==="
echo ""

# Function to get token
get_token() {
    local phone=$1
    local password=$2
    curl -s -X POST http://localhost:8080/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"phone\": \"$phone\", \"password\": \"$password\"}" | \
        grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

# Get fresh tokens
echo "Getting fresh tokens..."
USER_TOKEN=$(get_token "+998900123458" "testpass123")
ADMIN_TOKEN=$(get_token "+998900000000" "admin123") 
DISPATCHER_TOKEN=$(get_token "+998900000001" "dispatcher123")

echo "USER_TOKEN: ${USER_TOKEN:0:20}..."
echo "ADMIN_TOKEN: ${ADMIN_TOKEN:0:20}..."
echo "DISPATCHER_TOKEN: ${DISPATCHER_TOKEN:0:20}..."
echo ""

# Test AUTH APIs
echo "1. AUTH APIs:"
echo "============="
echo -n "POST /api/v1/auth/register: "
curl -s -X POST http://localhost:8080/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"phone": "+998900123463", "first_name": "Test", "last_name": "Final3", "password": "test123", "gender": "Erkak", "date_of_birth": "1990-01-01", "vehicle_make": "BMW", "vehicle_color": "Qora", "position": "Haydovchi", "license_plate": "55C555CC", "tech_passport": "CC555555"}' \
    -w "%{http_code}" | tail -1

echo -n "POST /api/v1/auth/login: "
curl -s -X POST http://localhost:8080/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"phone": "+998900123458", "password": "testpass123"}' \
    -w "%{http_code}" | tail -1

echo -n "POST /api/v1/auth/logout: "
curl -s -X POST http://localhost:8080/api/v1/auth/logout \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

echo ""
# Test USERS APIs
echo ""
echo "2. USERS APIs:"
echo "=============="
echo -n "GET /api/v1/users/profile: "
curl -s -X GET http://localhost:8080/api/v1/users/profile \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "PUT /api/v1/users/profile: "
curl -s -X PUT http://localhost:8080/api/v1/users/profile \
    -H "Authorization: Bearer $USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"first_name": "Updated", "last_name": "Name"}' \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/users/balance: "
curl -s -X GET http://localhost:8080/api/v1/users/balance \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/users/rides: "
curl -s -X GET http://localhost:8080/api/v1/users/rides \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/users/transactions: "
curl -s -X GET http://localhost:8080/api/v1/users/transactions \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

# Test FILES APIs
echo ""
echo "3. FILES APIs:"
echo "=============="
echo -n "POST /api/v1/files/profile-picture: "
curl -s -X POST http://localhost:8080/api/v1/files/profile-picture \
    -H "Authorization: Bearer $USER_TOKEN" \
    -F "file=@test_image.png" \
    -w "%{http_code}" | tail -1

echo -n "POST /api/v1/files/upload/general: "
curl -s -X POST http://localhost:8080/api/v1/files/upload/general \
    -H "Authorization: Bearer $USER_TOKEN" \
    -F "file=@test_image.png" \
    -w "%{http_code}" | tail -1

# Test DRIVER APIs
echo ""
echo "4. DRIVER APIs:"
echo "==============="
echo -n "POST /api/v1/driver/status: "
curl -s -X POST http://localhost:8080/api/v1/driver/status \
    -H "Authorization: Bearer $USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"is_on_duty": true, "lat": 41.2995, "lng": 69.2401}' \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/driver/stats: "
curl -s -X GET http://localhost:8080/api/v1/driver/stats \
    -H "Authorization: Bearer $USER_TOKEN" \
    -w "%{http_code}" | tail -1

# Test ADMIN APIs
echo ""
echo "5. ADMIN APIs:"
echo "=============="
echo -n "GET /api/v1/admin/users: "
curl -s -X GET http://localhost:8080/api/v1/admin/users \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/admin/stats: "
curl -s -X GET http://localhost:8080/api/v1/admin/stats \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/admin/analytics/daily: "
curl -s -X GET "http://localhost:8080/api/v1/admin/analytics/daily?date=2024-11-02" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -w "%{http_code}" | tail -1

echo -n "GET /api/v1/admin/income/stats: "
curl -s -X GET http://localhost:8080/api/v1/admin/income/stats \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -w "%{http_code}" | tail -1

echo ""
echo "=== TEST COMPLETE ==="
