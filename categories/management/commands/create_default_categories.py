"""
Management command para crear categorías por defecto para usuarios
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from categories.models import Category
from categories.services import CategoryService

User = get_user_model()


class Command(BaseCommand):
    help = "Crea categorías por defecto para usuarios especificados o para todos los usuarios"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="ID de usuario específico para crear categorías",
        )
        parser.add_argument(
            "--all-users",
            action="store_true",
            help="Crear categorías para todos los usuarios que no tengan",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forzar creación incluso si el usuario ya tiene categorías",
        )

    def handle(self, *args, **options):
        user_id = options.get("user_id")
        all_users = options.get("all_users")
        force = options.get("force")

        if user_id:
            # Crear para un usuario específico
            try:
                user = User.objects.get(pk=user_id)
                self.create_categories_for_user(user, force)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Usuario con ID {user_id} no existe"))
                return

        elif all_users:
            # Crear para todos los usuarios
            users = User.objects.all()
            created_count = 0
            skipped_count = 0

            for user in users:
                result = self.create_categories_for_user(user, force)
                if result:
                    created_count += 1
                else:
                    skipped_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"\nResumen:\n"
                    f"- Usuarios procesados: {created_count}\n"
                    f"- Usuarios omitidos: {skipped_count}"
                )
            )

        else:
            self.stdout.write(self.style.ERROR("Debes especificar --user-id <ID> o --all-users"))

    def create_categories_for_user(self, user, force=False):
        """
        Crear categorías por defecto para un usuario específico

        Args:
            user: Usuario para el que crear categorías
            force: Si True, crea categorías incluso si ya tiene

        Returns:
            bool: True si se crearon categorías, False si se omitió
        """
        # Verificar si ya tiene categorías
        existing_count = Category.objects.filter(user=user).count()

        if existing_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"Usuario {user.username} (ID: {user.id}) ya tiene "
                    f"{existing_count} categorías. Omitiendo..."
                )
            )
            return False

        if existing_count > 0 and force:
            self.stdout.write(
                self.style.WARNING(
                    f"Usuario {user.username} (ID: {user.id}) ya tiene "
                    f"{existing_count} categorías, pero se forzará la creación..."
                )
            )

        # Crear categorías por defecto
        try:
            created_categories = CategoryService.create_default_categories(user)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Creadas {len(created_categories)} categorías por defecto "
                    f"para usuario {user.username} (ID: {user.id})"
                )
            )

            # Mostrar resumen por tipo
            income_count = sum(1 for cat in created_categories if cat.type == Category.INCOME)
            expense_count = sum(1 for cat in created_categories if cat.type == Category.EXPENSE)

            self.stdout.write(f"  - Categorías de ingresos: {income_count}")
            self.stdout.write(f"  - Categorías de gastos: {expense_count}")

            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"✗ Error al crear categorías para usuario {user.username} "
                    f"(ID: {user.id}): {e!s}"
                )
            )
            return False
