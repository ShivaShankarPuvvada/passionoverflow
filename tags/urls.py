from django.urls import path
from . import views

app_name = "tags"

"""
list of all possible tasks for tags

create tag
delete tag
update tag
get tag
get all or specific tags
activate all or specific tags
deactivate all or specific tags
get active tags
get deactive tags
show tag history for a particular tag if possible
"""

urlpatterns = [
    # path('create_tag/', views.CreateTagView.as_view(), name="create_tag"),
    # path('tag/<int:tag_id>/', views.TagView.as_view(), name="tag"),
    # path('get_tags/<str:tag_ids>/', views.GetTagsView.as_view(), name="get_tags"),
    # path('activate_tags/<str:tag_ids>/', views.ActivateTags.as_view(), name="activate_tags"),
    # path('deactivate_tags/<str:tag_ids>/', views.DeActivateTags.as_view(), name="deactivate_tags"),
    # path('get_active_tags/', views.GetActiveTagsView.as_view(), name="get_active_tags"),
    # path('get_deactive_tags/', views.GetDeActiveTagsView.as_view(), name="get_Deactive_tags"),
    # path('get_tag_history/<int:tag_id>/', views.GetTagHistoryView.as_view(), name="get_tag_history"),
]