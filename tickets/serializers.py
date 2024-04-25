from rest_framework import serializers
from .models import Post,Ticket


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'ticket', 'content', 'upvotes', 'downvotes', 'created_by', 'created_at', 'updated_at']

class TicketCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['title','description','start_date','end_date','estimated_end_date','due_date','status','priority_type','priority','priority_scale','ticket_type','deleted']
