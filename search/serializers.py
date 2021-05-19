from rest_framework import serializers

from .models import Search


class SimpleSearchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    search_type = serializers.IntegerField(required=True)
    search_terms = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=False)

    class Meta:
        model = Search
        depth = 1
        fields = [
            "id",
            "search_type",
            "search_terms",
            "user_id",
        ]
