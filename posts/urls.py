from django.urls import path
from . import views

app_name = "posts"


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
For all list data table views, need to do bulk update option.
For all list data table views, need to do bulk update option. Need to write get views based on permissions. Add all possible filters seperately for each field. Not a common search bar.

"""

urlpatterns = [
    path('tickets/<int:ticket_id>/posts/', views.ticket_posts, name='ticket_posts'),
    path('create_post/', views.create_post, name="create_post"),
    path('vote_post/', views.vote_post, name="vote_post"),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('pin/<int:post_id>/', views.pin_post, name='pin_post'),
    path('unpin/<int:post_id>/', views.unpin_post, name='unpin_post'),
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('un_save_post/<int:post_id>/', views.un_save_post, name='un_save_post'),
    # path('post/<int:post_id>/', views.PostView.as_view(), name="post"),
    # path('get_posts/<str:post_ids>/', views.GetPostsView.as_view(), name="get_posts"),
    # path('activate_posts/<str:post_ids>/', views.ActivatePosts.as_view(), name="activate_posts"),
    # path('deactivate_posts/<str:post_ids>/', views.DeActivatePosts.as_view(), name="deactivate_posts"),
    # path('get_active_posts/', views.GetActivePostsView.as_view(), name="get_active_posts"),
    # path('get_deactive_posts/', views.GetDeActivePostsView.as_view(), name="get_Deactive_posts"),
    # path('pin_post/<int:post_id>/', views.PinPostView.as_view(), name='pin_post'),
    # path('unpin_post/<int:post_id>/', views.UnPinPostView.as_view(), name='unpin_post'),
    # path('upvote_post/<int:post_id>/', views.upvote_post, name='upvote_post'),
    # path('upvote_post/<int:post_id>/', views.downvote_post, name='downvote_post'),
    # path('get_post_history/<int:post_id>/', views.GetPostHistoryView.as_view(), name="get_post_history"),
    
    
    # path('create_saved_post/', views.CreateSavedPostView.as_view(), name="create_saved_post"),
    # path('saved_post/<int:saved_post_id>/', views.SavedPostView.as_view(), name="saved_post"),
    # path('get_saved_posts/<str:saved_post_ids>/', views.GetSavedPostsView.as_view(), name="get_saved_posts"),
    # path('get_unsaved_posts/<str:saved_post_ids>/', views.GetUnSavedPostsView.as_view(), name="get_unsaved_posts"),
    # path('get_post_history/<int:post_id>/', views.GetPostHistoryView.as_view(), name="get_post_history"),
]