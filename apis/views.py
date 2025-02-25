from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Max, Sum
from django.db.models.functions import Coalesce
from sic.models import InfluencerMetrics, YoutubeUser
from .serializers import LeaderboardEntrySerializer, CombinedLeaderboardEntrySerializer

@api_view(['GET'])
def calculate_leaderboard_api(request):
    """
    API to fetch, normalize, and rank influencers per platform.
    """
    max_values = InfluencerMetrics.objects.aggregate(
        max_views=Max('views'),
        max_likes=Max('likes'),
        max_comments=Max('comments')
    )

    max_views = max_values['max_views'] or 1  # Avoid division by zero
    max_likes = max_values['max_likes'] or 1
    max_comments = max_values['max_comments'] or 1

    leaderboard = []

    influencers = InfluencerMetrics.objects.select_related('user__youtubeuser', 'platform').all()

    for influencer in influencers:
        normalized_views = influencer.views / max_views
        normalized_likes = influencer.likes / max_likes
        normalized_comments = influencer.comments / max_comments

        final_score = (normalized_views * 0.5) + (normalized_likes * 0.3) + (normalized_comments * 0.2)

        leaderboard.append({
            "user": influencer.user.youtubeuser.channel_name,
            "platform": influencer.platform.name,
            "score": round(final_score, 4)
        })

    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    serializer = LeaderboardEntrySerializer(leaderboard, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def calculate_combined_leaderboard_api(request):
    """
    API to fetch, aggregate, normalize, and rank influencers across all platforms.
    """
    max_values = InfluencerMetrics.objects.aggregate(
        max_views=Max('views'),
        max_likes=Max('likes'),
        max_comments=Max('comments')
    )

    max_views = max_values['max_views'] if max_values['max_views'] else 1
    max_likes = max_values['max_likes'] if max_values['max_likes'] else 1
    max_comments = max_values['max_comments'] if max_values['max_comments'] else 1

    leaderboard = []

    influencers = InfluencerMetrics.objects.values('user').annotate(
        total_views=Coalesce(Sum('views'), 0),
        total_likes=Coalesce(Sum('likes'), 0),
        total_comments=Coalesce(Sum('comments'), 0)
    )

    youtube_users = {yu.user_id: yu for yu in YoutubeUser.objects.all()}

    for influencer in influencers:
        user_id = influencer['user']
        yt_user = youtube_users.get(user_id)

        normalized_views = influencer['total_views'] / max_views
        normalized_likes = influencer['total_likes'] / max_likes
        normalized_comments = influencer['total_comments'] / max_comments
        final_score = (normalized_views * 0.5) + (normalized_likes * 0.3) + (normalized_comments * 0.2)

        leaderboard.append({
            "id": yt_user.id if yt_user else user_id,
            "user": yt_user.channel_name if yt_user else f"User-{user_id}",
            "score": round(final_score, 4),
            "channel_category": yt_user.channel_category.name if yt_user else "Unknown"
        })

    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    serializer = CombinedLeaderboardEntrySerializer(leaderboard, many=True)
    return Response(serializer.data)