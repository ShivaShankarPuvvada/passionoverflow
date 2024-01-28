from django.urls import path
from . import views

app_name = "segments"


"""
list of all possible tasks for segments

# create segment (by default segment status = 1)
# delete segment
# update segment
# get segment
# get all or specific segments
# activate segments (change status to 1)
# deactivate segments (change status to 0)
# add employees to the segment (this will be covered in CRUD operations)
# remove employees to the segment (this will be covered in CRUD operations)
# add admin members to the segment (this will be covered in CRUD operations)
# remove admin members to the segment (this will be covered in CRUD operations)
# add/change phase to the segment (this will be covered in CRUD operations)
# Segment assignment CRUD operations will be covered in Segment model CRUD operations.
# show assignment history for a segment (get all the rows for this segment and display them in order)
# show segment model history if possible
"""

urlpatterns = [
    # path('create_segment/', views.CreateSegmentView.as_view(), name="create_segment"),
    # path('segment/<int:segment_id>/', views.SegmentView.as_view(), name="segment"),
    # path('get_segments/<str:segment_ids>/', views.GetSegmentsView.as_view(), name="get_segments"),
    # path('activate_segments/<str:segment_ids>/', views.ActivateSegmentsView.as_view(), name="activate_segments"),
    # path('deactivate_segments/<str:segment_ids>/', views.DeActivateSegmentsView.as_view(), name="deactivate_segments"),
    # path('segment_assignment_history/<int:segment_id>/', views.SegmentAssignmentHistoryView.as_view(), name="segment_assignment_history"),
    # path('segment_history/<int:segment_id>/', views.SegmentHistoryView.as_view(), name="segment_history"),
]