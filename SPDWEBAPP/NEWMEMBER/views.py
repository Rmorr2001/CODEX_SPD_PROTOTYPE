from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .views_functions import (
    get_new_members, calculate_member_marks, get_user_submitted_marks,
    get_personal_stats, get_active_member_analytics, create_mark_requests,
    process_mark_approval, get_pending_mark_requests, get_member_mark_history,
    check_user_role,
)
from .models import NewMember_Mark_Event_and_Request
from AUTHENTICATE.models import Brother_Profile
from AUTHENTICATE.models import PClass
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404
from SPDWEBAPP_CORE.domain import Conflict
from .operations import edit_mark, revoke_mark, revision, history_target, require_marks
import uuid

def newmember_dashboard(request):
    return render(request, 'newmember_dashboard.html')

@login_required
def newmember_marks_dashboard(request):
    require_marks(request.user)
    new_members = get_new_members()
    new_members_progress = calculate_member_marks(new_members)
    
    is_active = check_user_role(request.user, 'ACTIVE')
    is_new_member = check_user_role(request.user, 'NEW_MEMBER')
    user_submitted_marks = get_user_submitted_marks(request.user) if is_active else None

    # Calculate analytics based on user role
    if is_new_member:
        personal_stats = get_personal_stats(request.user)
        analytics = None
    else:
        analytics = get_active_member_analytics(new_members_progress)
        personal_stats = None
    
    pclasses = Brother_Profile.objects.values_list('pclass', flat=True).distinct() # returns all unique classes in the database
    pclass_choices = [c[0] for c in PClass.choices]
    sorted_pclasses = sorted([pc for pc in pclasses if pc != 'Current'], key=lambda x: pclass_choices.index(x) if x in pclass_choices else float('inf'), reverse=True)
    context = {
        'new_members_progress': new_members_progress,
        'user_submitted_marks': user_submitted_marks,
        'is_active': is_active,
        'is_new_member_board': check_user_role(request.user, 'NM_BOARD'),
        'analytics': analytics,
        'personal_stats': personal_stats,
        'pclasses': sorted_pclasses
    }
    
    template_name = 'ACTIVE_newmember_marks_dashboard.html' if is_active else 'newmember_marks_dashboard.html'

    return render(request, template_name, context)

@login_required
def newmember_request(request):
    if not check_user_role(request.user, 'ACTIVE'):
        messages.error(request, 'Only active members can submit marks.')
        return redirect('newmember_marks_dashboard')
        
    if request.method == 'POST':
        success, message = create_mark_requests(
            requesting_user=request.user,
            target_users=request.POST.getlist('target_users'),
            mark_value=request.POST.get('mark_value'),
            mark_reason=request.POST.get('mark_reason'),
            mark_date=request.POST.get('mark_date'), request_key=request.POST.get('request_key')
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('newmember_marks_dashboard')
    
    new_members = get_new_members()
    return render(request, 'newmember_marks_request.html', {'new_members': new_members, 'request_key': uuid.uuid4()})

@login_required
def newmember_approve(request):
    if not check_user_role(request.user, 'NM_BOARD'):
        messages.error(request, 'Only New Member Board members can approve marks.')
        return redirect('newmember_marks_dashboard')
        
    if request.method == 'POST':
        success, message = process_mark_approval(
            request, 
            request.POST.get('mark_id'), 
            request.POST.get('action')
        )
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    pending_requests = get_pending_mark_requests()
    for mark in pending_requests:
        mark.revision = revision(mark)
    
    return render(request, 'newmember_marks_approve.html', {
        'pending_requests': pending_requests
    })

@login_required
def newmember_mark_history(request, user_id):
    try:
        new_member = history_target(request.user, user_id)
        
        marks, total_marks = get_member_mark_history(user_id)

        is_nm_board = request.user.brother_profile.roles.filter(name="NM_BOARD").exists()
        
        context = {
            'new_member': new_member,
            'marks': marks,
            'total_marks': total_marks,
            'is_negative': total_marks < 0,
            'is_nm_board': is_nm_board,
        }
        
        return render(request, 'newmember_marks_history.html', context)
        
    except (Brother_Profile.DoesNotExist, Http404):
        messages.error(request, 'New Member not found.')
        return redirect('newmember_dashboard')



@login_required
def newmember_edit_mark(request, mark_id):
    # Only NM_BOARD can edit
    if not check_user_role(request.user, 'NM_BOARD'):
        messages.error(request, 'Only New Member Board members can edit marks.')
        return redirect('newmember_marks_dashboard')

    mark = get_object_or_404(NewMember_Mark_Event_and_Request, id=mark_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'deny' and not check_user_role(request.user, 'NME'):
            messages.error(request, 'Only New Member Educators can deny marks.')
            return redirect('newmember_marks_dashboard')
        try:
            if action == 'deny':
                mark = revoke_mark(request.user, mark_id, request.POST.get('revision'))
                messages.success(request, 'Mark successfully denied.')
                return redirect('newmember_marks_dashboard')
            if action != 'update':
                raise ValidationError('Choose update or deny.')
            mark = edit_mark(request.user, mark_id, request.POST, request.POST.get('revision'))
        except (ValidationError, Conflict):
            messages.error(request, 'Invalid target user selected or mark changed. Check fields and reload before saving.')
            return redirect('newmember_edit_mark', mark_id=mark_id)
        except Exception:
            messages.error(request, 'Unable to save this mark. Check its current state before retrying.')
            return redirect('newmember_edit_mark', mark_id=mark_id)
        messages.success(request, 'Mark updated successfully.')
        return redirect('newmember_mark_history', user_id=mark.target_user_id)

    # Prepopulate form with mark data
    new_members = get_new_members()
    context = {
        'new_members': new_members,
        'editing': True,
        'mark': mark, 'revision': revision(mark)
    }
    return render(request, 'newmember_marks_request.html', context)

from .exports import export_marks

@login_required
def export_approved_newmember_marks(request):
    try:
        return export_marks(request.user, request.GET.get('pclass'))
    except PermissionDenied as exc:
        messages.error(request, str(exc))
        return redirect('newmember_marks_dashboard')
    except Exception:
        messages.error(request, 'Unable to export marks. Please check the selected class and retry.')
        return redirect('newmember_marks_dashboard')
