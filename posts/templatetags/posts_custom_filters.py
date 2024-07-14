from django import template
from posts.models import Vote, SavedPost

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


@register.filter
def get_saved_by_username(saved_posts):
    saved_post = saved_posts.filter(saved=SavedPost.Saved.YES).first()
    if saved_post:
        return saved_post.saved_by.full_name
    return None


@register.filter
def are_saved_posts_exists(saved_posts):
    saved_post = saved_posts.filter(saved=SavedPost.Saved.YES).first()
    if saved_post:
        return True
    return False