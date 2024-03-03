from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pict')
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True,)

    def __str__(self):
        return f'{self.user.username} Profile'

    def total_following(self):
        return self.follows.count()

    def total_followers(self):
        return self.followed_by.count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 and img.width > 300:
            new_size = (300, 300)
            img.thumbnail(new_size)
            img.save(self.image.path)


