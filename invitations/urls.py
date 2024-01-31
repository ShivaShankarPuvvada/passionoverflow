from django.urls import path
from . import views

app_name = "invitations"

"""
list of all possible tasks for invitations

create invitation
Input list for create invitation as follows, expiration date is optional.
inviations_list = [
    [
        email, 
        [
            [project id, read access, expiration date], 
            [project id, read access, expiration date], 
            [project id, write access, expiration date]
        ], 
        [
            [segment id, write access, expiration date],
            [segment id, write access, expiration date],
            [segment id, read access, expiration date]
            
        ],
    ],
        [
        email, 
        [
            [project id, read access, expiration date], 
            [project id, read access, expiration date], 
            [project id, write access, expiration date]
        ], 
        [
            [segment id, write access, expiration date],
            [segment id, write access, expiration date],
            [segment id, read access, expiration date]
            
        ],
    ],
]
update invitation, for updation also same above list. we need to make the existing records status to 0 and create new records if there are any changes.
there is only one url for create invitation and update invitation. i.e, modify_invitations.
get single user invitations (show all his invitations)
get all or specific invitations ()
get active invitations
get deactive invitations
show invitation history for a particular invitation if possible, this may not be needed for any kind of users. this is purely for devleoper.
"""

urlpatterns = [
    # path('modify_invitations/<str:inviations_list>/', views.ModifyInvitationsView.as_view(), name="modify _invitations"), # inviations_list mentioned above in docstring. this one covers create or update.
    # path('get_user_invitations/<int:user_d>/', views.GetUserInvitationsView.as_view(), name="get_user_invitations"), # this is for contributor to check the invitations that user was invited to. he can enter his own mail id to check which projects he was invited to. this is not for collaborators.
    # path('get_user_invitation_tasks/<int:user_d>/', views.GetUserInvitation_tasksView.as_view(), name="get_user_invitation_tasks"), # this is for contributor to check all the invitation tasks performed by user.
    # path('get_invitation_history/<int:invitation_id>/', views.GetInvitationHistoryView.as_view(), name="get_invitation_history"),
]