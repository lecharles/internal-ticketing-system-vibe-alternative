from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.tickets import bp
from app.tickets.forms import TicketForm, CommentForm
from app.models import Ticket, Comment, Project

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