from django.shortcuts import get_object_or_404
from .models import Post, Vote
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def upvote_post(request, post_id):
    if request.method == "POST" and request.is_ajax():
        try:
            post = get_object_or_404(Post, pk=post_id)
            user = request.user

            # Check if the user has already voted
            existing_vote = Vote.objects.filter(voted_by=user, post=post, deleted=False).first()
            if existing_vote:
                if existing_vote.vote_type == 1:
                    return JsonResponse({'success': False, 'message': 'Already upvoted.'})
                else:
                    post.down_votes -= 1
                    existing_vote.vote_type = 1
                    existing_vote.save()

            # If the user hasn't voted or their previous vote was deleted, create an upvote
            post.up_votes += 1
            Vote.objects.create(voted_by=user, post=post, vote_type=1)
            post.save()
            return JsonResponse({"success": True, "data": [post.up_votes, post.down_votes]})
        except:
            return JsonResponse({'success': False, 'error': 'Post not found.'}, status=HTTPStatus.NOT_FOUND)
    else:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=HTTPStatus.BAD_REQUEST)

@login_required
def downvote_post(request, post_id):
    if request.method == "POST" and request.is_ajax():
        try:
            post = get_object_or_404(Post, pk=post_id)
            user = request.user

            # Check if the user has already voted
            existing_vote = Vote.objects.filter(voted_by=user, post=post, deleted=False).first()
            if existing_vote:
                if existing_vote.vote_type == -1:
                    return JsonResponse({'success': False, 'message': 'Already down voted.'})
                else:
                    post.up_votes -= 1
                    existing_vote.vote_type = -1
                    existing_vote.save()

            # If the user hasn't voted or their previous vote was deleted, create an upvote
            post.down_votes += 1
            Vote.objects.create(voted_by=user, post=post, vote_type=-1)
            post.save()
            return JsonResponse({"success": True, "data": [post.up_votes, post.down_votes]})
        except:
            return JsonResponse({'success': False, 'error': 'Post not found.'}, status=HTTPStatus.NOT_FOUND)
    else:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=HTTPStatus.BAD_REQUEST)

