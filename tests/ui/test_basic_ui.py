import pytest
from flask import url_for

def test_navbar_structure(auth_client, test_user):
    """Test navigation bar structure and links."""
    response = auth_client.get('/')
    assert response.status_code == 200
    
    # Check main navigation elements
    assert b'Dashboard' in response.data
    assert b'Projects' in response.data
    assert b'Tickets' in response.data
    assert b'Teams' in response.data
    
    # Check user-specific elements
    assert test_user.username.encode() in response.data
    assert b'Profile' in response.data
    assert b'Logout' in response.data

def test_dashboard_layout(auth_client):
    """Test dashboard page layout and components."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    
    # Check dashboard components
    assert b'Recent Activity' in response.data
    assert b'My Tickets' in response.data
    assert b'My Projects' in response.data
    assert b'Team Updates' in response.data

def test_ticket_list_layout(auth_client, test_ticket):
    """Test ticket list page layout and components."""
    response = auth_client.get('/tickets')
    assert response.status_code == 200
    
    # Check ticket list components
    assert b'All Tickets' in response.data
    assert b'Create Ticket' in response.data
    assert b'Status' in response.data
    assert b'Priority' in response.data
    assert b'Assignee' in response.data
    
    # Verify ticket appears in list
    assert test_ticket.title.encode() in response.data

def test_ticket_detail_layout(auth_client, test_ticket):
    """Test ticket detail page layout and components."""
    response = auth_client.get(f'/tickets/{test_ticket.id}')
    assert response.status_code == 200
    
    # Check ticket detail components
    assert test_ticket.title.encode() in response.data
    assert test_ticket.description.encode() in response.data
    assert b'Status' in response.data
    assert b'Priority' in response.data
    assert b'Comments' in response.data
    assert b'Edit Ticket' in response.data

def test_project_list_layout(auth_client, test_project):
    """Test project list page layout and components."""
    response = auth_client.get('/projects')
    assert response.status_code == 200
    
    # Check project list components
    assert b'All Projects' in response.data
    assert b'Create Project' in response.data
    assert test_project.name.encode() in response.data

def test_project_detail_layout(auth_client, test_project):
    """Test project detail page layout and components."""
    response = auth_client.get(f'/projects/{test_project.id}')
    assert response.status_code == 200
    
    # Check project detail components
    assert test_project.name.encode() in response.data
    assert test_project.description.encode() in response.data
    assert b'Tickets' in response.data
    assert b'Team Members' in response.data
    assert b'Project Settings' in response.data

def test_form_layouts(auth_client):
    """Test various form layouts and components."""
    # Test ticket creation form
    response = auth_client.get('/tickets/create')
    assert response.status_code == 200
    assert b'Create New Ticket' in response.data
    assert b'Title' in response.data
    assert b'Description' in response.data
    assert b'Priority' in response.data
    assert b'Status' in response.data
    
    # Test project creation form
    response = auth_client.get('/projects/create')
    assert response.status_code == 200
    assert b'Create New Project' in response.data
    assert b'Name' in response.data
    assert b'Description' in response.data

def test_responsive_layout(auth_client):
    """Test responsive design elements."""
    # Test with mobile viewport
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'}
    response = auth_client.get('/', headers=headers)
    assert response.status_code == 200
    assert b'navbar-toggler' in response.data  # Bootstrap mobile menu toggle
    
    # Test dashboard mobile layout
    response = auth_client.get('/dashboard', headers=headers)
    assert response.status_code == 200
    assert b'container-fluid' in response.data  # Bootstrap responsive container

def test_error_page_layouts(auth_client):
    """Test error page layouts."""
    # Test 404 page
    response = auth_client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
    assert b'Return to Dashboard' in response.data
    
    # Test 403 page (forbidden)
    response = auth_client.get('/admin')  # Assuming this is a protected route
    assert response.status_code == 403
    assert b'Access Denied' in response.data

def test_flash_message_display(auth_client):
    """Test flash message display in layout."""
    # Test successful action
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data  # Bootstrap alert component
    assert b'You have been logged out' in response.data

def test_theme_consistency(auth_client):
    """Test consistency of theme elements."""
    response = auth_client.get('/')
    assert response.status_code == 200
    
    # Check for consistent brand colors and styles
    assert b'primary' in response.data  # Bootstrap primary color class
    assert b'btn-primary' in response.data  # Primary button style
    assert b'navbar-dark' in response.data  # Dark navbar theme 