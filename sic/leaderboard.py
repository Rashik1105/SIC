from .models import InfluencerMetrics, SocialPlatform
from django.db.models import Max
from django.db.models import Max, Sum

def calculate_leaderboard():
    """
    Fetch influencer metrics, normalize scores, and rank influencers.
    """

    # Step 1: Get Max values across all influencers & platforms
    max_values = InfluencerMetrics.objects.aggregate(
        max_views=Max('views'),
        max_likes=Max('likes'),
        max_comments=Max('comments')
    )

    max_views = max_values['max_views'] or 1  # Avoid division by zero
    max_likes = max_values['max_likes'] or 1
    max_comments = max_values['max_comments'] or 1

    leaderboard = []

    # Step 2: Fetch influencer metrics & compute score
    influencers = InfluencerMetrics.objects.all()
    
    for influencer in influencers:
        normalized_views = influencer.views / max_views
        normalized_likes = influencer.likes / max_likes
        normalized_comments = influencer.comments / max_comments

        # Weighted Score Formula
        final_score = (normalized_views * 0.5) + (normalized_likes * 0.3) + (normalized_comments * 0.2)

        leaderboard.append({
            "user": influencer.user,
            "platform": influencer.platform.name,
            "score": round(final_score, 4)
        })

    # Step 3: Sort by score in descending order
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    return leaderboard


def calculate_combined_leaderboard():
    """
    Fetch influencer metrics across all platforms, aggregate data, normalize scores, and rank influencers.
    """

    # Step 1: Get max values across all influencers & platforms
    max_values = InfluencerMetrics.objects.aggregate(
        max_views=Max('views'),
        max_likes=Max('likes'),
        max_comments=Max('comments')
    )

    max_views = max_values['max_views'] or 1  # Avoid division by zero
    max_likes = max_values['max_likes'] or 1
    max_comments = max_values['max_comments'] or 1

    leaderboard = []

    # Step 2: Aggregate influencer data across all platforms
    influencers = InfluencerMetrics.objects.values('user').annotate(
        total_views=Sum('views'),
        total_likes=Sum('likes'),
        total_comments=Sum('comments')
    )

    for influencer in influencers:
        normalized_views = influencer['total_views'] / max_views
        normalized_likes = influencer['total_likes'] / max_likes
        normalized_comments = influencer['total_comments'] / max_comments

        # Weighted Score Formula
        final_score = (normalized_views * 0.5) + (normalized_likes * 0.3) + (normalized_comments * 0.2)

        leaderboard.append({
            "user": influencer['user'],
            "score": round(final_score, 4)
        })

    # Step 3: Sort by score in descending order
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    return leaderboard
