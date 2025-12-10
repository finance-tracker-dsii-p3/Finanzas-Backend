"""
Tests para el NotificationEngine
Verifica creación de notificaciones, respeto de preferencias, prevención de duplicados, multi-idioma
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from users.models import User, UserNotificationPreferences
from notifications.models import Notification, CustomReminder
from notifications.engine import NotificationEngine
from budgets.models import Budget
from bills.models import Bill
from vehicles.models import Vehicle, SOAT
from categories.models import Category
from accounts.models import Account


class NotificationEngineTestCase(TestCase):
    """Tests para el servicio NotificationEngine"""

    def setUp(self):
        """Configuración inicial para los tests"""
        # Usuario de prueba
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            identification="1234567890",
            password="testpass123",
        )

        # Preferencias con notificaciones activadas (español)
        self.preferences = UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
            language="es",
            enable_budget_alerts=True,
            enable_bill_reminders=True,
            enable_soat_reminders=True,
            enable_month_end_reminders=True,
            enable_custom_reminders=True,
        )

        # Categoría para presupuesto
        self.category = Category.objects.create(name="Comida", type="expense", user=self.user)

        # Presupuesto de prueba
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("1000000.00"),
            period=Budget.MONTHLY,
        )

        # Cuenta para facturas
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta principal",
            account_type=Account.ASSET,
            category=Account.SAVINGS_ACCOUNT,
            current_balance=Decimal("5000000.00"),
        )

        # Factura de prueba
        self.bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=timezone.now().date() + timedelta(days=3),
            suggested_account=self.account,
        )

        # Vehículo y SOAT de prueba
        self.vehicle = Vehicle.objects.create(
            user=self.user, plate="ABC123", brand="Toyota", model="Corolla", year=2020
        )

        self.soat = SOAT.objects.create(
            vehicle=self.vehicle,
            policy_number="SOAT-2025-001",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=15),
            cost=80000000,  # $800,000.00 en centavos
        )

    def test_create_budget_warning_spanish(self):
        """Test: Crear notificación de alerta de presupuesto en español"""
        notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.notification_type, "budget_warning")
        self.assertIn("⚠️", notification.title)
        self.assertIn("Comida", notification.message)
        self.assertIn("850,000", notification.message)
        self.assertIn("1,000,000", notification.message)
        self.assertEqual(notification.related_object_id, self.budget.id)
        self.assertEqual(notification.related_object_type, "budget")
        self.assertFalse(notification.read)

    def test_create_budget_warning_english(self):
        """Test: Crear notificación de alerta de presupuesto en inglés"""
        # Cambiar idioma a inglés
        self.preferences.language = "en"
        self.preferences.save()

        notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        self.assertIsNotNone(notification)
        self.assertIn("Budget Alert", notification.title)
        self.assertIn("Comida", notification.message)  # Nombre de categoría se mantiene
        self.assertIn("850,000", notification.message)

    def test_budget_alert_disabled(self):
        """Test: No crear notificación si las alertas de presupuesto están desactivadas"""
        # Desactivar alertas de presupuesto
        self.preferences.enable_budget_alerts = False
        self.preferences.save()

        notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        self.assertIsNone(notification)

    def test_create_budget_exceeded(self):
        """Test: Crear notificación de presupuesto excedido"""
        notification = NotificationEngine.create_budget_exceeded(
            user=self.user,
            budget=self.budget,
            spent=Decimal("1050000.00"),
            limit=Decimal("1000000.00"),
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "budget_exceeded")
        self.assertIn("🚨", notification.title)
        self.assertIn("excedido", notification.message.lower())
        self.assertIn("1,050,000", notification.message)

    def test_duplicate_prevention(self):
        """Test: Prevención de notificaciones duplicadas en 24 horas"""
        # Crear primera notificación
        notification1 = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )
        self.assertIsNotNone(notification1)

        # Intentar crear segunda notificación inmediatamente
        notification2 = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=86,
            spent=Decimal("860000.00"),
            limit=Decimal("1000000.00"),
        )
        self.assertIsNone(notification2, "No debe crear duplicado en 24 horas")

        # Verificar que solo hay una notificación
        count = Notification.objects.filter(
            user=self.user, notification_type="budget_warning", related_object_id=self.budget.id
        ).count()
        self.assertEqual(count, 1)

    def test_create_bill_reminder(self):
        """Test: Crear recordatorio de factura"""
        notification = NotificationEngine.create_bill_reminder(
            user=self.user, bill=self.bill, reminder_type="upcoming"
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "bill_reminder")
        self.assertIn("📄", notification.title)
        self.assertIn("Netflix", notification.message)
        self.assertIn("45,000", notification.message)
        self.assertEqual(notification.related_object_type, "bill")

    def test_bill_reminder_disabled(self):
        """Test: No crear recordatorio si están desactivados"""
        self.preferences.enable_bill_reminders = False
        self.preferences.save()

        notification = NotificationEngine.create_bill_reminder(
            user=self.user, bill=self.bill, reminder_type="upcoming"
        )

        self.assertIsNone(notification)

    def test_create_soat_reminder(self):
        """Test: Crear recordatorio de SOAT"""
        notification = NotificationEngine.create_soat_reminder(
            user=self.user,
            soat=self.soat,
            alert_type="upcoming",
            days=15,  # Pasar días explícitamente
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "soat_reminder")
        self.assertIn("🚗", notification.title)
        self.assertIn("ABC123", notification.message)
        self.assertIn("15", notification.message)
        self.assertEqual(notification.related_object_type, "soat")

    def test_soat_reminder_disabled(self):
        """Test: No crear recordatorio de SOAT si están desactivados"""
        self.preferences.enable_soat_reminders = False
        self.preferences.save()

        notification = NotificationEngine.create_soat_reminder(
            user=self.user, soat=self.soat, alert_type="upcoming"
        )

        self.assertIsNone(notification)

    def test_create_month_end_reminder(self):
        """Test: Crear recordatorio de fin de mes"""
        notification = NotificationEngine.create_month_end_reminder(self.user)

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "month_end_reminder")
        self.assertIn("📅", notification.title)
        self.assertIn("extracto", notification.message.lower())
        self.assertEqual(notification.related_object_type, "system")
        self.assertIsNone(notification.related_object_id)

    def test_month_end_reminder_disabled(self):
        """Test: No crear recordatorio de fin de mes si está desactivado"""
        self.preferences.enable_month_end_reminders = False
        self.preferences.save()

        notification = NotificationEngine.create_month_end_reminder(self.user)

        self.assertIsNone(notification)

    def test_create_custom_reminder_notification(self):
        """Test: Crear notificación de recordatorio personalizado"""
        # Crear recordatorio personalizado
        reminder = CustomReminder.objects.create(
            user=self.user,
            title="Reunión con contador",
            message="Llevar documentos del mes",
            reminder_date=timezone.now().date() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )

        notification = NotificationEngine.create_custom_reminder_notification(
            custom_reminder=reminder  # Parámetro correcto
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, "custom_reminder")
        self.assertEqual(notification.title, "Reunión con contador")
        self.assertEqual(notification.message, "Llevar documentos del mes")
        self.assertEqual(notification.related_object_type, "custom_reminder")
        self.assertEqual(notification.related_object_id, reminder.id)

        # Verificar que el reminder fue actualizado
        reminder.refresh_from_db()
        self.assertTrue(reminder.is_sent)
        self.assertIsNotNone(reminder.sent_at)
        self.assertIsNotNone(reminder.notification)
        self.assertEqual(reminder.notification.id, notification.id)

    def test_custom_reminder_disabled(self):
        """Test: No crear notificación de recordatorio si están desactivados"""
        self.preferences.enable_custom_reminders = False
        self.preferences.save()

        reminder = CustomReminder.objects.create(
            user=self.user,
            title="Test reminder",
            message="Test message",
            reminder_date=timezone.now().date() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )

        notification = NotificationEngine.create_custom_reminder_notification(
            custom_reminder=reminder  # Parámetro correcto
        )

        self.assertIsNone(notification)

        # El reminder no debe ser marcado como enviado
        reminder.refresh_from_db()
        self.assertFalse(reminder.is_sent)

    def test_get_pending_custom_reminders(self):
        """Test: Obtener recordatorios personalizados pendientes"""
        # Crear 2 recordatorios: 1 pasado (debe detectarse), 1 futuro (no debe detectarse)
        yesterday = timezone.now() - timedelta(days=1)
        tomorrow = timezone.now() + timedelta(days=1)

        reminder_past = CustomReminder.objects.create(
            user=self.user,
            title="Pasado",
            message="Pasado",
            reminder_date=yesterday.date(),
            reminder_time=yesterday.time(),
        )

        reminder_future = CustomReminder.objects.create(
            user=self.user,
            title="Futuro",
            message="Futuro",
            reminder_date=tomorrow.date(),
            reminder_time=tomorrow.time(),
        )

        # Obtener pendientes (solo el pasado)
        pending = NotificationEngine.get_pending_custom_reminders()

        # Verificar que obtiene el pasado y no el futuro
        pending_ids = [r.id for r in pending]
        self.assertIn(reminder_past.id, pending_ids, "Recordatorio pasado debe estar en pendientes")
        self.assertNotIn(
            reminder_future.id, pending_ids, "Recordatorio futuro no debe estar en pendientes"
        )

    def test_check_month_end_reminders(self):
        """Test: Verificar recordatorios de fin de mes"""
        # Este test solo funciona si se ejecuta el día 28
        current_day = timezone.now().day

        created = NotificationEngine.check_month_end_reminders()

        if current_day == 28:
            # check_month_end_reminders retorna una lista de notificaciones creadas
            self.assertIsInstance(created, list, "Debe retornar una lista")
            self.assertEqual(len(created), 1, "Debe crear 1 notificación el día 28")
            # Verificar que se creó la notificación
            notification = Notification.objects.filter(
                user=self.user, notification_type="month_end_reminder"
            ).first()
            self.assertIsNotNone(notification)
        else:
            # Otros días no crea notificaciones
            self.assertIsInstance(created, list, "Debe retornar una lista")
            self.assertEqual(len(created), 0, "No debe crear notificaciones en otros días")

    def test_user_without_preferences(self):
        """Test: Manejo de usuario sin preferencias configuradas"""
        # Crear usuario sin preferencias
        user_no_prefs = User.objects.create_user(
            username="noprefs",
            email="noprefs@example.com",
            identification="0987654321",
            password="testpass123",
        )

        # Intentar crear notificación
        NotificationEngine.create_budget_warning(
            user=user_no_prefs,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        # No debe crear notificación sin preferencias (o las crea por defecto desactivadas)
        # Verificar que se crearon preferencias automáticamente
        prefs = UserNotificationPreferences.objects.filter(user=user_no_prefs).first()
        self.assertIsNotNone(prefs, "Las preferencias deberían crearse automáticamente")

        # Si las preferencias se crean por defecto con alertas activadas, la notificación existirá
        # Este test verifica que el sistema maneja bien usuarios sin preferencias previas

    def tearDown(self):
        """Limpieza después de los tests"""
        Notification.objects.all().delete()
        CustomReminder.objects.all().delete()
        UserNotificationPreferences.objects.all().delete()
        Budget.objects.all().delete()
        Bill.objects.all().delete()
        SOAT.objects.all().delete()
        Vehicle.objects.all().delete()
        Account.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
