import pytest
from flask import url_for
from app.models import Team, User
from app import db

def test_create_team_page(auth_client):
    """Test team creation page loads."""
    response = auth_client.get('/teams/create')
    assert response.status_code == 200
    assert b'Create Team' in response.data
    assert b'Team Name' in response.data
    assert b'Description' in response.data

def test_create_team(auth_client, test_user):
    """Test team creation through the web interface."""
    response = auth_client.post('/teams/create', data={
        'name': 'New Team',
        'description': 'A new team description',
        'submit': 'Create Team'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Team created successfully' in response.data
    
    # Verify team was created
    team = Team.query.filter_by(name='New Team').first()
    assert team is not None
    assert team.description == 'A new team description'
    assert team.leader == test_user
    assert test_user in team.members
    
    # Clean up
    db.session.delete(team)
    db.session.commit()

def test_team_list(auth_client, test_team):
    """Test team listing page."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    assert test_team.name.encode() in response.data
    assert test_team.description.encode() in response.data

def test_team_detail(auth_client, test_team):
    """Test team detail page."""
    response = auth_client.get(f'/teams/{test_team.id}')
    assert response.status_code == 200
    assert test_team.name.encode() in response.data
    assert test_team.description.encode() in response.data
    assert test_team.leader.username.encode() in response.data

def test_edit_team(auth_client, test_team):
    """Test team editing."""
    response = auth_client.post(f'/teams/{test_team.id}/edit', data={
        'name': 'Updated Team Name',
        'description': 'Updated description',
        'submit': 'Update Team'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Team updated successfully' in response.data
    
    # Verify changes
    updated_team = Team.query.get(test_team.id)
    assert updated_team.name == 'Updated Team Name'
    assert updated_team.description == 'Updated description'

def test_add_team_member(auth_client, test_team, app):
    """Test adding a team member."""
    with app.app_context():
        # Create a new user to add
        new_user = User(username='newmember', email='newmember@example.com')
        new_user.set_password('password123')
        db.session.add(new_user)
        db.session.commit()
        
        response = auth_client.post(f'/teams/{test_team.id}/members/add', data={
            'user_id': new_user.id,
            'submit': 'Add Member'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Member added successfully' in response.data
        assert new_user in test_team.members
        
        # Clean up
        db.session.delete(new_user)
        db.session.commit()

def test_remove_team_member(auth_client, test_team, app):
    """Test removing a team member."""
    with app.app_context():
        # Create and add a new user
        member = User(username='removeme', email='removeme@example.com')
        member.set_password('password123')
        db.session.add(member)
        test_team.add_member(member)
        db.session.commit()
        
        response = auth_client.post(f'/teams/{test_team.id}/members/{member.id}/remove', 
                                  follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Member removed successfully' in response.data
        assert member not in test_team.members
        
        # Clean up
        db.session.delete(member)
        db.session.commit()

def test_team_permissions(client, auth_client, test_team, test_user, app):
    """Test team-related permissions."""
    with app.app_context():
        # Unauthenticated user can't access team pages
        response = client.get('/teams/create')
        assert response.status_code == 302  # Redirects to login
        
        # Non-leader can't edit team
        other_user = User(username='other', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        with client:
            client.post('/auth/login', data={
                'username': 'other',
                'password': 'password123'
            })
            
            response = client.post(f'/teams/{test_team.id}/edit', data={
                'name': 'Unauthorized Edit',
                'description': 'Should not work'
            })
            assert response.status_code == 403  # Forbidden
            
        # Clean up
        db.session.delete(other_user)
        db.session.commit() 