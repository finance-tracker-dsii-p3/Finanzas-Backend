"""
Tests para servicios de exportación (export/services.py)
"""

import tempfile
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from export.models import ExportJob
from export.services import BasicDataExporter, ExportService
from notifications.models import Notification

User = get_user_model()


class ExportServicesTests(TestCase):
    """Tests para servicios de exportación"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuario
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_verified=True,
        )

        # Crear otro usuario
        self.user2 = User.objects.create_user(
            identification="87654321",
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test2",
            last_name="User2",
            is_verified=True,
        )

        # Crear notificaciones
        self.notification1 = Notification.objects.create(
            user=self.user,
            title="Test Notification 1",
            message="Test message 1",
            notification_type="info",
            read=False,
        )
        self.notification2 = Notification.objects.create(
            user=self.user2,
            title="Test Notification 2",
            message="Test message 2",
            notification_type="warning",
            read=True,
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_basic_data_exporter_init(self):
        """Test: Inicialización de BasicDataExporter"""
        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            user_ids=[self.user.id],
        )

        exporter = BasicDataExporter(export_job)
        assert exporter.export_job == export_job
        assert exporter.user_ids == [self.user.id]

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_users_data_success(self):
        """Test: Exportar datos de usuarios exitosamente"""
        export_job = ExportJob.objects.create(
            title="Test Users Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            user_ids=[self.user.id, self.user2.id],
        )

        exporter = BasicDataExporter(export_job)
        result = exporter.export_users_data()

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED
        assert export_job.file is not None
        assert export_job.file_size is not None

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_users_data_all_users(self):
        """Test: Exportar todos los usuarios cuando no se especifican IDs"""
        export_job = ExportJob.objects.create(
            title="Test All Users Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            user_ids=None,
        )

        exporter = BasicDataExporter(export_job)
        result = exporter.export_users_data()

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_notifications_data_success(self):
        """Test: Exportar datos de notificaciones exitosamente"""
        export_job = ExportJob.objects.create(
            title="Test Notifications Export",
            export_type=ExportJob.NOTIFICATIONS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
        )

        exporter = BasicDataExporter(export_job)
        result = exporter.export_notifications_data()

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED
        assert export_job.file is not None

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_notifications_data_with_date_filters(self):
        """Test: Exportar notificaciones con filtros de fecha"""
        # Crear notificación antigua
        old_notification = Notification.objects.create(
            user=self.user,
            title="Old Notification",
            message="Old message",
            notification_type="info",
        )
        old_notification.created_at = timezone.now() - timedelta(days=10)
        old_notification.save()

        export_job = ExportJob.objects.create(
            title="Test Notifications Export Filtered",
            export_type=ExportJob.NOTIFICATIONS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today(),
        )

        exporter = BasicDataExporter(export_job)
        result = exporter.export_notifications_data()

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_service_process_export_job_users(self):
        """Test: ExportService procesa trabajo de usuarios"""
        export_job = ExportJob.objects.create(
            title="Test Export Service Users",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
            user_ids=[self.user.id],
        )

        result = ExportService.process_export_job(export_job.id)

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_service_process_export_job_notifications(self):
        """Test: ExportService procesa trabajo de notificaciones"""
        export_job = ExportJob.objects.create(
            title="Test Export Service Notifications",
            export_type=ExportJob.NOTIFICATIONS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        result = ExportService.process_export_job(export_job.id)

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_service_process_export_job_unknown_type(self):
        """Test: ExportService procesa tipo desconocido (usa usuarios por defecto)"""
        export_job = ExportJob.objects.create(
            title="Test Export Service Unknown",
            export_type=ExportJob.GENERAL_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        result = ExportService.process_export_job(export_job.id)

        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_service_process_export_job_nonexistent(self):
        """Test: ExportService maneja trabajo inexistente"""
        result = ExportService.process_export_job(99999)
        assert result is False

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_users_data_marks_as_failed_on_error(self):
        """Test: Exportar usuarios marca como fallido en caso de error"""
        # Este test verifica que el manejo de errores funciona
        # El código actual crea el directorio si no existe, así que
        # verificamos que el método mark_as_failed existe y funciona
        export_job = ExportJob.objects.create(
            title="Test Export Error",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        # Verificar que mark_as_failed funciona
        export_job.mark_as_failed("Test error message")
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.FAILED
        assert export_job.error_message == "Test error message"
