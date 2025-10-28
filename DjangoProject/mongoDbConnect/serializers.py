from rest_framework import serializers
from mongoDbConnect.models import RegisterDb


class PreprocessedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterDb
        # fields = '__all__'
        fields = ["company_name", "company_url","description","publication_date"]
        read_only_fields = ["_id"]