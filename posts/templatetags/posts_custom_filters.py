from django import template
from posts.models import Vote

register = template.Library()

@register.filter
def is_up_voted_by_user(post, user):
    return Vote.objects.filter(post=post, voted_by=user, vote_type="1", deleted=False).exists()


@register.filter
def is_down_voted_by_user(post, user):
    return Vote.objects.filter(post=post, voted_by=user, vote_type="-1", deleted=False).exists()


@register.filter
def get_pinned_by_username(pinned_posts):
    pinned_post = pinned_posts.filter(deleted=False).first()
    if pinned_post:
        return pinned_post.pinned_by.username
    return None


@register.filter
def are_pinned_posts_exists(pinned_posts):
    pinned_post = pinned_posts.filter(deleted=False).first()
    if pinned_post:
        return True
    return False