from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Vote
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket
from django.db import transaction, IntegrityError
import json
from accounts.models import CustomerCompanyDetails
from django.urls import reverse

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
                    existing_vote.save(user=request.user)

            # If the user hasn't voted or their previous vote was deleted, create an upvote
            post.up_votes += 1
            Vote.objects.create(voted_by=user, post=post, vote_type=1)
            post.save(user=request.user)
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
                    existing_vote.save(user=request.user)

            # If the user hasn't voted or their previous vote was deleted, create an upvote
            post.down_votes += 1
            Vote.objects.create(voted_by=user, post=post, vote_type=-1)
            post.save(user=request.user)
            return JsonResponse({"success": True, "data": [post.up_votes, post.down_votes]})
        except:
            return JsonResponse({'success': False, 'error': 'Post not found.'}, status=HTTPStatus.NOT_FOUND)
    else:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=HTTPStatus.BAD_REQUEST)


@login_required
def ticket_posts(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    posts = Post.objects.filter(ticket=ticket).order_by('-created_at')  # Fetch posts related to the ticket

    return render(request, 'posts/ticket_posts.html', {
        'ticket': ticket,
        'posts': posts,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        old_post = ''
        try:
            data = request.POST
            # required_fields = ['content', 'ticket_id', 'post_id']
            required_fields = ['content', 'ticket_id']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'content' in data:
                content = data.get('content')

            if 'ticket_id' in data:
                ticket_id = data.get('ticket_id')

            if 'post_id' in data:
                post_id = data.get('post_id')

            # Basic validation
            errors = []
            if not content:
                errors.append("content is required.")
            if not ticket_id:
                errors.append("ticket_id is required.")
            # if not post_id:
            #     errors.append("post_id is required.")

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                tickets = Ticket.objects.filter(id=ticket_id)
                if tickets.exists():
                    ticket = tickets.first()
                if post_id:
                    posts = Post.objects.filter(id=post_id)
                    if posts.exists():
                        old_post = posts.first()
                post = Post()
                post.content=content
                post.ticket=ticket
                if old_post:
                    post.parent_post = old_post
                post.save(user=request.user)

            url = reverse('posts:ticket_posts', kwargs={'ticket_id': ticket_id})
            return redirect(url)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)