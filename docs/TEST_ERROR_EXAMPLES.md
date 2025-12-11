"""
Endpoint de prueba para demostrar mensajes de error mejorados
"""

# Para probar desde Postman o curl:

# 1. Error de validación de categoría:
POST http://localhost:8000/api/rules/
Authorization: Token TU_TOKEN_AQUI
Content-Type: application/json

{
  "name": "Prueba error categoría",
  "criteria_type": "description_contains",
  "keyword": "test",
  "action_type": "assign_category",
  "target_category": 999999,
  "is_active": true,
  "order": 1
}

# Respuesta esperada:
{
  "error": "Datos de entrada inválidos",
  "details": {
    "target_category": "La categoría con ID 999999 no te pertenece. IDs de categorías disponibles: [1, 2, 3]. Usa GET /api/categories/ para ver tus categorías."
  },
  "message": "Por favor corrige los siguientes errores:"
}

# 2. Error de campos requeridos:
POST http://localhost:8000/api/rules/
Authorization: Token TU_TOKEN_AQUI
Content-Type: application/json

{
  "name": "Prueba campos vacíos",
  "criteria_type": "description_contains",
  "action_type": "assign_category",
  "is_active": true,
  "order": 1
}

# Respuesta esperada:
{
  "error": "Datos de entrada inválidos",
  "details": {
    "keyword": "La palabra clave es requerida para criterio \"descripción contiene texto\"",
    "target_category": "La categoría objetivo es requerida para acción \"asignar categoría\""
  },
  "message": "Por favor corrige los siguientes errores:"
}

# 3. Error de nombre duplicado (después de crear una regla):
POST http://localhost:8000/api/rules/
Authorization: Token TU_TOKEN_AQUI
Content-Type: application/json

{
  "name": "Uber y taxis",  # Usar un nombre que ya existe
  "criteria_type": "description_contains",
  "keyword": "test",
  "action_type": "assign_tag",
  "target_tag": "prueba",
  "is_active": true,
  "order": 1
}

# Respuesta esperada:
{
  "error": "Datos de entrada inválidos",
  "details": {
    "name": "Ya tienes una regla con este nombre."
  },
  "message": "Por favor corrige los siguientes errores:"
}
