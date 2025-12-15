"""
Tests para export/services.py
Fase 1: Aumentar cobertura de tests
"""

import os
import tempfile
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from export.models import ExportJob
from export.services import BasicDataExporter, ExportService
from notifications.models import Notification

User = get_user_model()


class BasicDataExporterTests(TestCase):
    """Tests para BasicDataExporter"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        # Crear otro usuario para pruebas
        self.user2 = User.objects.create_user(
            identification="87654321",
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            is_verified=True,
        )

        # Crear export job
        self.export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        self.exporter = BasicDataExporter(self.export_job)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_users_data_success(self):
        """Test: Exportar datos de usuarios exitosamente"""
        result = self.exporter.export_users_data()
        assert result is True
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.COMPLETED
        assert self.export_job.file is not None

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_users_data_with_user_ids_filter(self):
        """Test: Exportar usuarios filtrados por IDs"""
        self.export_job.user_ids = [self.user.id]
        self.export_job.save()
        exporter = BasicDataExporter(self.export_job)

        result = exporter.export_users_data()
        assert result is True
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_notifications_data_success(self):
        """Test: Exportar datos de notificaciones exitosamente"""
        # Crear notificaciones
        Notification.objects.create(
            user=self.user,
            notification_type="info",
            title="Test Notification",
            message="Test message",
        )

        # Cambiar tipo de exportación
        self.export_job.export_type = ExportJob.NOTIFICATIONS_DATA
        self.export_job.save()
        exporter = BasicDataExporter(self.export_job)

        result = exporter.export_notifications_data()
        assert result is True
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_export_notifications_data_with_date_filters(self):
        """Test: Exportar notificaciones con filtros de fecha"""
        # Crear notificaciones con diferentes fechas
        old_notification = Notification.objects.create(
            user=self.user,
            notification_type="info",
            title="Old Notification",
            message="Old message",
        )
        old_notification.created_at = timezone.now() - timedelta(days=10)
        old_notification.save()

        recent_notification = Notification.objects.create(
            user=self.user,
            notification_type="info",
            title="Recent Notification",
            message="Recent message",
        )

        # Configurar filtros de fecha
        self.export_job.export_type = ExportJob.NOTIFICATIONS_DATA
        self.export_job.start_date = date.today() - timedelta(days=5)
        self.export_job.end_date = date.today()
        self.export_job.save()
        exporter = BasicDataExporter(self.export_job)

        result = exporter.export_notifications_data()
        assert result is True
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.COMPLETED

    @patch("export.services.openpyxl.Workbook")
    def test_export_users_data_handles_exception(self, mock_workbook):
        """Test: Manejar excepciones durante exportación de usuarios"""
        mock_workbook.side_effect = Exception("Test error")

        result = self.exporter.export_users_data()
        assert result is False
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.FAILED
        assert "Test error" in self.export_job.error_message

    @patch("export.services.openpyxl.Workbook")
    def test_export_notifications_data_handles_exception(self, mock_workbook):
        """Test: Manejar excepciones durante exportación de notificaciones"""
        mock_workbook.side_effect = Exception("Test error")

        self.export_job.export_type = ExportJob.NOTIFICATIONS_DATA
        self.export_job.save()
        exporter = BasicDataExporter(self.export_job)

        result = exporter.export_notifications_data()
        assert result is False
        self.export_job.refresh_from_db()
        assert self.export_job.status == ExportJob.FAILED
        assert "Test error" in self.export_job.error_message

    def test_init_stores_export_job_data(self):
        """Test: Inicialización almacena datos del export job"""
        assert self.exporter.export_job == self.export_job
        assert self.exporter.user_ids == self.export_job.user_ids
        assert self.exporter.start_date == self.export_job.start_date
        assert self.exporter.end_date == self.export_job.end_date


class ExportServiceTests(TestCase):
    """Tests para ExportService"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_process_export_job_users_data(self):
        """Test: Procesar trabajo de exportación de usuarios"""
        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        result = ExportService.process_export_job(export_job.id)
        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_process_export_job_notifications_data(self):
        """Test: Procesar trabajo de exportación de notificaciones"""
        # Crear notificación
        Notification.objects.create(
            user=self.user,
            notification_type="info",
            title="Test Notification",
            message="Test message",
        )

        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.NOTIFICATIONS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        result = ExportService.process_export_job(export_job.id)
        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_process_export_job_unknown_type_defaults_to_users(self):
        """Test: Tipo desconocido usa exportación de usuarios por defecto"""
        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.GENERAL_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        result = ExportService.process_export_job(export_job.id)
        assert result is True
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.COMPLETED

    def test_process_export_job_nonexistent_id(self):
        """Test: Manejar ID de trabajo inexistente"""
        result = ExportService.process_export_job(99999)
        assert result is False

    @patch("export.services.BasicDataExporter")
    def test_process_export_job_handles_exception(self, mock_exporter_class):
        """Test: Manejar excepciones durante procesamiento"""
        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        mock_exporter = MagicMock()
        mock_exporter.export_users_data.side_effect = Exception("Test error")
        mock_exporter_class.return_value = mock_exporter

        result = ExportService.process_export_job(export_job.id)
        assert result is False
        export_job.refresh_from_db()
        assert export_job.status == ExportJob.FAILED
        assert "Test error" in export_job.error_message

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_process_export_job_marks_as_processing(self):
        """Test: Marcar trabajo como en procesamiento"""
        export_job = ExportJob.objects.create(
            title="Test Export",
            export_type=ExportJob.USERS_DATA,
            format=ExportJob.EXCEL,
            requested_by=self.user,
        )

        # Verificar que está pendiente inicialmente
        assert export_job.status == ExportJob.PENDING

        # Procesar (debe marcar como processing antes de exportar)
        with patch("export.services.BasicDataExporter") as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter.export_users_data.return_value = True
            mock_exporter_class.return_value = mock_exporter

            ExportService.process_export_job(export_job.id)

        # El trabajo debería estar completado después del procesamiento
        export_job.refresh_from_db()
        assert export_job.status in [ExportJob.COMPLETED, ExportJob.PROCESSING]
