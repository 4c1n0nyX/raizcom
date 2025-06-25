from django.db import models
from django.conf import settings

# =============== Modelo de Contactos ================ #
class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_contacts',
        verbose_name="Usuario"
    )
    contact_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='is_contact_of',
        verbose_name="Contacto"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pendiente'), 
        ('accepted', 'Aceptada'), 
        ('rejected', 'Rechazada'), 
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('user', 'contact_user')
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"

    def __str__(self):
        return f"{self.user.username} tiene como contacto a {self.contact_user.username} (Estado: {self.status})"

    def accept_request(self):
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            Contact.objects.update_or_create(
                user=self.contact_user, 
                contact_user=self.user,
                defaults={'status': 'accepted'}
            )
            return True
        return False

    def reject_request(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False
