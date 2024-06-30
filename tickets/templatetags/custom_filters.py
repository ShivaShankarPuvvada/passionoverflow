from django import template

register = template.Library()

@register.filter(name='check_super_id')
def check_super_id(ticket_object, super_ticket_id):
    super_tickets = ticket_object.super_tickets.all()
    
    for super_ticket in super_tickets:
        if super_ticket.id == super_ticket_id:
            return True
    
    return False


@register.filter(name='check_sub_id')
def check_sub_id(ticket_object, sub_ticket_id):
    sub_tickets = ticket_object.sub_tickets.all()
    print('for each ticket')
    for sub_ticket in sub_tickets:
        if sub_ticket.id == sub_ticket_id:
            return True
    return False


@register.filter(name='check_stage')
def check_stage(ticket_object, stage_id):
    stages = ticket_object.stages.all()
    
    for stage in stages:
        if stage.id == stage_id:
            return True
    
    return False


@register.filter(name='check_tag')
def check_tag(ticket_object, tag_id):
    tags = ticket_object.tags.all()
    for tag in tags:
        if tag.id == tag_id:
            return True
    return False


@register.filter(name='is_user_assigned')
def is_user_assigned(user_id, assigned_users):
    """
    Checks if the user with given user_id is in the assigned_users list.
    """
    return user_id in assigned_users.values_list('id', flat=True)