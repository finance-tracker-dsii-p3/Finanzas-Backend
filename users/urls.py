from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views_preferences import UserNotificationPreferencesViewSet

router = DefaultRouter()

# /api/users/preferences/ - Gestión de preferencias de notificaciones
# GET    /api/users/preferences/              - Ver preferencias del usuario
# POST   /api/users/preferences/              - Crear/actualizar preferencias
# GET    /api/users/preferences/{id}/         - Ver detalle de preferencias
# PUT    /api/users/preferences/{id}/         - Actualizar preferencias completas
# PATCH  /api/users/preferences/{id}/         - Actualizar preferencias parciales
# GET    /api/users/preferences/timezones/    - Listar zonas horarias disponibles
router.register(
    r"preferences", UserNotificationPreferencesViewSet, basename="notification-preferences"
)

urlpatterns = [
    # Router endpoints
    path("", include(router.urls)),
    # Autenticación
    path("register/", views.register_view, name="register"),  # POST - Registrar nuevo usuario
    path("login/", views.login_view, name="login"),  # POST - Iniciar sesión
    path("logout/", views.logout_view, name="logout"),  # POST - Cerrar sesión
    # Perfil de usuario
    path("profile/", views.profile_view, name="profile"),  # GET - Ver perfil actual
    path(
        "profile/update/", views.update_profile_view, name="update_profile"
    ),  # PUT/PATCH - Actualizar perfil
    path(
        "profile/delete/", views.delete_own_account_view, name="delete_own_account"
    ),  # DELETE - Eliminar propia cuenta
    path(
        "change-password/", views.change_password_view, name="change_password"
    ),  # POST - Cambiar contraseña
    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),  # GET - Panel principal del usuario
    # Administración de usuarios (solo admins)
    path(
        "admin/users/", views.admin_users_list_view, name="admin_users_list"
    ),  # GET - Listar todos los usuarios
    path(
        "admin/users/<int:user_id>/edit/", views.admin_edit_user_view, name="admin_edit_user"
    ),  # PATCH - Editar información completa (incluye rol y verificación)
    path(
        "admin/users/<int:user_id>/detail/", views.admin_user_detail_view, name="admin_user_detail"
    ),  # GET - Ver detalle de usuario
    path(
        "admin/users/search/", views.admin_users_search_view, name="admin_users_search"
    ),  # GET - Buscar usuarios con filtros
    # Endpoints DEPRECATED - usar admin_edit_user_view en su lugar
    path(
        "admin/users/<int:user_id>/verify/", views.admin_verify_user_view, name="admin_verify_user"
    ),  # POST - Verificar usuario (DEPRECATED - usar editar)
    path(
        "admin/users/<int:user_id>/promote/",
        views.admin_promote_user_view,
        name="admin_promote_user",
    ),  # POST - Promover a admin (DEPRECATED - usar editar)
    path(
        "admin/users/<int:user_id>/", views.admin_delete_user_view, name="admin_delete_user"
    ),  # DELETE - Eliminar usuario
    path(
        "password/reset-request/", views.password_reset_request_view, name="password_reset_request"
    ),  # POST - Solicitar reset de contraseña
    path(
        "password/reset-confirm/", views.password_reset_confirm_view, name="password_reset_confirm"
    ),  # POST - Confirmar reset de contraseña
]
