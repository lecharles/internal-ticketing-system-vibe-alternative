from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.tickets import bp
from app.tickets.forms import TicketForm, CommentForm
from app.models import Ticket, Comment, Project, Team
from app.errors.exceptions import ResourceNotFoundError, AuthorizationError, DatabaseError
import logging

@bp.route('/tickets')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('tickets/list.html',
                         title='Tickets',
                         tickets=tickets)

@bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TicketForm()
    # Get list of projects for the form
    projects = Project.query.all()
    form.project = SelectField('Project', choices=[(p.id, p.name) for p in projects])
    
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            project_id=form.project.data,
            creator_id=current_user.id,
            assignee_id=form.assignee.data if form.assignee.data != 0 else None
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket has been created!', 'success')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
    
    return render_template('tickets/create.html',
                         title='Create Ticket',
                         form=form)

@bp.route('/tickets/<int:ticket_id>')
@login_required
def view(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    return render_template('tickets/view.html',
                         title=f'Ticket: {ticket.title}',
                         ticket=ticket,
                         form=form)

@bp.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    # Check if user has permission to edit
    if ticket.creator_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to edit this ticket.', 'error')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
    
    form = TicketForm()
    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.description = form.description.data
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        ticket.assignee_id = form.assignee.data if form.assignee.data != 0 else None
        db.session.commit()
        flash('Ticket has been updated!', 'success')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
    elif request.method == 'GET':
        form.title.data = ticket.title
        form.description.data = ticket.description
        form.status.data = ticket.status
        form.priority.data = ticket.priority
        form.assignee.data = ticket.assignee_id if ticket.assignee_id else 0
    
    return render_template('tickets/edit.html',
                         title='Edit Ticket',
                         form=form,
                         ticket=ticket)

@bp.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            ticket_id=ticket.id,
            author_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('tickets.view', ticket_id=ticket.id))

@bp.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete(ticket_id):
    """
    Delete a ticket and its associated comments.
    
    Args:
        ticket_id: The ID of the ticket to delete.
        
    Returns:
        A redirect response to the ticket list.
        
    Raises:
        ResourceNotFoundError: If the ticket doesn't exist.
        AuthorizationError: If the user doesn't have permission to delete the ticket.
        DatabaseError: If there's an error during deletion.
    """
    try:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ResourceNotFoundError("Ticket", ticket_id)
        
        # Check if user has permission to delete
        can_delete = (
            ticket.creator_id == current_user.id or  # Creator can delete
            current_user.role == 'admin' or          # Admin can delete
            (                                        # Team lead/project manager of the project's team can delete
                ticket.project and 
                ticket.project.team and 
                current_user in ticket.project.team.members and
                ticket.project.team.get_member_role(current_user) in ['team_lead', 'project_manager']
            )
        )
        
        if not can_delete:
            current_app.logger.warning(
                f'User {current_user.username} attempted unauthorized deletion of ticket {ticket_id}',
                extra={
                    'user_id': current_user.id,
                    'ticket_id': ticket_id,
                    'user_role': current_user.role
                }
            )
            raise AuthorizationError("You don't have permission to delete this ticket")
        
        # Log the deletion attempt
        current_app.logger.info(
            f'Deleting ticket {ticket_id}',
            extra={
                'user_id': current_user.id,
                'ticket_id': ticket_id,
                'ticket_title': ticket.title,
                'project_id': ticket.project_id
            }
        )
        
        try:
            # Delete associated comments first
            Comment.query.filter_by(ticket_id=ticket.id).delete()
            
            # Delete the ticket
            db.session.delete(ticket)
            db.session.commit()
            
            current_app.logger.info(
                f'Successfully deleted ticket {ticket_id}',
                extra={
                    'user_id': current_user.id,
                    'ticket_id': ticket_id
                }
            )
            
            flash('Ticket has been deleted successfully.', 'success')
            return redirect(url_for('tickets.list'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f'Database error while deleting ticket {ticket_id}',
                exc_info=True,
                extra={
                    'user_id': current_user.id,
                    'ticket_id': ticket_id
                }
            )
            raise DatabaseError(f"Failed to delete ticket: {str(e)}")
            
    except (ResourceNotFoundError, AuthorizationError, DatabaseError) as e:
        flash(str(e.message), 'error')
        if isinstance(e, ResourceNotFoundError):
            return redirect(url_for('tickets.list'))
        return redirect(url_for('tickets.view', ticket_id=ticket_id))
        
    except Exception as e:
        current_app.logger.error(
            f'Unexpected error while deleting ticket {ticket_id}',
            exc_info=True,
            extra={
                'user_id': current_user.id,
                'ticket_id': ticket_id
            }
        )
        flash('An unexpected error occurred. Please try again later.', 'error')
        return redirect(url_for('tickets.list')) 