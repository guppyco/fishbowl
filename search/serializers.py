from rest_framework import serializers

from .models import History, Search


class SimpleSearchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    search_type = serializers.IntegerField(required=True)
    search_terms = serializers.CharField(required=True)

    class Meta:
        model = Search
        depth = 1
        fields = [
            "id",
            "search_type",
            "search_terms",
            "user_id",
        ]


class HistorySerialzer(serializers.ModelSerializer):
    url = serializers.URLField(max_length=2048, required=True)
    title = serializers.CharField(max_length=1000, required=False)
    last_origin = serializers.URLField(max_length=2048, required=False)

    class Meta:
        model = History
        depth = 1
        fields = "__all__"
