import datetime
from .models import Holiday
from office.models import OfficeAttendance, OfficeLeaveApplication


def is_second_saturday(d: datetime.date) -> bool:
    """Return True if the date is the second Saturday of its month."""
    return d.weekday() == 5 and (8 <= d.day <= 14)


def is_sunday(d: datetime.date) -> bool:
    """Return True if the date is a Sunday."""
    return d.weekday() == 6


def get_holidays_map():
    """Return a dictionary of {date_obj: holiday_obj}."""
    return {h.date: h for h in Holiday.objects.all()}


def get_holidays_dict():
    """Return a JSON-serializable dictionary of holidays { 'YYYY-MM-DD': { ... } }."""
    return {
        h.date.strftime("%Y-%m-%d"): {
            'id': h.id,
            'name': h.name,
            'description': h.description or '',
            'date': h.date.strftime("%Y-%m-%d"),
        }
        for h in Holiday.objects.all().order_by('date')
    }


def compute_office_staff_attendance(staff, target_month=None, target_year=None):
    """
    Computes complete daily attendance history and summary statistics for an office staff member.
    Automatically marks unrecorded past working days (excluding Sundays, 2nd Saturdays, and College Holidays)
    as Absent.
    """
    today = datetime.date.today()
    registered_on = (
        staff.login_info.registered_on 
        if (staff.login_info and staff.login_info.registered_on) 
        else datetime.date(2026, 7, 1)
    )

    holidays_map = get_holidays_map()
    attendances = OfficeAttendance.objects.filter(office_staff=staff)
    att_by_date = {att.date: att for att in attendances}
    
    # Approved leave applications
    approved_leaves = OfficeLeaveApplication.objects.filter(
        office_staff=staff, 
        status='A'
    )
    leave_dates = set()
    for l in approved_leaves:
        curr = l.start_date
        while curr <= l.end_date:
            leave_dates.add(curr)
            curr += datetime.timedelta(days=1)

    # Calculate date range from registered_on up to today
    start_date = registered_on
    if start_date > today:
        start_date = today

    attendance_dict = {}
    records_list = []

    # Map all actual DB records first
    for att in attendances:
        date_str = att.date.strftime("%Y-%m-%d")
        duration = None
        if att.marked_at and att.checked_out_at:
            delta = att.checked_out_at - att.marked_at
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            duration = f"{hours}h {minutes}m"

        attendance_dict[date_str] = {
            'id': att.id,
            'status': att.status,
            'status_display': att.get_status_display(),
            'marked_at_time': att.marked_at.strftime("%H:%M") if att.marked_at else "",
            'marked_at_display': att.marked_at.strftime("%I:%M %p") if att.marked_at else "",
            'checked_out_at_time': att.checked_out_at.strftime("%H:%M") if att.checked_out_at else "",
            'checked_out_at_display': att.checked_out_at.strftime("%I:%M %p") if att.checked_out_at else "",
            'is_auto_absent': False,
        }

    # Iterate over all dates from start_date to today to compute auto-absents
    curr = start_date
    while curr <= today:
        date_str = curr.strftime("%Y-%m-%d")
        
        if curr in att_by_date:
            # Already in attendance_dict
            pass
        elif curr in leave_dates:
            attendance_dict[date_str] = {
                'id': None,
                'status': 'L',
                'status_display': 'Leave',
                'marked_at_time': '',
                'marked_at_display': '',
                'checked_out_at_time': '',
                'checked_out_at_display': '',
                'is_auto_absent': False,
            }
        elif is_sunday(curr):
            # Sunday off - no auto absent
            pass
        elif is_second_saturday(curr):
            # Second Saturday off - no auto absent
            pass
        elif curr in holidays_map:
            # Holiday off - no auto absent
            pass
        elif curr < today:
            # Unrecorded past working day -> Automatic Absent!
            attendance_dict[date_str] = {
                'id': None,
                'status': 'A',
                'status_display': 'Absent',
                'marked_at_time': '',
                'marked_at_display': '',
                'checked_out_at_time': '',
                'checked_out_at_display': '',
                'is_auto_absent': True,
            }
        
        curr += datetime.timedelta(days=1)

    # Calculate overall stats
    present_days = sum(1 for v in attendance_dict.values() if v['status'] == 'P')
    absent_days = sum(1 for v in attendance_dict.values() if v['status'] == 'A')
    leave_days = sum(1 for v in attendance_dict.values() if v['status'] == 'L')
    total_days = present_days + absent_days + leave_days
    att_percentage = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0

    # Build sorted records list for the table view (ordered newest first)
    # Include all actual DB records and any auto-absent days
    all_logged_dates = sorted(
        [datetime.datetime.strptime(k, "%Y-%m-%d").date() for k in attendance_dict.keys()],
        reverse=True
    )

    records = []
    for d in all_logged_dates:
        d_str = d.strftime("%Y-%m-%d")
        info = attendance_dict[d_str]
        
        att_obj = att_by_date.get(d)
        duration = None
        if att_obj and att_obj.marked_at and att_obj.checked_out_at:
            delta = att_obj.checked_out_at - att_obj.marked_at
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            duration = f"{hours}h {minutes}m"

        records.append({
            'date': d,
            'date_str': d_str,
            'day_name': d.strftime("%A"),
            'att_id': info.get('id'),
            'status': info['status'],
            'status_display': info['status_display'],
            'marked_at_display': info['marked_at_display'],
            'checked_out_at_display': info['checked_out_at_display'],
            'duration': duration,
            'is_auto_absent': info.get('is_auto_absent', False),
        })

    return {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'att_percentage': att_percentage,
        'attendance_dict': attendance_dict,
        'records': records,
        'registered_on': registered_on,
    }
