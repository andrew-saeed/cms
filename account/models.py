from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True
    )

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return f'https://ui-avatars.com/api/?name={self.user.username}&background=d1d5dc&color=000&bold=true&font-size=0.38'
    
@receiver(pre_save, sender=Profile)
def delete_old_photo(sender, instance, **kwargs):
    if not instance.pk:
        return False
    
    try:
        old_instance = Profile.objects.get(pk=instance.pk)
        if old_instance.photo and old_instance.photo != instance.photo:
            old_instance.photo.delete(save=False)
    except Profile.DoesNotExist:
        pass