import pytest
from flask import url_for

def test_form_validation_ui(auth_client):
    """Test client-side form validation UI."""
    # Test required fields
    response = auth_client.post('/tickets/create', data={
        'title': '',  # Empty required field
        'description': 'Test description'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'This field is required' in response.data
    assert b'form-control is-invalid' in response.data  # Bootstrap invalid form styling

def test_dynamic_status_updates(auth_client, test_ticket):
    """Test dynamic status update UI."""
    response = auth_client.get(f'/tickets/{test_ticket.id}')
    assert response.status_code == 200
    
    # Check status dropdown
    assert b'status-select' in response.data
    assert b'open' in response.data
    assert b'in_progress' in response.data
    assert b'review' in response.data
    assert b'done' in response.data

def test_search_interface(auth_client, test_ticket):
    """Test search interface components."""
    response = auth_client.get('/tickets')
    assert response.status_code == 200
    
    # Check search components
    assert b'search-form' in response.data
    assert b'search-input' in response.data
    assert b'filter-options' in response.data

def test_pagination_ui(auth_client):
    """Test pagination interface."""
    response = auth_client.get('/tickets?page=1')
    assert response.status_code == 200
    
    # Check pagination components
    assert b'pagination' in response.data
    assert b'Previous' in response.data
    assert b'Next' in response.data
    assert b'page-link' in response.data

def test_modal_dialogs(auth_client, test_ticket):
    """Test modal dialog interfaces."""
    response = auth_client.get(f'/tickets/{test_ticket.id}')
    assert response.status_code == 200
    
    # Check delete confirmation modal
    assert b'delete-modal' in response.data
    assert b'Are you sure' in response.data
    assert b'modal-footer' in response.data
    assert b'btn-danger' in response.data

def test_dropdown_menus(auth_client):
    """Test dropdown menu interfaces."""
    response = auth_client.get('/tickets/create')
    assert response.status_code == 200
    
    # Check dropdown components
    assert b'priority-select' in response.data
    assert b'dropdown-menu' in response.data
    assert b'dropdown-item' in response.data

def test_form_feedback(auth_client):
    """Test form feedback UI."""
    # Test successful submission feedback
    response = auth_client.post('/projects/create', data={
        'name': 'UI Test Project',
        'description': 'Testing form feedback'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'alert-success' in response.data
    assert b'Project created successfully' in response.data

def test_loading_states(auth_client):
    """Test loading state indicators."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    
    # Check for loading indicators
    assert b'loading-spinner' in response.data
    assert b'data-loading' in response.data

def test_responsive_tables(auth_client):
    """Test responsive table layouts."""
    response = auth_client.get('/tickets')
    assert response.status_code == 200
    
    # Check responsive table components
    assert b'table-responsive' in response.data
    assert b'table-hover' in response.data
    assert b'table-striped' in response.data

def test_tooltip_elements(auth_client):
    """Test tooltip UI elements."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    
    # Check tooltip components
    assert b'data-toggle="tooltip"' in response.data
    assert b'title=' in response.data

def test_sidebar_navigation(auth_client):
    """Test sidebar navigation interface."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    
    # Check sidebar components
    assert b'sidebar' in response.data
    assert b'sidebar-toggle' in response.data
    assert b'nav-item' in response.data

def test_card_layouts(auth_client):
    """Test card-based layouts."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    
    # Check card components
    assert b'card' in response.data
    assert b'card-header' in response.data
    assert b'card-body' in response.data
    assert b'card-footer' in response.data 