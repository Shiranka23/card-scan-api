from django.db import models

def upload_location(instance, filename):
    extension=filename.split()[-1]
    # print(filename,extension)
    # print(instance.name)
    return 'assets/%s' % (instance.name)

class CardData(models.Model):
    name=models.CharField(max_length=150,null=False, blank=False)
    image=models.ImageField(upload_to=upload_location)

    
    def __str__(self):
        return self.name