"""
Swagger UI configuration for Royal Taxi API
"""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError
from config import settings
# JWT error handler
def jwt_exception_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Could not validate credentials"}
    )


def setup_swagger_ui(app: FastAPI):
    """Configure Swagger UI with improved authentication and open endpoints"""
    
    # Add JWT error handler
    app.add_exception_handler(JWTError, jwt_exception_handler)
    
    # Update the OpenAPI schema to include security definitions
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=settings.api_title,
            version=settings.api_version,
            description=settings.api_description,
            routes=app.routes,
        )
        
        # Add security definitions
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token in format: Bearer <token>"
            }
        }
        
        # Ensure registration endpoint is properly documented
        if "/api/v1/auth/register" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/v1/auth/register"]["post"].update({
                "tags": ["Authentication"],
                "summary": "Register a new user",
                "description": "Create a new user account with the provided details",
                "responses": {
                    "201": {
                        "description": "User registered successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Token"}
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - phone number already exists"
                    },
                    "422": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
                            }
                        }
                    }
                },
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UserRegister"}
                        }
                    }
                }
            })
        
        # Define open endpoints (no authentication required)
        open_endpoints = [
            "/auth/login",
            "/auth/register",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/health",
            "/api/v1/map/route"  # Public route calculation
        ]
        
        # Add security only to protected endpoints
        if "paths" in openapi_schema:
            for path, path_info in openapi_schema["paths"].items():
                if path not in open_endpoints:
                    for method in path_info.keys():
                        if method.lower() in ["get", "post", "put", "delete", "patch"]:
                            if "security" not in path_info[method]:
                                path_info[method]["security"] = [{"Bearer": []}]
        
        # Add login endpoint to the schema
        if "paths" not in openapi_schema:
            openapi_schema["paths"] = {}
            
        openapi_schema["paths"]["/api/v1/auth/login"] = {
            "post": {
                "tags": ["Auth"],
                "summary": "Login",
                "description": "Login with email/phone and password. Returns token for automatic authorization.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserLogin"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful login - token will be automatically applied to Swagger UI",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {"type": "string", "description": "JWT access token"},
                                        "token_type": {"type": "string", "example": "bearer"},
                                        "expires_in": {"type": "integer", "description": "Token expiration in seconds"},
                                        "user": {
                                            "type": "object",
                                            "description": "User information"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add register endpoint
        openapi_schema["paths"]["/api/v1/auth/register"] = {
            "post": {
                "tags": ["Auth"],
                "summary": "Register",
                "description": "Register a new user. Returns token for automatic authorization.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserRegister"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful registration - token will be automatically applied to Swagger UI",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {"type": "string", "description": "JWT access token"},
                                        "token_type": {"type": "string", "example": "bearer"},
                                        "expires_in": {"type": "integer", "description": "Token expiration in seconds"},
                                        "user": {
                                            "type": "object",
                                            "description": "User information"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add schemas
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        if "schemas" not in openapi_schema["components"]:
            openapi_schema["components"]["schemas"] = {}
            
        openapi_schema["components"]["schemas"]["UserLogin"] = {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Uzbekistan phone number format (+998XXXXXXXXX)", "example": "+998901234567"},
                "password": {"type": "string", "format": "password", "example": "yourpassword"}
            },
            "required": ["phone", "password"]
        }
        
        openapi_schema["components"]["schemas"]["DispatchOrderCreate"] = {
            "type": "object",
            "properties": {
                "customer_phone": {
                    "type": "string",
                    "description": "Customer phone number (+998XXXXXXXXX)",
                    "example": "+998901234567",
                    "pattern": r"^\+998\d{9}$"
                },
                "customer_name": {
                    "type": "string", 
                    "description": "Customer name (optional)",
                    "example": "Ali Valiyev"
                },
                "pickup_location": {
                    "$ref": "#/components/schemas/Location"
                },
                "dropoff_location": {
                    "$ref": "#/components/schemas/Location"
                },
                "vehicle_type": {
                    "type": "string",
                    "enum": ["ECONOMY", "COMFORT", "BUSINESS"],
                    "default": "ECONOMY",
                    "description": "Vehicle type",
                    "example": "ECONOMY"
                }
            },
            "required": ["pickup_location", "dropoff_location"]
        }
        
        openapi_schema["components"]["schemas"]["Location"] = {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "format": "float",
                    "minimum": -90,
                    "maximum": 90,
                    "description": "Latitude",
                    "example": 41.2995
                },
                "lng": {
                    "type": "number", 
                    "format": "float",
                    "minimum": -180,
                    "maximum": 180,
                    "description": "Longitude",
                    "example": 69.2401
                },
                "address": {
                    "type": "string",
                    "description": "Address string",
                    "example": "Toshkent shahar, Amir Temur kochasi"
                },
                "city": {
                    "type": "string",
                    "description": "City/Region name (optional)",
                    "example": "Toshkent"
                }
            },
            "required": ["lat", "lng", "address"]
        }
        
        openapi_schema["components"]["schemas"]["DriverStatusUpdate"] = {
            "type": "object",
            "properties": {
                "is_on_duty": {
                    "type": "boolean",
                    "description": "Whether driver is on duty",
                    "example": True
                },
                "lat": {
                    "type": "number",
                    "format": "float",
                    "minimum": -90,
                    "maximum": 90,
                    "description": "Current latitude (optional)",
                    "example": 41.2995
                },
                "lng": {
                    "type": "number",
                    "format": "float", 
                    "minimum": -180,
                    "maximum": 180,
                    "description": "Current longitude (optional)",
                    "example": 69.2401
                },
                "city": {
                    "type": "string",
                    "description": "Current city (optional)",
                    "example": "Toshkent"
                }
            },
            "required": ["is_on_duty"]
        }
        
        openapi_schema["components"]["schemas"]["UserRegister"] = {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string", 
                    "description": "O'zbekiston telefon raqami formati (+998XXXXXXXXX)", 
                    "example": "+998901234567",
                    "pattern": r"^\+998\d{9}$"
                },
                "first_name": {
                    "type": "string", 
                    "description": "Foydalanuvchi ismi", 
                    "example": "Falonchi",
                    "minLength": 2,
                    "maxLength": 50
                },
                "last_name": {
                    "type": "string", 
                    "description": "Foydalanuvchi familiyasi", 
                    "example": "Falonchiyev",
                    "minLength": 2,
                    "maxLength": 50
                },
                "password": {
                    "type": "string", 
                    "format": "password", 
                    "description": "Parol (kamida 6 ta belgi)", 
                    "example": "strongpassword123",
                    "minLength": 6,
                    "maxLength": 100
                },
                "gender": {
                    "type": "string", 
                    "description": "Jinsi (Erkak/Ayol)", 
                    "example": "Erkak"
                },
                "date_of_birth": {
                    "type": "string", 
                    "format": "date", 
                    "description": "Tug'ilgan sana (YYYY-MM-DD)", 
                    "example": "1990-01-01"
                },
                "vehicle_make": {
                    "type": "string", 
                    "description": "Avtomobil markasi", 
                    "example": "Chevrolet"
                },
                "vehicle_color": {
                    "type": "string", 
                    "description": "Avtomobil rangi", 
                    "example": "Qora"
                },
                "position": {
                    "type": "string", 
                    "description": "Pozitsiya", 
                    "example": "Haydovchi"
                },
                "license_plate": {
                    "type": "string", 
                    "description": "Davlat raqami", 
                    "example": "01A123AA"
                },
                "tech_passport": {
                    "type": "string", 
                    "description": "Texpassport raqami", 
                    "example": "AA1234567"
                }
            },
            "required": [
                "phone", 
                "first_name", 
                "last_name", 
                "password", 
                "gender", 
                "date_of_birth",
                "vehicle_make",
                "vehicle_color", 
                "position",
                "license_plate",
                "tech_passport"
            ]
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    # Apply the custom OpenAPI schema
    app.openapi = custom_openapi
    
    # Configure Swagger UI parameters for better UX with auto-authorization
    app.swagger_ui_parameters = {
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
        "requestSnippetsEnabled": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "showExtensions": True,
        "showCommonExtensions": True,
        "oauth2RedirectUrl": "/docs/oauth2-redirect",
        "onComplete": "function() { "
            "const apiKeyAuth = localStorage.getItem('authorized') && JSON.parse(localStorage.getItem('authorized'))['Bearer']?.value; "
            "if (apiKeyAuth) { "
                "const input = document.querySelector('input[type=\'password\']'); "
                "if (input) { "
                    "input.value = apiKeyAuth; "
                    "const authBtn = document.querySelector('.btn.authorize'); "
                    "if (authBtn) authBtn.click(); "
                    "const modal = document.querySelector('.dialog-ux'); "
                    "if (modal) modal.remove(); "
                "} "
            "} "
            "// Auto-submit login form if credentials are in URL hash "
            "const hash = window.location.hash.substring(1); "
            "if (hash) { "
                "const params = new URLSearchParams(hash); "
                "const accessToken = params.get('access_token'); "
                "if (accessToken) { "
                    "localStorage.setItem('authorized', JSON.stringify({ 'Bearer': { value: accessToken, name: 'Authorization', 'type': 'bearer' } })); "
                    "window.ui.preauthorizeApiKey('Bearer', accessToken); "
                "} "
            "} "
        "}",
        "onFailure": "function() { console.log('Swagger UI failed to load'); }"
    }
    
    return app
