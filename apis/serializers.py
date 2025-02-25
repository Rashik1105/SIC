from rest_framework import serializers

class LeaderboardEntrySerializer(serializers.Serializer):
    user = serializers.CharField()
    platform = serializers.CharField()
    score = serializers.FloatField()

class CombinedLeaderboardEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.CharField()
    score = serializers.FloatField()
    channel_category = serializers.CharField()
