"""
Modelos para reglas automáticas de categorización (HU-12)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class AutomaticRule(models.Model):
    """
    Modelo para reglas automáticas que asignan categorías o etiquetas
    a transacciones basándose en criterios definidos por el usuario.
    """

    # Tipos de criterio
    DESCRIPTION_CONTAINS = "description_contains"
    TRANSACTION_TYPE = "transaction_type"

    CRITERIA_CHOICES = [
        (DESCRIPTION_CONTAINS, "Descripción contiene texto"),
        (TRANSACTION_TYPE, "Tipo de transacción"),
    ]

    # Tipos de acción
    ASSIGN_CATEGORY = "assign_category"
    ASSIGN_TAG = "assign_tag"

    ACTION_CHOICES = [
        (ASSIGN_CATEGORY, "Asignar categoría"),
        (ASSIGN_TAG, "Asignar etiqueta"),
    ]

    # Tipos de transacción para reglas
    INCOME = 1
    EXPENSE = 2
    TRANSFER = 3
    SAVING = 4

    TRANSACTION_TYPE_CHOICES = [
        (INCOME, "Ingresos"),
        (EXPENSE, "Gastos"),
        (TRANSFER, "Transferencias"),
        (SAVING, "Ahorros"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="automatic_rules",
        verbose_name="Usuario",
        help_text="Usuario propietario de la regla",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre de la regla",
        help_text="Nombre descriptivo para identificar la regla",
    )

    criteria_type = models.CharField(
        max_length=50,
        choices=CRITERIA_CHOICES,
        verbose_name="Tipo de criterio",
        help_text="Tipo de criterio para aplicar la regla",
    )

    # Para criterio DESCRIPTION_CONTAINS
    keyword = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Palabra clave",
        help_text="Texto que debe contener la descripción (insensible a mayúsculas)",
    )

    # Para criterio TRANSACTION_TYPE
    target_transaction_type = models.IntegerField(
        choices=TRANSACTION_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Tipo de transacción objetivo",
        help_text="Tipo de transacción al que aplicar la regla",
    )

    action_type = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name="Tipo de acción",
        help_text="Acción a realizar cuando se cumpla el criterio",
    )

    # Para acción ASSIGN_CATEGORY
    target_category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rules",
        verbose_name="Categoría objetivo",
        help_text="Categoría a asignar cuando se aplique la regla",
    )

    # Para acción ASSIGN_TAG
    target_tag = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Etiqueta objetivo",
        help_text="Etiqueta a asignar cuando se aplique la regla",
    )

    is_active = models.BooleanField(
        default=True, verbose_name="Activa", help_text="Si la regla está activa y se puede aplicar"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de aplicación (menor número = mayor prioridad)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Regla automática"
        verbose_name_plural = "Reglas automáticas"
        ordering = ["order", "created_at"]
        unique_together = [["user", "name"]]

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar que los campos requeridos según el criterio estén presentes
        if self.criteria_type == self.DESCRIPTION_CONTAINS:
            if not self.keyword:
                raise ValidationError(
                    {
                        "keyword": 'La palabra clave es requerida para criterio "descripción contiene texto"'
                    }
                )
        elif self.criteria_type == self.TRANSACTION_TYPE:
            if self.target_transaction_type is None:
                raise ValidationError(
                    {
                        "target_transaction_type": 'El tipo de transacción es requerido para criterio "tipo de transacción"'
                    }
                )

        # Validar que los campos requeridos según la acción estén presentes
        if self.action_type == self.ASSIGN_CATEGORY:
            if not self.target_category:
                raise ValidationError(
                    {
                        "target_category": 'La categoría objetivo es requerida para acción "asignar categoría"'
                    }
                )
        elif self.action_type == self.ASSIGN_TAG:
            if not self.target_tag:
                raise ValidationError(
                    {
                        "target_tag": 'La etiqueta objetivo es requerida para acción "asignar etiqueta"'
                    }
                )

        # Validar que la categoría objetivo pertenezca al usuario
        if self.target_category and self.target_category.user != self.user:
            raise ValidationError(
                {"target_category": "La categoría objetivo debe pertenecer al mismo usuario"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def matches_transaction(self, transaction):
        """
        Verifica si esta regla aplica a una transacción dada.

        Args:
            transaction: Instancia de Transaction

        Returns:
            bool: True si la regla aplica, False en caso contrario
        """
        if not self.is_active:
            return False

        if self.criteria_type == self.DESCRIPTION_CONTAINS:
            if not transaction.description:
                return False
            return self.keyword.lower() in transaction.description.lower()

        elif self.criteria_type == self.TRANSACTION_TYPE:
            return transaction.type == self.target_transaction_type

        return False

    def apply_to_transaction(self, transaction):
        """
        Aplica esta regla a una transacción.

        Args:
            transaction: Instancia de Transaction

        Returns:
            dict: Información sobre qué se aplicó
        """
        result = {
            "applied": False,
            "rule_name": self.name,
            "action_type": self.action_type,
            "changes": {},
        }

        if not self.matches_transaction(transaction):
            return result

        if self.action_type == self.ASSIGN_CATEGORY:
            transaction.category = self.target_category
            result["changes"]["category"] = self.target_category.name

        elif self.action_type == self.ASSIGN_TAG:
            transaction.tag = self.target_tag
            result["changes"]["tag"] = self.target_tag

        transaction.applied_rule = self
        result["applied"] = True

        return result

    def __str__(self):
        return f"{self.name} - {self.get_criteria_type_display()}"
