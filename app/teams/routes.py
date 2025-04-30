from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.teams import bp
from app.teams.forms import TeamForm, AddMemberForm
from app.models import Team, User

@bp.route('/teams')
@login_required
def list_teams():
    """List all teams."""
    teams = Team.query.all()
    return render_template('teams/list.html', teams=teams)

@bp.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    """Create a new team."""
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            description=form.description.data,
            leader=current_user
        )
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully', 'success')
        return redirect(url_for('teams.list_teams'))
    return render_template('teams/create.html', form=form)

@bp.route('/teams/<int:id>')
@login_required
def team_detail(id):
    """Show team details."""
    team = Team.query.get_or_404(id)
    return render_template('teams/detail.html', team=team)

@bp.route('/teams/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    """Edit a team."""
    team = Team.query.get_or_404(id)
    if team.leader != current_user:
        abort(403)
    
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.description = form.description.data
        db.session.commit()
        flash('Team updated successfully', 'success')
        return redirect(url_for('teams.team_detail', id=team.id))
    return render_template('teams/edit.html', form=form, team=team)

@bp.route('/teams/<int:id>/members/add', methods=['GET', 'POST'])
@login_required
def add_member(id):
    """Add a member to the team."""
    team = Team.query.get_or_404(id)
    if team.leader != current_user:
        abort(403)
    
    form = AddMemberForm()
    form.user_id.choices = [(u.id, u.username) for u in User.query.all() if u not in team.members]
    
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if user:
            team.add_member(user)
            db.session.commit()
            flash('Member added successfully', 'success')
            return redirect(url_for('teams.team_detail', id=team.id))
    return render_template('teams/add_member.html', form=form, team=team)

@bp.route('/teams/<int:team_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    """Remove a member from the team."""
    team = Team.query.get_or_404(team_id)
    if team.leader != current_user:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user == team.leader:
        flash('Cannot remove team leader', 'error')
    else:
        team.remove_member(user)
        db.session.commit()
        flash('Member removed successfully', 'success')
    return redirect(url_for('teams.team_detail', id=team_id)) 