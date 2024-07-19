from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Vote, PinnedPost, SavedPost
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket
from django.db import transaction, IntegrityError
import json
from accounts.models import CustomerCompanyDetails
from django.urls import reverse
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from django.db.models import Q  # For complex queries
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
@login_required
def ticket_posts(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    posts = Post.objects.filter(ticket=ticket, deleted=Post.Deleted.NO).order_by('-created_at')  # Fetch posts related to the ticket
    posted_users = []
    for post in posts:
        posted_users.append(post.created_by)
    posted_users = list(set(posted_users))
    return render(request, 'posts/ticket_posts.html', {
        'ticket': ticket,
        'posts': posts,
        'posted_users': posted_users,
    })

@login_required 
def delete_post(request, post_id): # we will make only soft deletions.
    post = get_object_or_404(Post, pk=post_id)
    post.deleted = Post.Deleted.YES
    post.save(user=request.user)
    url = reverse('posts:ticket_posts', kwargs={'ticket_id': post.ticket.id})
    return redirect(url)

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

@login_required
def vote_post(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        vote_type = request.POST.get('vote_type')
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        # Check if the user has already voted
        existing_vote = Vote.objects.filter(voted_by=user, post=post, deleted=False).first()
        if vote_type == "1":
            if existing_vote:
                if existing_vote.vote_type == 1:
                    return JsonResponse({'success': False, 'message': 'Already up voted.'})
                else:
                    post.down_votes -= 1
                    existing_vote.vote_type = 1
                    existing_vote.save(user=request.user)
            else:
                # If the user hasn't voted or their previous vote was deleted, create an upvote
                Vote.objects.create(voted_by=user, post=post, vote_type=1)
            post.up_votes += 1
        if vote_type == "-1":
            if existing_vote:
                if existing_vote.vote_type == -1:
                    return JsonResponse({'success': False, 'message': 'Already down voted.'})
                else:
                    post.up_votes -= 1
                    existing_vote.vote_type = -1
                    existing_vote.save(user=request.user)
            else:
                # If the user hasn't voted or their previous vote was deleted, create an upvote
                Vote.objects.create(voted_by=user, post=post, vote_type=-1)
            post.down_votes += 1
        post.save(user=request.user)
        return JsonResponse({"success": True, "data": {'up_votes': post.up_votes, 'down_votes': post.down_votes}})

@login_required
def pin_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # Check if the post is already pinned
    existing_pin = PinnedPost.objects.filter(post=post, deleted=False).first()
    
    if existing_pin:
        return JsonResponse({'success': False, 'message': 'Post is already pinned.'})
    
    # Create a new pinned post record
    pinned_post = PinnedPost(post=post, pinned_by=request.user, deleted=False)
    pinned_post.save()
    
    url = reverse('posts:ticket_posts', kwargs={'ticket_id': post.ticket.id})
    return redirect(url)

@login_required
def unpin_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if the post is pinned by the current user
    pinned_post = PinnedPost.objects.filter(post=post, pinned_by=request.user, deleted=False).first()
    
    if not pinned_post:
        return JsonResponse({'success': False, 'message': 'Post is not pinned by current user. You can not un pin this.'})
    
    # Soft delete the pinned post record
    pinned_post.deleted = True
    pinned_post.save()
    
    url = reverse('posts:ticket_posts', kwargs={'ticket_id': post.ticket.id})
    return redirect(url)

@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    saved_post, created = SavedPost.objects.get_or_create(post=post, saved_by=request.user, defaults={'saved': SavedPost.Saved.YES})

    if not created:
        # If the post was already saved, mark it as saved again if it was unsaved
        saved_post.saved = SavedPost.Saved.YES
        saved_post.save(user=request.user)

    url = reverse('posts:ticket_posts', kwargs={'ticket_id': post.ticket.id})
    return redirect(url)

@login_required
def un_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    saved_post = get_object_or_404(SavedPost, post=post, saved_by=request.user)
    saved_post.saved = SavedPost.Saved.NO
    saved_post.save(user=request.user)

    url = reverse('posts:ticket_posts', kwargs={'ticket_id': post.ticket.id})
    return redirect(url)

@login_required
def filter_posts(request, ticket_id):
    if request.method == "POST":
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        posts = Post.objects.filter(ticket=ticket, deleted=Post.Deleted.NO) # Fetch posts related to the ticket

        search = request.POST.get('search', '')
        sort_by_date = request.POST.get('sort_by_date')
        posted_by = request.POST.get('posted_by')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        accepted_answer = request.POST.get('accepted_answer')
        saved_posts = request.POST.get('saved_posts')
        my_posts = request.POST.get('my_posts')
        admin_posts = request.POST.get('admin_posts')
        pinned_posts = request.POST.get('pinned_posts')
        top_voted_posts = request.POST.get('top_voted_posts')
        top_saved_posts = request.POST.get('top_saved_posts')
        has_mentions = request.POST.get('has_mentions')
        has_previews = request.POST.get('has_previews')
        has_links = request.POST.get('has_links')
        has_attachments = request.POST.get('has_attachments')
        has_tables = request.POST.get('has_tables')
        
        # Convert strings to datetime objects
        start_date = parse_datetime(start_date) if start_date else None
        end_date = parse_datetime(end_date) if end_date else None

        if search:
            search_query = Q(content__icontains=search)  # Adjust this if you want to search in different fields
            posts = posts.filter(search_query)

        # sort by date
        if sort_by_date == 'oldest':
            posts = posts.order_by('created_at')
        else:
            posts = posts.order_by('-created_at')

        # Filter by posted_by
        if posted_by:
            posted_by_user = User.objects.get(id=posted_by)
            posts = posts.filter(created_by__username=posted_by_user)
        
        # Filter posts based on the provided dates
        if start_date and not end_date:
            # Filter latest posts if only start_date exists
            posts = posts.filter(created_at__gte=start_date).order_by('-created_at')
        elif end_date and not start_date:
            # Filter old posts if only end_date exists
            posts = posts.filter(created_at__lte=end_date).order_by('created_at')
        elif start_date and end_date:
            # Filter posts within the date range if both dates exist
            posts = posts.filter(created_at__range=(start_date, end_date)).order_by('-created_at')

        # Filter by accepted answer
        if accepted_answer == "on":
            posts = posts.filter(accepted_solution=True)
        
        # Filter by saved posts
        if saved_posts == "on":
            posts = posts.filter(saved_posts__saved_by=request.user, saved_posts__saved=SavedPost.Saved.YES)
        
        # Filter by my posts
        if my_posts == "on":
            posts = posts.filter(created_by=request.user)

        # Filter by admin/contributor posts
        if admin_posts == "on":
            collaborator = CustomerCompanyDetails.objects.filter(company_user=request.user)
            contributor = CustomerCompanyDetails.objects.filter(company_root_user=request.user)
            
            if contributor.exists():
                company = contributor.first().company
            if collaborator.exists():
                company = collaborator.first().company
            
            company_customer_details = CustomerCompanyDetails.objects.filter(
                                                                    company=company,
                                                                    company_root_user__isnull=False
                                                                )
            root_users = [company_customer_detail.company_root_user for company_customer_detail in company_customer_details]
            posts = posts.filter(created_by__in=root_users)

        # Filter by pinned posts
        if pinned_posts == "on":
            posts = posts.filter(pinned_posts__deleted=False)

        # Filter by top voted posts
        if top_voted_posts == "on":
            posts = posts.annotate(vote_count=Count('vote')).order_by('-vote_count')

        # Filter by top saved posts
        if top_saved_posts == "on":
            posts = posts.filter(saved_posts__saved=SavedPost.Saved.YES)
            posts = posts.annotate(saved_count=Count('saved_posts')).order_by('-saved_count')

        # Filter by mentions
        if has_mentions == "on":
            posts = posts.filter(content__regex=r'@\w+')

        # Filter by previews
        if has_previews == "on":
            posts = posts.filter(content__regex=r'<iframe[^>]+src="([^">]+)"')

        # Filter by links
        if has_links == "on":
            posts = posts.filter(content__regex=r'<a[^>]+href="([^">]+)"')

        # Filter by attachments
        if has_attachments == "on":
            posts = posts.filter(content__regex=r'http[s]?://\S+')

        # Filter by tables
        if has_tables == "on":
            posts = posts.filter(content__regex=r'<table[^>]*>')

        posted_users = []
        for post in posts:
            posted_users.append(post.created_by)
        posted_users = list(set(posted_users))
        
        return render(request, 'posts/ticket_posts.html', {
            'ticket': ticket,
            'posts': posts,
            'posted_users': posted_users,
            'search': search,
            'sort_by_date': sort_by_date,
            'posted_by': posted_by,
            'start_date': start_date,
            'end_date': end_date,
            'accepted_answer': accepted_answer,
            'saved_posts': saved_posts,
            'my_posts': my_posts,
            'admin_posts': admin_posts,
            'pinned_posts': pinned_posts,
            'top_voted_posts': top_voted_posts,
            'top_saved_posts': top_saved_posts,
            'has_mentions': has_mentions,
            'has_previews': has_previews,
            'has_links': has_links,
            'has_attachments': has_attachments,
            'has_tables': has_tables,
        })


@login_required
def accept_as_answer(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    ticket = post.ticket

    # Ensure only the creator of the ticket can accept or unaccept an answer
    if ticket.created_by != request.user:
        return redirect('posts:ticket_posts', ticket_id=ticket.id)

    # Check if the post is already marked as accepted
    if post.accepted_solution:
        # Unmark this post as accepted answer
        post.accepted_solution = False
        post.save()
    else:
        # Ensure there is no previously accepted answer
        Post.objects.filter(ticket=ticket, accepted_solution=True).update(accepted_solution=False)
        
        # Mark the selected post as accepted answer
        post.accepted_solution = True
        post.save()

    return redirect('posts:ticket_posts', ticket_id=ticket.id)