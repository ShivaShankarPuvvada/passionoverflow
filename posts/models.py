from django.utils.translation import gettext_lazy as _

from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from tickets.models import Ticket
User = get_user_model()


"""
    # Users can post the ideas as tickets. 
    # These ideas can be reviewed by anyone who can access the ticket. 
    # The calculation for the ideas will be done by adding their inputs.
    
    # add this field in the models for idea submission and calculation.
    idea_calculation = models.TextField(blank=True, null=True)

    # add these methods to the models for idea submission and calculation.
    def calculate_idea(self):
        # Consider factors for cost reduction
        # You can customize this based on your project and business requirements

        # Example: Calculate idea based on estimated cost savings
        estimated_cost_savings = self.calculate_estimated_cost_savings()

        # Example: Consider impact on productivity
        productivity_impact = self.calculate_productivity_impact()

        # Example: Consider time saved
        time_saved = self.calculate_time_saved()

        # Combine factors into an overall idea calculation
        overall_idea_calculation = f"Estimated Cost Savings: {estimated_cost_savings}, Productivity Impact: {productivity_impact}, Time Saved: {time_saved}"

        # Update the idea_calculation field
        self.idea_calculation = overall_idea_calculation

    def calculate_estimated_cost_savings(self):
        # Your logic for estimating cost savings goes here
        # For example, you might consider reduced resource costs, infrastructure savings, etc.
        return "$100,000"  # Placeholder value, replace with your actual calculation

    def calculate_productivity_impact(self):
        # Your logic for estimating productivity impact goes here
        # For example, you might consider improved efficiency, reduced errors, etc.
        return "High"  # Placeholder value, replace with your actual calculation

    def calculate_time_saved(self):
        # Your logic for estimating time saved goes here
        # For example, you might consider reduced development time, faster processes, etc.
        return "2 weeks"  # Placeholder value, replace with your actual calculation

    def save(self, *args, **kwargs):
        self.calculate_idea()  # Call the calculate_idea method before saving
        super().save(*args, **kwargs)

"""
# Create your models here.

# updated_by is not required for this model because on who creates only able to update.
class Post(models.Model):
    """
    User can post on ticket detail page. 
    If we click on ticket, we can see the list of posts.
    User who created the ticket can mark the post as accepted solution.
    There should be an option to show solution at the top, if one exists.
    User can reply to any post. The reply will be a other post.
    """
    class Deleted(models.TextChoices):
        YES = '1', _("This post was deleted by user.")
        NO = '2', _("This post was not deleted by user.")

    ticket = models.ForeignKey(Ticket, related_name='post_ticket', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField() # this is the actual field that will store the data.
    up_votes = models.IntegerField(default=0) # increase the count if up voted.
    down_votes = models.IntegerField(default=0) # increase the count if down voted.
    accepted_solution = models.BooleanField(default=False)  # creator of the ticket can check it as accepted solution.
    parent_post = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE) # new post id will be 2 and this field id is 1. User can select any post and create reply as seperate post.
    history = HistoricalRecords() # this field will store all the updates done to this model so far.
    deleted = models.CharField(max_length=1, choices=Deleted.choices, default=Deleted.NO) # we will keep the user deleted tickets as well.
    created_by = models.ForeignKey(User, related_name='post_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='post_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Post by @{self.created_by.username} on Ticket #{self.ticket.id}'
    

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Post, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Post, self).save()


class SavedPost(models.Model):
    """
    User can save the post. This is for saving his favorite posts. He can come and check his saved posts later.
    """
    class Saved(models.TextChoices):
        YES = '1', _("This post was saved by user.")
        NO = '2', _("This post was not saved by user.")
    post = models.ForeignKey(Post, related_name='saved_posts', on_delete=models.SET_NULL, null=True, blank=True)
    saved_by = models.ForeignKey(User, related_name='post_saved_by', on_delete=models.SET_NULL, null=True, blank=True)
    saved = models.CharField(max_length=1, choices=Saved.choices, default=Saved.YES) # we will keep the user saved and unsaved posts as well.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_by = models.ForeignKey(User, related_name='saved_post_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='saved_post_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'post - {self.post.id} saved by @{self.saved_by.username}'


    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SavedPost, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(SavedPost, self).save()




class PinnedPost(models.Model):
    """
    User can pin the post. Pinned posts are public, everybody can pin the posts.
    All the pinned posts will be shown in top in an order. 
    At the bottom of that, normal posts will be shown in order.
    When user un pin the post, we need to change the 'saved' field to Pinned.NO
    While filtering the Pinned posts we need to inclued saved = YES in the filter.
    """
    class Pinned(models.TextChoices):
        YES = '1', _("This post was pinned by user.")
        NO = '2', _("This post was not pinned by user.")
    post = models.ForeignKey(Post, related_name='pinned_posts', on_delete=models.SET_NULL, null=True, blank=True)
    pinned_by = models.ForeignKey(User, related_name='post_pinned_by', on_delete=models.SET_NULL, null=True, blank=True)
    saved = models.CharField(max_length=1, choices=Pinned.choices, default=Pinned.YES) # we will keep the user pinned and unpinned posts as well. i.e, if he un pins, we will change this to NO.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_by = models.ForeignKey(User, related_name='pinned_post_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='pinned_post_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'post - {self.post.id} pinned by @{self.saved_by.username}'


    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(PinnedPost, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(PinnedPost, self).save()



class Vote(models.Model):
    """
    User can upvote or downvote the post.
    If user was deleted, his opinion won't delete, he already voted to post. Even though he left the company the vote matters.
    If we delete the user, we don't delete his vote.
    If post is deleted, then we delete the vote.
    """
    voted_by = models.ForeignKey(User, related_name='post_voted_by', on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])
    deleted = models.BooleanField(default=False) # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_by = models.ForeignKey(User, related_name='vote_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='vote_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f'post - {self.post.id} voted by @{self.voted_by.username}'
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Vote, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Vote, self).save()
