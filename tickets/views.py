from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Vote
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import views, permissions, status
from .serializers import TicketCreationSerializer
from .models import Ticket
from django.db.models import Q

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

class CreateTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    """
    get method is not needed. we don't need to send anything to frontend.
    """
    def post(self, request):
        try:
            data = request.data
            must_keys = ["title", "start_date", "end_date"]
            
            if bool(set(must_keys) - set(data.keys())):
                return Response({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract user data
            ticket_data = {
                "title": data["title"],
                "description": data["description"],
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                "estimated_end_date": data["estimated_end_date"],
                "due_date": data["due_date"],
                "status": data["status"],
                "priority_type": data["priority_type"],
                "priority": data["priority"],
                "priority_scale": data["priority_scale"],
                "ticket_type": data["ticket_type"],
                "deleted": data["deleted"],
            }


            # Create User and Company instances
            ticket_serializer = TicketCreationSerializer(data=ticket_data)
            # Validate and save User and Company instances
            if not ticket_serializer.is_valid():
                return Response({'user_error': ticket_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                ticket_serializer.is_valid(raise_exception=True)
                user_instance = ticket_serializer.save()
                user_instance.save()

                response_data = {
                    'data': ticket_serializer.data,
                    "message": "Data Saved Successfully.",
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error)
            return Response({'Message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetActiveTicketsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            
            ticket_object = Ticket.objects.filter()

            if ticket_object.exists():
                ticket_object = ticket_object.latest()
                ticket_title = ticket_object.title
                ticket_description = ticket_object.description
                ticket_startdate = ticket_object.start_date
                ticket_enddate = ticket_object.end_date
                ticket_status = ticket_object.status
                ticket_priority = ticket_object.priority
                ticket_ticket_type = ticket_object.ticket_type
                response_data = {
                    'data': {
                        "ticket_title": ticket_title,
                        "ticket_description": ticket_description,
                        "ticket_startdate": ticket_startdate,
                        "ticket_enddate": ticket_enddate,
                        "ticket_status": ticket_status,
                        "ticket_priority": ticket_priority,
                        "ticket_ticket_type": ticket_ticket_type,
                        },
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "There are no tickets available",
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data=request.data
            must_keys=["id"]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)
            
            ticket_id = data.get('id')
            ticket_object = Ticket.objects.filter(Q(id=ticket_id))

            if ticket_object.exists():
                ticket_object = ticket_object.latest()
                ticket_title = ticket_object.title
                ticket_description = ticket_object.description
                ticket_startdate = ticket_object.start_date
                ticket_enddate = ticket_object.end_date
                ticket_status = ticket_object.status
                ticket_priority = ticket_object.priority
                ticket_ticket_type = ticket_object.ticket_type
                response_data = {
                    'data': {
                        "ticket_title": ticket_title,
                        "ticket_description": ticket_description,
                        "ticket_startdate": ticket_startdate,
                        "ticket_enddate": ticket_enddate,
                        "ticket_status": ticket_status,
                        "ticket_priority": ticket_priority,
                        "ticket_ticket_type": ticket_ticket_type,
                        },
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "This is new data. We can proceed.",
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
