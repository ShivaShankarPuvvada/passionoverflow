# Project Management Software - passionoverflow.com

## Overview

This Django-based project management software facilitates collaboration among users with two distinct roles: Contributor and Collaborator. Contributors have the ability to modify anything within their invited projects, while Collaborators are limited to working on tickets and posts within segments in the project.

## User Roles

### Contributor
- A Contributor, is the primary user who registers the company.
- Contributors can invite others through emails with two options: Invite as Contributor or Collaborator.
- If a Contributor is added to a project by another Contributor, they can edit anything within the project.

### Collaborator
- Collaborators are invited to the company space by the Contributor.
- They have limited access and can only edit tickets and posts within a project.
- Collaborators cannot edit segments or the project itself.

## Project Management

- Contributors create projects and add invited people to them.
- Only Contributors or Managers can invite others.
- Once a person is invited to a company space, they are added to the project by a Contributor.
- Once added to a project, all users can create tickets, posts, view all segments, and access project details.
- Users can also view "My Tickets," "My Projects," and "My Segments."

## Invitation Process

- Contributors can invite others. Not Collaborators.
- Invited users receive a registration mail with a link to passionoverflow.com and their company space (e.g., company.passionoverflow.com).
- Clicking the link autofills company name and URL; users complete the registration form with verified email and additional details.

## Notifications

- Users receive email and website notifications for relevant activities.
- If mentioned in any other ticket (ex: @sam) they are involved in, users receive email notifications (ex: sam@companymail.com or sam@gmail.com etc.).

## Ticket Creation Example

```markdown
Title: Need to add Facebook like functionality in this segment
Description:
Completion date:
Assignees: Sam, Adam, Tom

## NOTES

- Even if customer deletes anything, we will not delete in our database. We will have deleted field in everymodel and make it true. We will keep the records until a year (decide this time period later).


1. Have to add width for summernote. If we paste long line, currently it is extending.
2. Have to add kanban board for tickets.
3. Have to add filters for all list tables.
4. Need to add @ and # for username and tickets in content in posts in ticket_posts page.

