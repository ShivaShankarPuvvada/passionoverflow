from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Vote
from .serializers import PostSerializer


class UpvotePost(APIView):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        # Check if the user has already voted
        existing_vote = Vote.objects.filter(voted_by=user, post=post, deleted=False).first()
        if existing_vote:
            return Response({'error': 'You have already voted on this post.'}, status=status.HTTP_400_BAD_REQUEST)

        # If the user hasn't voted or their previous vote was deleted, create an upvote
        post.upvotes += 1
        vote = Vote.objects.create(voted_by=user, post=post, vote_type=1)
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DownvotePost(APIView):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        # Check if the user has already voted
        existing_vote = Vote.objects.filter(voted_by=user, post=post, deleted=False).first()
        if existing_vote:
            return Response({'error': 'You have already voted on this post.'}, status=status.HTTP_400_BAD_REQUEST)

        # If the user hasn't voted or their previous vote was deleted, create a downvote
        post.downvotes += 1
        vote = Vote.objects.create(voted_by=user, post=post, vote_type=-1)
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
