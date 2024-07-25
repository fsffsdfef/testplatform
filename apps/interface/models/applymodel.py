from apps.management.models import BaseModel, Depart
from django.db import models


class Apply(BaseModel):
    app_id = models.CharField(max_length=100, primary_key=True)
    app_name = models.CharField(verbose_name='应用名', max_length=30, unique=True)
    domains = models.URLField(verbose_name='域名', unique=True)
    depart = models.ForeignKey(to=Depart, to_field='depart_id', related_name='app', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_apply'

    def __str__(self):
        return self.app_name

    def save(self, *args, **kwargs):
        if not self.app_id:
            self.app_id = self.get_random_number(field_name='app_id', length=5, prefix='1000')
        super().save(*args, **kwargs)
