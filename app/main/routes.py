from flask import render_template
from flask_login import login_required
from app.main import bp
from app.models import Ticket, Project

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Get recent tickets
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
    
    # Get project statistics
    projects = Project.query.all()
    project_stats = []
    for project in projects:
        total_tickets = project.tickets.count()
        open_tickets = project.tickets.filter_by(status='open').count()
        in_progress = project.tickets.filter_by(status='in progress').count()
        completed = project.tickets.filter_by(status='done').count()
        
        project_stats.append({
            'project': project,
            'total': total_tickets,
            'open': open_tickets,
            'in_progress': in_progress,
            'completed': completed
        })
    
    return render_template('main/index.html',
                         title='Dashboard',
                         recent_tickets=recent_tickets,
                         project_stats=project_stats) 