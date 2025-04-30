import pytest
from app.models import User, Team, Project
from app import db

def test_team_creation(auth_client, test_admin):
    """Test team creation process."""
    response = auth_client.post('/teams/create', data={
        'name': 'Test Team',
        'description': 'A test team'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Team created successfully' in response.data
    
    # Verify team in database
    team = Team.query.filter_by(name='Test Team').first()
    assert team is not None
    assert team.description == 'A test team'
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_member_assignment(auth_client, test_admin, test_user):
    """Test assigning members to a team."""
    # Create a team first
    team = Team(name='Member Test Team', description='Testing member assignment')
    db.session.add(team)
    db.session.commit()
    
    # Assign member
    response = auth_client.post(f'/teams/{team.id}/members/add', data={
        'user_id': test_user.id,
        'role': 'developer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Member added successfully' in response.data
    
    # Verify assignment
    assert test_user in team.members
    assert team in test_user.teams
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_project_assignment(auth_client, test_admin, test_project):
    """Test assigning projects to a team."""
    # Create a team
    team = Team(name='Project Test Team', description='Testing project assignment')
    db.session.add(team)
    db.session.commit()
    
    # Assign project
    response = auth_client.post(f'/teams/{team.id}/projects/add', data={
        'project_id': test_project.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Project assigned successfully' in response.data
    
    # Verify assignment
    assert test_project in team.projects
    assert team in test_project.teams
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_role_management(auth_client, test_admin, test_user):
    """Test managing team member roles."""
    # Create a team
    team = Team(name='Role Test Team', description='Testing role management')
    db.session.add(team)
    db.session.commit()
    
    # Add member with initial role
    team.add_member(test_user, role='developer')
    
    # Update role
    response = auth_client.post(f'/teams/{team.id}/members/{test_user.id}/role', data={
        'role': 'team_lead'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Role updated successfully' in response.data
    
    # Verify role update
    assert team.get_member_role(test_user) == 'team_lead'
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_member_removal(auth_client, test_admin, test_user):
    """Test removing members from a team."""
    # Create a team and add member
    team = Team(name='Removal Test Team', description='Testing member removal')
    db.session.add(team)
    db.session.commit()
    team.add_member(test_user)
    
    # Remove member
    response = auth_client.post(f'/teams/{team.id}/members/{test_user.id}/remove', 
                              follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Member removed successfully' in response.data
    
    # Verify removal
    assert test_user not in team.members
    assert team not in test_user.teams
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_access_control(client, auth_client, test_user, test_admin):
    """Test team-related access control."""
    # Create a team
    team = Team(name='Access Test Team', description='Testing access control')
    db.session.add(team)
    db.session.commit()
    
    # Test unauthorized access
    response = client.get(f'/teams/{team.id}')
    assert response.status_code == 302  # Redirect to login
    
    # Test non-member access
    response = auth_client.get(f'/teams/{team.id}')
    assert response.status_code == 403  # Forbidden
    
    # Add as member and test access
    team.add_member(test_user)
    response = auth_client.get(f'/teams/{team.id}')
    assert response.status_code == 200
    assert b'Access Test Team' in response.data
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_listing(auth_client, test_user):
    """Test team listing functionality."""
    # Create multiple teams
    teams = [
        Team(name=f'Test Team {i}', description=f'Test Description {i}')
        for i in range(3)
    ]
    for team in teams:
        db.session.add(team)
        team.add_member(test_user)
    db.session.commit()
    
    # Test listing
    response = auth_client.get('/teams')
    assert response.status_code == 200
    for team in teams:
        assert team.name.encode() in response.data
    
    # Clean up
    for team in teams:
        db.session.delete(team)
    db.session.commit() 