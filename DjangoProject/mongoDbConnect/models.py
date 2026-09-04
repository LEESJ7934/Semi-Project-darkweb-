from django.db import models


class RegisterDb(models.Model):
    _id = models.TextField(primary_key=True)
    company_name = models.TextField(null=True)
    company_url = models.TextField(null=True)
    country = models.TextField(null=True)
    data_contents = models.TextField(null=True)
    data_size = models.TextField(null=True)
    description = models.TextField(null=True)
    publication_date = models.TextField(null=True)
    scraped_time = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = "leaked_data"

    def __str__(self):
        return self.company_name or self._id