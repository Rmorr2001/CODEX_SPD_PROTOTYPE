"""Shared XLSX delivery for the legacy and REST export routes."""
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Philanthropy_Hours_Event_and_Request
from AUTHENTICATE.models import Brother_Profile
# EXPORT PHILANTHROPY FUNCTION

import io
from collections import defaultdict
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment
from openpyxl.utils import get_column_letter

@login_required
#@requires_role('PHIL_CHAIR')
def export_approved_philanthropy_hours(request):
    # 1. Get all active brothers
    brothers = Brother_Profile.objects.filter(roles__name='ACTIVE').select_related('user')
    name_map = {bp.user_id: f"{bp.firstName} {bp.lastName}" for bp in brothers}
    
    # 2. Get approved events
    events = (Philanthropy_Hours_Event_and_Request.objects
        .filter(philanthropy_approval_status='approved')
        .select_related('user')
        .order_by('philanthropy_event_date')
    )

    # 3. Organize by user full name
    by_user = defaultdict(list)
    for e in events:
        name = name_map.get(e.user.id, e.user.username)
        by_user[name].append({
            'Date': e.philanthropy_event_date.strftime('%Y-%m-%d'),
            'Event': e.philanthropy_event_title,
            'Hours': e.philanthropy_event_hours,
            'Approved By': e.philanthropy_event_approver_name or '—',
        })

    # 4. Workbook setup
    wb = Workbook()
    ws = wb.active
    ws.title = 'Philanthropy Hours'
    subheaders = ['Date', 'Event', 'Hours', 'Approved By']
    palette = ['FFC7CE','C6EFCE','FFEB9C','9BC2E6','D9D9D9']
    block_size = len(subheaders) + 1
    max_rows = max((len(events) for events in by_user.values()), default=0)

    # 5. Write each block
    for idx, member_name in enumerate(sorted(by_user)):
        col0 = idx * block_size + 1
        cols = [col0 + i for i in range(len(subheaders))]
        spacer = col0 + len(subheaders)
        total_hours = sum(item['Hours'] for item in by_user[member_name])
        if total_hours < 5:
            fill_color = 'FFC7CE'  # red
        elif total_hours < 10:
            fill_color = 'FFEB9C'  # yellow
        else:
            fill_color = 'C6EFCE'  # green
        fill = PatternFill('solid', fgColor=fill_color)



        # Header
        ws.merge_cells(start_row=1, start_column=col0, end_row=1, end_column=cols[-1])
        hcell = ws.cell(row=1, column=col0, value=member_name)
        hcell.fill = fill
        hcell.alignment = Alignment(horizontal='center', vertical='center')

        # Total hours
        ws.merge_cells(start_row=2, start_column=col0, end_row=2, end_column=cols[-1])
        tcell = ws.cell(row=2, column=col0, value=f"Total: {Decimal(str(total_hours)).normalize():f}")
        tcell.fill = fill
        tcell.alignment = Alignment(horizontal='center', vertical='center')

        # Subheaders
        for j, hdr in enumerate(subheaders):
            cell = ws.cell(row=3, column=cols[j], value=hdr)
            cell.fill = fill
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Data rows
        for r, item in enumerate(by_user[member_name]):
            for j, key in enumerate(subheaders):
                ws.cell(row=4 + r, column=cols[j], value=item[key])

    # 6. Autosize
    for idx, _ in enumerate(by_user):
        base = idx * block_size + 1
        for j, hdr in enumerate(subheaders):
            col_idx = base + j
            letter = get_column_letter(col_idx)
            if hdr == 'Event':
                for row in range(3, 4 + max_rows):
                    ws.cell(row=row, column=col_idx).alignment = Alignment(wrap_text=True)
                ws.column_dimensions[letter].width = 15
            else:
                maxlen = max(
                    len(str(ws.cell(row=r, column=col_idx).value or ''))
                    for r in range(1, 4 + max_rows)
                )
                ws.column_dimensions[letter].width = maxlen + 2
        # Spacer column
        spacer_col = base + len(subheaders)
        ws.column_dimensions[get_column_letter(spacer_col)].width = 2

    # 7. Response
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=approved_philanthropy_hours.xlsx'
    return response

