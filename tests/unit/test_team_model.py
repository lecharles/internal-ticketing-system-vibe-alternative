import pytest
from datetime import datetime
from app.models import Team, User, Project
from app import db

@pytest.fixture
def test_team(app, test_user):
    """Create a test team."""
    with app.app_context():
        team = Team(
            name='Test Team',
            description='A test team',
            leader=test_user
        )
        db.session.add(team)
        db.session.commit()
        yield team
        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_create_team(app, test_user):
    """Test team creation."""
    with app.app_context():
        team = Team(
            name='Engineering',
            description='Engineering team',
            leader=test_user
        )
        db.session.add(team)
        db.session.commit()
        
        # Verify team creation
        assert team.id is not None
        assert team.name == 'Engineering'
        assert team.description == 'Engineering team'
        assert team.leader == test_user
        
        # Verify leader is automatically added as a member with team_lead role
        assert test_user in team.members.all()
        assert team.get_member_role(test_user) == 'team_lead'
        
        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_member_management(app, test_user):
    """Test adding and removing team members."""
    with app.app_context():
        # Create another user
        other_user = User(username='other_user', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        
        team = Team(name='Test Team', leader=test_user)
        db.session.add(team)
        db.session.commit()
        
        # Test adding member
        team.add_member(other_user, role='developer')
        assert team.has_member(other_user)
        assert len(team.members) == 2  # Leader + new member
        assert team.get_member_role(other_user) == 'developer'
        
        # Test updating member role
        team.update_member_role(other_user, 'project_manager')
        assert team.get_member_role(other_user) == 'project_manager'
        
        # Test removing member
        team.remove_member(other_user)
        assert not team.has_member(other_user)
        assert len(team.members) == 1  # Only leader remains
        assert team.get_member_role(test_user) == 'team_lead'  # Leader role unchanged
        
        # Test cannot remove leader
        with pytest.raises(ValueError, match='Cannot remove team leader'):
            team.remove_member(test_user)
        
        # Clean up
        db.session.delete(team)
        db.session.delete(other_user)
        db.session.commit()

def test_team_unique_name(app, test_team):
    """Test that team names must be unique."""
    with app.app_context():
        duplicate_team = Team(name='Test Team')
        db.session.add(duplicate_team)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

def test_team_project_relationship(app, test_team, test_project):
    """Test team-project relationship."""
    with app.app_context():
        test_project.team = test_team
        db.session.commit()
        
        assert test_project in test_team.projects
        assert test_project.team == test_team

def test_team_leader_relationship(app, test_user):
    """Test team leader relationship."""
    with app.app_context():
        team = Team(name='Leadership Test', leader=test_user)
        db.session.add(team)
        db.session.commit()
        
        assert team.leader == test_user
        assert team in test_user.led_teams
        
        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_timestamps(app, test_user):
    """Test team timestamp fields."""
    with app.app_context():
        team = Team(name='Timestamp Test', leader=test_user)
        db.session.add(team)
        db.session.commit()
        
        assert team.created_at is not None
        assert team.updated_at is not None
        
        original_updated_at = team.updated_at
        
        # Modify team and check updated_at changes
        team.description = 'Updated description'
        db.session.commit()
        
        assert team.updated_at > original_updated_at
        
        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_representation(app):
    """Test string representation of team."""
    with app.app_context():
        team = Team(name='Test Team', description='A test team')
        assert str(team) == '<Team Test Team>'

def test_team_member_relationships(app, test_user):
    """Test team relationships with members."""
    with app.app_context():
        team = Team(name='Member Test Team', description='Testing member relationships')
        db.session.add(team)
        db.session.commit()

        # Test adding member
        team.add_member(test_user, role='developer')
        db.session.commit()
        assert test_user in team.members
        assert team in test_user.teams
        assert team.get_member_role(test_user) == 'developer'

        # Test updating member role
        team.update_member_role(test_user, 'team_lead')
        db.session.commit()
        assert team.get_member_role(test_user) == 'team_lead'

        # Test removing member
        team.remove_member(test_user)
        db.session.commit()
        assert test_user not in team.members
        assert team not in test_user.teams

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_project_relationships(app, test_project):
    """Test team relationships with projects."""
    with app.app_context():
        team = Team(name='Project Test Team', description='Testing project relationships')
        db.session.add(team)
        db.session.commit()

        # Test adding project
        team.add_project(test_project)
        db.session.commit()
        assert test_project in team.projects
        assert team in test_project.teams

        # Test removing project
        team.remove_project(test_project)
        db.session.commit()
        assert test_project not in team.projects
        assert team not in test_project.teams

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_invalid_team_creation(app):
    """Test invalid team creation."""
    with app.app_context():
        # Test creating team without name
        with pytest.raises(Exception):
            team = Team(description='Invalid team')
            db.session.add(team)
            db.session.commit()

def test_team_name_unique_constraint(app):
    """Test team name uniqueness constraint."""
    with app.app_context():
        team1 = Team(name='Test Team', description='First team')
        db.session.add(team1)
        db.session.commit()

        # Try to create another team with the same name
        with pytest.raises(Exception):
            team2 = Team(name='Test Team', description='Second team')
            db.session.add(team2)
            db.session.commit()

        # Clean up
        db.session.delete(team1)
        db.session.commit()

def test_team_cascade_delete(app, test_user, test_project):
    """Test that deleting a team properly handles relationships."""
    with app.app_context():
        team = Team(name='Cascade Test Team', description='Testing cascade delete')
        db.session.add(team)
        db.session.commit()

        # Add member and project
        team.add_member(test_user, role='developer')
        team.add_project(test_project)
        db.session.commit()

        # Delete team
        db.session.delete(team)
        db.session.commit()

        # Verify relationships are removed but entities still exist
        assert test_user.teams.count() == 0
        assert test_project.teams.count() == 0
        assert User.query.get(test_user.id) is not None
        assert Project.query.get(test_project.id) is not None

def test_team_member_limit(app):
    """Test team member limit constraints."""
    with app.app_context():
        team = Team(name='Limit Test Team', description='Testing member limits')
        db.session.add(team)
        db.session.commit()

        # Create max_members + 1 users
        max_members = 10  # Assuming there's a limit of 10 members per team
        users = []
        for i in range(max_members + 1):
            user = User(
                username=f'test_user_{i}',
                email=f'test{i}@example.com',
                password='password123'
            )
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        # Add users up to the limit
        for i in range(max_members):
            team.add_member(users[i], role='developer')
            db.session.commit()

        # Try to add one more user
        with pytest.raises(Exception):
            team.add_member(users[-1], role='developer')
            db.session.commit()

        # Clean up
        db.session.delete(team)
        for user in users:
            db.session.delete(user)
        db.session.commit()

def test_team_member_roles(app, test_user):
    """Test team member role validation and management."""
    with app.app_context():
        team = Team(name='Role Test Team', description='Testing roles')
        db.session.add(team)
        db.session.commit()

        # Test valid roles
        valid_roles = ['developer', 'team_lead', 'project_manager']
        for role in valid_roles:
            team.add_member(test_user, role=role)
            db.session.commit()
            assert team.get_member_role(test_user) == role
            team.remove_member(test_user)
            db.session.commit()

        # Test invalid role
        with pytest.raises(ValueError):
            team.add_member(test_user, role='invalid_role')
            db.session.commit()

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_member_role_validation(app, test_user):
    """Test validation of team member roles."""
    with app.app_context():
        team = Team(name='Role Validation Team')
        db.session.add(team)
        db.session.commit()

        # Test invalid role
        with pytest.raises(ValueError, match='Invalid role specified'):
            team.update_member_role(test_user, 'invalid_role')

        # Test updating role of non-member
        with pytest.raises(ValueError, match='User is not a member of this team'):
            team.update_member_role(test_user, 'developer')

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_get_member_role_nonmember(app, test_user):
    """Test getting role of non-member."""
    with app.app_context():
        team = Team(name='Role Test Team')
        db.session.add(team)
        db.session.commit()

        assert team.get_member_role(test_user) is None

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_multiple_projects(app):
    """Test team with multiple projects."""
    with app.app_context():
        team = Team(name='Multi-Project Team')
        db.session.add(team)
        db.session.commit()

        # Create multiple projects
        projects = []
        for i in range(3):
            project = Project(
                name=f'Project {i}',
                description=f'Test project {i}'
            )
            projects.append(project)
            team.add_project(project)
        
        db.session.add_all(projects)
        db.session.commit()

        # Verify all projects are associated
        assert len(team.projects.all()) == 3
        for project in projects:
            assert project in team.projects

        # Test removing projects
        for project in projects:
            team.remove_project(project)
        db.session.commit()

        assert len(team.projects.all()) == 0

        # Clean up
        db.session.delete(team)
        for project in projects:
            db.session.delete(project)
        db.session.commit()

def test_team_member_roles_after_readd(app, test_user):
    """Test member roles when removing and re-adding members."""
    with app.app_context():
        team = Team(name='Role Persistence Team')
        db.session.add(team)
        db.session.commit()

        # Add member with role
        team.add_member(test_user)
        team.update_member_role(test_user, 'developer')
        db.session.commit()

        # Remove and re-add member
        team.remove_member(test_user)
        db.session.commit()
        
        team.add_member(test_user)
        db.session.commit()

        # Should get default role
        assert team.get_member_role(test_user) == 'developer'

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_empty_description(app, test_user):
    """Test team creation with empty description."""
    with app.app_context():
        team = Team(name='No Description Team', leader=test_user)
        db.session.add(team)
        db.session.commit()

        assert team.description is None
        assert team.name == 'No Description Team'

        # Clean up
        db.session.delete(team)
        db.session.commit()

def test_team_name_length_validation(app):
    """Test team name length validation."""
    with app.app_context():
        # Test name that's too long (>64 characters)
        long_name = 'a' * 65
        with pytest.raises(Exception):
            team = Team(name=long_name)
            db.session.add(team)
            db.session.commit()
        db.session.rollback()

def test_team_description_length_validation(app):
    """Test team description length validation."""
    with app.app_context():
        # Test description that's too long (>256 characters)
        long_desc = 'a' * 257
        with pytest.raises(Exception):
            team = Team(name='Test Team', description=long_desc)
            db.session.add(team)
            db.session.commit()
        db.session.rollback() 