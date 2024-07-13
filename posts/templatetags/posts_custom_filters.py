from django import template
from posts.models import Vote

register = template.Library()

@register.filter
def is_up_voted_by_user(post, user):
    return Vote.objects.filter(post=post, voted_by=user, vote_type="1", deleted=False).exists()


@register.filter
def is_down_voted_by_user(post, user):
    return Vote.objects.filter(post=post, voted_by=user, vote_type="-1", deleted=False).exists()
