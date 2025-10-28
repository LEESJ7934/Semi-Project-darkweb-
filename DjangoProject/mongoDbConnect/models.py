from django.db import models

# Create your models here.

from djongo import models


class RegisterDb(models.Model):
    _id = models.TextField(primary_key=True)  # 나중에 수정할 부분입니다!
    company_name = models.TextField(null=True)
    company_url = models.TextField(null=True)
    description = models.TextField(null=True)
    publication_date = models.TextField(null=True)
    scraped_time = models.TextField(null=True)
    class Meta:
        db_table = "clawling_data"