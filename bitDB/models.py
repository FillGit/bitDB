from django.db import models

# Create your models here.

class Element(models.Model):

    value = models.CharField(max_length=50,
                             help_text="Value of element")
    changed = models.DateTimeField(auto_now=True)

    parentID = models.PositiveIntegerField()
    level = models.PositiveIntegerField()

    status = models.BooleanField(default=True)

    def save_instance(self, **kwargs):
        instance = kwargs.pop('instance')
        self.id=instance['id']
        self.value=instance['value']
        self.parentID=instance['parentID']
        self.level=instance['level']
        self.status=instance['status']
        self.save()

    def save(self, *args, **kwargs):
        super(Element, self).save(*args, **kwargs)

    def __str__(self):
        return self.value
