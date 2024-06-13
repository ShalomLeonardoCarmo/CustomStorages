from django.db import models
from AcampsBK.storage import SupabaseStorage

# Create your models here.

class Images(models.Model):
    name = models.CharField(max_length=50, null=False)

    image = models.ImageField(upload_to='uploads/', storage=SupabaseStorage)
