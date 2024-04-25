from django.urls import path
from . import views

app_name = "tickets"

"""
list of all possible tasks for tickets

create ticket
delete ticket
update ticket
get ticket
get all or specific tickets
activate all or specific tickets
deactivate all or specific tickets
get active tickets
get deactive tickets
show ticket history for a particular ticket if possible
"""


"""
list of all possible tasks for posts

create post
delete post
update post
get post
get all or specific posts
activate all or specific posts
deactivate all or specific posts
get active posts
get deactive posts
show post history for a particular post if possible
"""

urlpatterns = [
    path('create_ticket/', views.CreateTicketView.as_view(), name="create_ticket"),
    path('ticket/<int:ticket_id>/', views.TicketView.as_view(), name="ticket"),
    # path('get_tickets/<str:ticket_ids>/', views.GetTicketsView.as_view(), name="get_tickets"),
    # path('activate_tickets/<str:ticket_ids>/', views.ActivateTickets.as_view(), name="activate_tickets"),
    # path('deactivate_tickets/<str:ticket_ids>/', views.DeActivateTickets.as_view(), name="deactivate_tickets"),
    path('get_active_tickets/', views.GetActiveTicketsView.as_view(), name="get_active_tickets"),
    # path('get_deactive_tickets/', views.GetDeActiveTicketsView.as_view(), name="get_Deactive_tickets"),
    # path('get_ticket_history/<int:ticket_id>/', views.GetTicketHistoryView.as_view(), name="get_ticket_history"),

    # path('create_post/', views.CreatePostView.as_view(), name="create_post"),
    # path('post/<int:post_id>/', views.PostView.as_view(), name="post"),
    # path('get_posts/<str:post_ids>/', views.GetPostsView.as_view(), name="get_posts"),
    # path('activate_posts/<str:post_ids>/', views.ActivatePosts.as_view(), name="activate_posts"),
    # path('deactivate_posts/<str:post_ids>/', views.DeActivatePosts.as_view(), name="deactivate_posts"),
    # path('get_active_posts/', views.GetActivePostsView.as_view(), name="get_active_posts"),
    # path('get_deactive_posts/', views.GetDeActivePostsView.as_view(), name="get_Deactive_posts"),
    # path('pin_post/<int:post_id>/', views.PinPostView.as_view(), name='pin_post'),
    # path('unpin_post/<int:post_id>/', views.UnPinPostView.as_view(), name='unpin_post'),
    # path('upvote_post/<int:post_id>/', views.UpVotePostView.as_view(), name='upvote_post'),
    # path('upvote_post/<int:post_id>/', views.DownVotePostView.as_view(), name='downvote_post'),
    # path('get_post_history/<int:post_id>/', views.GetPostHistoryView.as_view(), name="get_post_history"),
    
    
    # path('create_saved_post/', views.CreateSavedPostView.as_view(), name="create_saved_post"),
    # path('saved_post/<int:saved_post_id>/', views.SavedPostView.as_view(), name="saved_post"),
    # path('get_saved_posts/<str:saved_post_ids>/', views.GetSavedPostsView.as_view(), name="get_saved_posts"),
    # path('get_unsaved_posts/<str:saved_post_ids>/', views.GetUnSavedPostsView.as_view(), name="get_unsaved_posts"),
    # path('get_post_history/<int:post_id>/', views.GetPostHistoryView.as_view(), name="get_post_history"),
]