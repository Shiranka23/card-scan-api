from django.db import models

class CardData(models.Model):
    name=models.CharField(max_length=255,null=False, blank=False)
    number=models.CharField(max_length=255, null=False, blank=False)
    email=models.EmailField(max_length=255, null=False, blank=False)
    address=models.TextField()
    image=models.ImageField(upload_to='assets/')

    
    def __str__(self):
        return self.name, self.address