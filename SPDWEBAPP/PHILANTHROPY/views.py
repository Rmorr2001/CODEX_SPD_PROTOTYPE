from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from SPDWEBAPP_CORE.domain import Conflict
from .operations import decision_is_available, submit_event, edit_event
from .models import Philanthropy_Hours_Event_and_Request
from AUTHENTICATE.models import Brother_Profile, Role
from django.utils import timezone

from PARLEYPRO.pp_decorators import requires_role
import calendar




@login_required
@requires_role('ACTIVE')
def philanthropy_dashboard(request):
    #import functions to collect context
    from .views_functions import get_academic_year_dates, get_available_academic_years
    from .views_functions import get_user_events_and_total_hours, collect_philanthropy_statistics

    # Get selected academic year start (e.g. “2024” for 2024-2025 AY)
    selected_year = int(request.GET.get('year', 
        (timezone.now().year - 1) if timezone.now().month <= 6 else timezone.now().year
    ))
    start_date, end_date = get_academic_year_dates(selected_year)

    # Get all brothers with the 'Active Member' role
    active_brothers = Brother_Profile.objects.filter(
        roles__name='ACTIVE'
    ).select_related('user')
    
    brothers_progress, total_chapter_hours, members_meeting_goal = collect_philanthropy_statistics(active_brothers, start_date, end_date)
    # Calculate averages
    total_active_members = len(active_brothers)
    avg_hours_per_brother = total_chapter_hours / total_active_members if total_active_members > 0 else 0

    # Get user's personal events
    is_philanthropy_chair = request.user.brother_profile.roles.filter(name='PHIL_CHAIR').exists()
    user_events = None
    user_total_hours = 0
    
    user_events, user_total_hours = get_user_events_and_total_hours(request,start_date, end_date)  
    context = {
        'brothers_progress': sorted(brothers_progress, key=lambda x: x['total_hours'], reverse=True),
        'total_chapter_hours': total_chapter_hours,
        'avg_hours_per_brother': avg_hours_per_brother,
        'members_meeting_goal': members_meeting_goal,
        'total_active_members': total_active_members,
        'user_events': user_events,
        'user_total_hours': user_total_hours,
        'is_philanthropy_chair': is_philanthropy_chair,
        'available_years': get_available_academic_years(),
        'selected_year': selected_year,
        'year_label': f"{selected_year}–{selected_year+1} Academic Year"
    }
    
    return render(request, 'philanthropy_dashboard.html', context)

@login_required
@requires_role('ACTIVE')
def philanthropy_request(request):
    if request.method == 'POST':
        try:
            submit_event(request.user, request.POST)
            messages.success(request, 'Philanthropy hours submitted successfully!')
            return redirect('philanthropy_dashboard')
        except ValidationError as exc:
            messages.error(request, "Error submitting hours: " + "; ".join(exc.messages))
        except PermissionDenied:
            raise
        except Exception:
            messages.error(request, "Error submitting hours: Unable to save this request. Please check before retrying.")
    
    return render(request, 'philanthropy_request.html')

@requires_role('PHIL_CHAIR','ACTIVE')
@login_required
def philanthropy_approve(request):
    from .views_functions import philanthropy_approval_POST
    
    if request.method == 'POST':
        philanthropy_approval_POST(request)
    # Get pending requests
    pending_requests = Philanthropy_Hours_Event_and_Request.objects.filter(
        philanthropy_approval_status='requested'
    ).select_related('user', 'user__brother_profile').order_by('-philanthropy_event_date')
    
    for event in pending_requests:
        event.can_decide = decision_is_available(request.user.pk, event)

    return render(request, 'philanthropy_approve.html', {'pending_requests': pending_requests})


@login_required
@requires_role('ACTIVE')
def brother_philanthropy_history(request, user_id):
    from .views_functions import retrieve_individual_brother_history
    try:
        brother = Brother_Profile.objects.select_related('user').get(user_id=user_id)
        is_philanthropy_chair = request.user.brother_profile.roles.filter(name="PHIL_CHAIR").exists()

        #grabs and sorts all of the brothers philanthropy history, outputs the total approved hours per semester
        academic_year_totals, lifetime_event_total = retrieve_individual_brother_history(brother, user_id)
        context = {
            'brother': brother,
            'academic_year_totals': academic_year_totals,
            'lifetime_total': lifetime_event_total,
            'is_philanthropy_chair': is_philanthropy_chair
        }

        
        return render(request, 'philanthropy_brother_history.html', context)
        
    except Brother_Profile.DoesNotExist:
        messages.error(request, 'Brother not found.')
        return redirect('philanthropy_dashboard')







from .exports import export_approved_philanthropy_hours

from django.shortcuts import get_object_or_404

@login_required
@requires_role('PHIL_CHAIR')
def philanthropy_edit_event(request, event_id):
    # Only PHIL_CHAIR can edit
    #if not check_user_role(request.user, 'PHIL_CHAIR'):
    #    messages.error(request, 'Only Philanthropy Chair members can edit events.')
    #    return redirect('philanthropy_dashboard')

    event = get_object_or_404(Philanthropy_Hours_Event_and_Request, id=event_id)

    if request.method == 'POST':
        try:
            event = edit_event(request.user, event_id, request.POST)
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
            return render(request, 'philanthropy_request.html', {'editing': True, 'event': event})

        messages.success(request, 'Event updated successfully.')
        return redirect('brother_philanthropy_history', user_id=event.user.id)

    context = {
        'editing': True,
        'event': event
    }
    return render(request, 'philanthropy_request.html', context)
