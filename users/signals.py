from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import User
from notifications.models import Notification
from .email_utils import send_email_unified


# Signal deshabilitado - Los usuarios se auto-verifican automáticamente
# Los nuevos usuarios no requieren aprobación de administrador

@receiver(post_save, sender=User)
def auto_verify_new_users(sender, instance, created, **kwargs):
    """
    Auto-verifica usuarios recién creados.
    Los usuarios ya no requieren aprobación de administrador.
    """
    # Evitar bucles infinitos - solo ejecutar en la creación inicial
    if created and not instance.is_verified:
        # Usar update para evitar disparar signals nuevamente
        User.objects.filter(pk=instance.pk).update(
            is_verified=True,
            verification_date=timezone.now()
        )
        # Actualizar la instancia en memoria para reflejar los cambios
        instance.is_verified = True
        instance.verification_date = timezone.now()



@receiver(post_save, sender=User)
def notify_user_verification_status(sender, instance, **kwargs):
    """
    Notifica al usuario cuando su estado de verificación cambia
    """
    if hasattr(instance, '_verification_changed'):
        if instance.is_verified:
            verifier_name = (
                instance.verified_by.get_full_name()
                if getattr(instance, 'verified_by', None) else 'un administrador'
            )

            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='¡Cuenta verificada!',
                message=(
                    f'Tu cuenta ha sido verificada exitosamente por {verifier_name}. '
                    f'Ya puedes acceder a todas las funcionalidades del sistema.'
                ),
                related_object_id=instance.id,
            )
            try:
                send_email_unified(
                    to=instance.email,
                    subject='[DS2] Tu cuenta ha sido verificada',
                    text_content=(
                        f'Hola {instance.get_full_name()},\n\n'
                        f'Tu cuenta fue verificada por {verifier_name}.\n'
                        f'Ya puedes iniciar sesión y usar la plataforma.\n\n'
                        f'Saludos.'
                    )
                )
            except Exception as e:
                print(f"[EMAIL_ERROR] Error enviando email de verificación: {e}")
        else:
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='Verificación de cuenta',
                message='Tu solicitud de verificación ha sido procesada. Contacta al administrador para más información.',
                related_object_id=instance.id,
            )
            try:
                send_email_unified(
                    to=instance.email,
                    subject='[DS2] Actualización de verificación de cuenta',
                    text_content=(
                        f'Hola {instance.get_full_name()},\n\n'
                        f'Tu cuenta no ha sido verificada en este momento. '
                        f'Si crees que es un error, por favor contacta al administrador.\n\n'
                        f'Saludos.'
                    )
                )
            except Exception as e:
                print(f"[EMAIL_ERROR] Error enviando email de actualización: {e}")

        delattr(instance, '_verification_changed')


@receiver(post_delete, sender=User)
def notify_user_on_delete(sender, instance, **kwargs):
    """
    Envía correo al usuario cuando su cuenta es eliminada
    (por admin vía panel o endpoint)
    """
    if instance.email:
        try:
            send_email_unified(
                to=instance.email,
                subject='[DS2] Tu cuenta ha sido eliminada',
                text_content=(
                    f'Hola {instance.get_full_name()},\n\n'
                    f'Tu registro ha sido eliminado por un administrador. '
                    f'Si necesitas más información, por favor contáctanos.\n\n'
                    f'Saludos.'
                )
            )
        except Exception as e:
            print(f"[EMAIL_ERROR] Error enviando email de eliminación: {e}")

