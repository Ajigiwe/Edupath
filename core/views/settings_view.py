import json
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection, transaction
from django.core.management import call_command
from core.decorators import staff_required
from core.models import SiteSettings


@staff_required
@login_required
def site_settings_view(request):
    settings_obj = SiteSettings.load()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'save_keys':
            settings_obj.paystack_public_key = request.POST.get('paystack_public_key', '').strip()
            new_secret = request.POST.get('paystack_secret_key', '').strip()
            if new_secret:
                settings_obj.paystack_secret_key = new_secret
            settings_obj.save()
            messages.success(request, 'Paystack keys updated successfully.')
            return redirect('site_settings')

        if action == 'save_sms':
            settings_obj.sms_provider = request.POST.get('sms_provider', '').strip()
            settings_obj.sms_sender_id = request.POST.get('sms_sender_id', '').strip()
            new_sms_key = request.POST.get('sms_api_key', '').strip()
            if new_sms_key:
                settings_obj.sms_api_key = new_sms_key
            settings_obj.sms_api_url = request.POST.get('sms_api_url', '').strip()
            settings_obj.save()
            messages.success(request, 'SMS settings updated successfully.')
            return redirect('site_settings')

    return render(request, 'admin/settings.html', {
        'settings': settings_obj,
        'has_secret': bool(settings_obj.paystack_secret_key),
    })


@staff_required
@login_required
def download_backup(request):
    """Export database as downloadable JSON file."""
    buf = io.StringIO()
    call_command('dumpdata', '--indent', '2',
                 '--exclude', 'contenttypes',
                 '--exclude', 'auth.permission',
                 '--exclude', 'sessions.session',
                 stdout=buf)
    buf.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'edupath_backup_{timestamp}.json'
    response = HttpResponse(buf.read(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    messages.success(request, 'Backup downloaded successfully.')
    return response


@staff_required
@login_required
def clear_data(request):
    """Clear all application data after password confirmation."""
    if request.method != 'POST':
        return redirect('site_settings')

    password = request.POST.get('clear_password', '')
    if not request.user.check_password(password):
        messages.error(request, 'Incorrect password. Data clear cancelled.')
        return redirect('site_settings')

    try:
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys = OFF')
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'django_%'"
                "AND name NOT LIKE 'auth_%'"
                "AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f'DELETE FROM "{table}"')
            cursor.execute('PRAGMA foreign_keys = ON')

        messages.success(request, 'All data cleared successfully.')
    except Exception as e:
        messages.error(request, f'Clear failed: {e}')

    return redirect('site_settings')


@staff_required
@login_required
def restore_backup(request):
    """Restore database from uploaded JSON backup file."""
    if request.method != 'POST':
        return redirect('site_settings')

    # Verify admin password before destructive operation
    password = request.POST.get('admin_password', '')
    if not request.user.check_password(password):
        messages.error(request, 'Incorrect password. Restore cancelled.')
        return redirect('site_settings')

    file = request.FILES.get('backup_file')
    if not file:
        messages.error(request, 'No backup file selected.')
        return redirect('site_settings')

    # Read and validate JSON
    try:
        data = file.read().decode('utf-8')
        json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        messages.error(request, f'Invalid backup file: {e}')
        return redirect('site_settings')

    import tempfile
    import os

    tmp = None
    try:
        with transaction.atomic():
            # Clear all app data
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys = OFF')
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'django_%'"
                "AND name NOT LIKE 'auth_%'"
                "AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f'DELETE FROM \"{table}\"')
            cursor.execute('PRAGMA foreign_keys = ON')

            # Write backup to temp file for loaddata
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
            tmp.write(data)
            tmp.close()

            call_command('loaddata', tmp.name)

        messages.success(request, 'Database restored successfully from backup.')
    except Exception as e:
        messages.error(request, f'Restore failed: {e}')
    finally:
        if tmp:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    return redirect('site_settings')
