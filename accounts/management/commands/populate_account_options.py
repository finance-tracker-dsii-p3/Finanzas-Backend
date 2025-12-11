"""
Management command para poblar las opciones de bancos, billeteras y tarjetas
"""

from django.core.management.base import BaseCommand

from accounts.models import AccountOption, AccountOptionType


class Command(BaseCommand):
    help = "Pobla las opciones de bancos, billeteras y tarjetas de crédito"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forzar creación incluso si ya existen las opciones",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)

        # Poblar bancos
        banks = [
            "Bancolombia",
            "Banco de Bogotá",
            "Davivienda",
            "Banco Popular",
            "Banco AV Villas",
            "Banco Agrario",
            "Banco Caja Social",
            "Banco Falabella",
            "Banco Pichincha",
            "BBVA Colombia",
            "Citibank",
            "Scotiabank Colpatria",
            "Otro",
        ]

        self.stdout.write(self.style.WARNING("\nPoblando bancos..."))
        for i, bank in enumerate(banks):
            obj, created = AccountOption.objects.get_or_create(
                name=bank,
                option_type=AccountOptionType.BANK,
                defaults={"order": i, "is_active": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Creado: {bank}"))
            elif force:
                obj.order = i
                obj.is_active = True
                obj.save()
                self.stdout.write(self.style.WARNING(f"  ↻ Actualizado: {bank}"))
            else:
                self.stdout.write(self.style.NOTICE(f"  - Ya existe: {bank}"))

        # Poblar billeteras
        wallets = ["Nequi", "Daviplata", "RappiPay", "Ualá", "Lulo Bank", "Nu Colombia", "Otro"]

        self.stdout.write(self.style.WARNING("\nPoblando billeteras..."))
        for i, wallet in enumerate(wallets):
            obj, created = AccountOption.objects.get_or_create(
                name=wallet,
                option_type=AccountOptionType.WALLET,
                defaults={"order": i, "is_active": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Creado: {wallet}"))
            elif force:
                obj.order = i
                obj.is_active = True
                obj.save()
                self.stdout.write(self.style.WARNING(f"  ↻ Actualizado: {wallet}"))
            else:
                self.stdout.write(self.style.NOTICE(f"  - Ya existe: {wallet}"))

        # Poblar bancos para tarjetas
        credit_card_banks = [
            "Bancolombia",
            "Banco de Bogotá",
            "Davivienda",
            "Banco Popular",
            "Falabella",
            "Éxito",
            "Alkosto",
            "Otro",
        ]

        self.stdout.write(self.style.WARNING("\nPoblando bancos para tarjetas de crédito..."))
        for i, bank in enumerate(credit_card_banks):
            obj, created = AccountOption.objects.get_or_create(
                name=bank,
                option_type=AccountOptionType.CREDIT_CARD_BANK,
                defaults={"order": i, "is_active": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Creado: {bank}"))
            elif force:
                obj.order = i
                obj.is_active = True
                obj.save()
                self.stdout.write(self.style.WARNING(f"  ↻ Actualizado: {bank}"))
            else:
                self.stdout.write(self.style.NOTICE(f"  - Ya existe: {bank}"))

        # Resumen
        total_banks = AccountOption.objects.filter(option_type=AccountOptionType.BANK).count()
        total_wallets = AccountOption.objects.filter(option_type=AccountOptionType.WALLET).count()
        total_credit_banks = AccountOption.objects.filter(
            option_type=AccountOptionType.CREDIT_CARD_BANK
        ).count()

        self.stdout.write(self.style.SUCCESS("\nProceso completado!"))
        self.stdout.write(self.style.SUCCESS("\nResumen:"))
        self.stdout.write(self.style.SUCCESS(f"  - Bancos: {total_banks}"))
        self.stdout.write(self.style.SUCCESS(f"  - Billeteras: {total_wallets}"))
        self.stdout.write(self.style.SUCCESS(f"  - Bancos para tarjetas: {total_credit_banks}"))
        self.stdout.write(
            self.style.SUCCESS(
                f"  - Total: {total_banks + total_wallets + total_credit_banks} opciones"
            )
        )
