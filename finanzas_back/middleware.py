"""
Middleware personalizado para el proyecto de finanzas
"""

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class APIErrorHandlerMiddleware:
    """
    Middleware para asegurar que todas las respuestas de error de la API sean JSON
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Solo procesar rutas de API
        if request.path.startswith("/api/"):
            # Si la respuesta es HTML y hay un error, convertirla a JSON
            if response.status_code >= 400 and response.get("Content-Type", "").startswith(
                "text/html"
            ):
                error_message = self._get_error_message_from_status(response.status_code)

                return JsonResponse(
                    {
                        "error": error_message,
                        "status_code": response.status_code,
                        "message": "Error procesando la petición",
                        "suggestion": "Verifica que los datos enviados sean válidos y que tengas permisos para realizar esta acción",
                    },
                    status=response.status_code,
                )

        return response

    def process_exception(self, request, exception):
        """Manejar excepciones no capturadas en rutas de API"""
        if request.path.startswith("/api/"):
            logger.error(f"API Exception: {type(exception).__name__}: {exception!s}")

            # Diferentes tipos de errores
            if isinstance(exception, ValidationError):
                return JsonResponse(
                    {
                        "error": "Error de validación",
                        "message": str(exception),
                        "type": "ValidationError",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if isinstance(exception, PermissionError):
                return JsonResponse(
                    {
                        "error": "Sin permisos",
                        "message": "No tienes permisos para realizar esta acción",
                        "type": "PermissionError",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Error genérico
            return JsonResponse(
                {
                    "error": "Error interno del servidor",
                    "message": str(exception) if settings.DEBUG else "Ha ocurrido un error interno",
                    "type": type(exception).__name__,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Si no es una ruta de API, dejar que Django maneje la excepción normalmente
        return None

    def _get_error_message_from_status(self, status_code):
        """Obtener mensaje de error apropiado según el código de estado"""
        error_messages = {
            400: "Datos de entrada inválidos",
            401: "No autenticado - Token requerido",
            403: "Sin permisos para esta acción",
            404: "Recurso no encontrado",
            405: "Método HTTP no permitido",
            500: "Error interno del servidor",
        }

        return error_messages.get(status_code, f"Error HTTP {status_code}")


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para DRF
    """
    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)

    if response is not None:
        # Personalizar el formato de error
        custom_response_data = {
            "error": True,
            "message": "Error en la petición",
            "details": response.data,
            "status_code": response.status_code,
        }

        # Agregar sugerencias específicas según el tipo de error
        if response.status_code == 400:
            custom_response_data["suggestion"] = (
                "Verifica que todos los campos requeridos estén presentes y sean válidos"
            )
        elif response.status_code == 401:
            custom_response_data["suggestion"] = (
                "Incluye el token de autenticación en el header Authorization"
            )
        elif response.status_code == 403:
            custom_response_data["suggestion"] = (
                "Verifica que tengas permisos para realizar esta acción"
            )
        elif response.status_code == 404:
            custom_response_data["suggestion"] = (
                "Verifica que el ID del recurso sea correcto y te pertenezca"
            )

        response.data = custom_response_data

    return response
