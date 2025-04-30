from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from app.activity_log import log_activity

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Try username first, then email
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User.query.filter_by(email=form.username.data).first()
            
        if user is None or not user.check_password(form.password.data):
            log_activity(
                activity_type='failed_login',
                description=f'Failed login attempt for user: {form.username.data}',
                ip_address=request.remote_addr
            )
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        log_activity(
            activity_type='login',
            description='User logged in successfully',
            user=user,
            ip_address=request.remote_addr
        )
        flash('Logged in successfully', 'success')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_activity(
            activity_type='logout',
            description='User logged out',
            user=current_user,
            ip_address=request.remote_addr
        )
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        log_activity(
            activity_type='user_registration',
            description=f'New user registered: {user.username}',
            user=user,
            ip_address=request.remote_addr,
            additional_data={'email': user.email}
        )
        
        flash('Registration successful', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            log_activity(
                activity_type='password_reset_request',
                description='Password reset requested',
                user=user,
                ip_address=request.remote_addr
            )
        flash('Check your email for instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/request_reset.html',
                         title='Reset Password',
                         form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    
    if user is None or not user.verify_reset_token(token):
        log_activity(
            activity_type='invalid_password_reset',
            description='Invalid or expired password reset token used',
            ip_address=request.remote_addr,
            additional_data={'token': token}
        )
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        
        log_activity(
            activity_type='password_reset_complete',
            description='Password reset completed successfully',
            user=user,
            ip_address=request.remote_addr
        )
        
        flash('Your password has been reset', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form) 