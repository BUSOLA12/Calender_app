import requests
import json
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def index(request):
    """Home page view"""
    return render(request, 'calendar_app/index.html')

def login_view(request):
    """Initiate Microsoft OAuth login"""
    # Clear any existing session data
    request.session.flush()
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Force session save
    request.session.save()
    
    # Debug: Print state for troubleshooting
    print(f"Generated state: {state}")
    print(f"Session key: {request.session.session_key}")
    
    # Build authorization URL
    auth_params = {
        'client_id': settings.MICROSOFT_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        'response_mode': 'query',
        'scope': ' '.join(settings.MICROSOFT_SCOPE),
        'state': state,
    }
    
    auth_url = f"{settings.MICROSOFT_AUTHORITY}/oauth2/v2.0/authorize?{urlencode(auth_params)}"
    return redirect(auth_url)

def callback(request):
    """Handle OAuth callback from Microsoft"""
    # Debug: Print callback parameters
    print(f"Callback GET params: {dict(request.GET)}")
    print(f"Session data: {dict(request.session)}")
    print(f"Session key: {request.session.session_key}")
    
    # Get state parameters
    received_state = request.GET.get('state')
    stored_state = request.session.get('oauth_state')
    
    print(f"Received state: {received_state}")
    print(f"Stored state: {stored_state}")
    
    # Verify state parameter
    if not received_state or not stored_state or received_state != stored_state:
        print("State validation failed!")
        # Clear the oauth state
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        messages.error(request, f'Authentication failed: Invalid state parameter. Please try logging in again.')
        return redirect('calendar_app:index')
    
    # Clear the used state
    del request.session['oauth_state']
    
    # Get authorization code
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        print(f"OAuth error: {error} - {error_description}")
        messages.error(request, f'Login failed: {error_description}')
        return redirect('calendar_app:index')
    
    if not code:
        messages.error(request, 'Authorization code not received')
        return redirect('calendar_app:index')
    
    # Exchange code for access token
    token_data = {
        'client_id': settings.MICROSOFT_CLIENT_ID,
        'client_secret': settings.MICROSOFT_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    
    token_url = f"{settings.MICROSOFT_AUTHORITY}/oauth2/v2.0/token"
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Store tokens in session
        request.session['access_token'] = token_info['access_token']
        request.session['refresh_token'] = token_info.get('refresh_token')
        request.session['expires_in'] = token_info['expires_in']
        request.session['token_acquired_at'] = datetime.now().timestamp()
        
        # Get user profile
        user_info = get_user_profile(token_info['access_token'])
        if user_info:
            request.session['user_name'] = user_info.get('displayName', 'User')
            request.session['user_email'] = user_info.get('mail') or user_info.get('userPrincipalName')
        
        messages.success(request, 'Successfully logged in!')
        return redirect('calendar_app:calendar')
        
    except requests.exceptions.RequestException as e:
        print(f"Token exchange error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error response: {error_data}")
            except:
                print(f"Error response text: {e.response.text}")
        messages.error(request, f'Token exchange failed. Please try again.')
        return redirect('calendar_app:index')


def get_user_profile(access_token):
    """Get user profile from Microsoft Graph"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def calendar_view(request):
    """Display calendar events"""
    access_token = request.session.get('access_token')
    if not access_token:
        messages.error(request, 'Please log in first')
        return redirect('calendar_app:login')
    
    # Check if token is still valid (simplified check)
    token_acquired_at = request.session.get('token_acquired_at', 0)
    expires_in = request.session.get('expires_in', 0)
    current_time = datetime.now().timestamp()
    
    if current_time - token_acquired_at > expires_in - 300:  # 5 min buffer
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('calendar_app:login')
    
    # Fetch calendar events
    events = get_calendar_events(access_token)
    
    context = {
        'events': events,
        'user_name': request.session.get('user_name', 'User'),
        'user_email': request.session.get('user_email'),
    }
    
    return render(request, 'calendar_app/calendar.html', context)

def get_calendar_events(access_token):
    """Fetch calendar events from Microsoft Graph"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get next 10 events, ordered by start time
    params = {
        '$select': 'subject,start,end,location,organizer,attendees',
        '$orderby': 'start/dateTime',
        '$top': 10,
        '$filter': f"start/dateTime ge '{datetime.now(timezone.utc).isoformat()}'"
    }
    
    try:
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me/events',
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data.get('value', []):
            # Parse and format event data
            start_time = parse_graph_datetime(event['start'])
            end_time = parse_graph_datetime(event['end'])
            
            events.append({
                'subject': event.get('subject', 'No Subject'),
                'start': start_time,
                'end': end_time,
                'location': event.get('location', {}).get('displayName', ''),
                'organizer': event.get('organizer', {}).get('emailAddress', {}).get('name', ''),
                'attendee_count': len(event.get('attendees', [])),
            })
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return []

def parse_graph_datetime(datetime_obj):
    """Parse Microsoft Graph datetime object"""
    try:
        dt_str = datetime_obj['dateTime']
        timezone_str = datetime_obj.get('timeZone', 'UTC')
        
        # Parse the datetime string
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        
        return {
            'datetime': dt,
            'formatted': dt.strftime('%B %d, %Y at %I:%M %p'),
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%I:%M %p'),
            'timezone': timezone_str
        }
    except (KeyError, ValueError):
        return {
            'datetime': None,
            'formatted': 'Invalid Date',
            'date': '',
            'time': '',
            'timezone': ''
        }

def logout_view(request):
    """Log out user and clear session"""
    request.session.flush()
    messages.success(request, 'Successfully logged out!')
    return redirect('calendar_app:index')
