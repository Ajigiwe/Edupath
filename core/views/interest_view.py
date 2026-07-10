from core.services.interest_service import InterestService
from core.models import Interest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.core.paginator import Paginator


@staff_required
@login_required(login_url='login')
def interest_dashboard(request):
    search = request.GET.get('search') or None

    interest_list = InterestService.get_all(search)

    paginator = Paginator(interest_list, 5)
    page_number = request.GET.get('page')
    interests = paginator.get_page(page_number)

    total_interests = interest_list.count()

    return render(request, 'admin/interest.html', {
        'interests': interests,
        'total_interests': total_interests,
        'search': search
    })


@staff_required
@login_required(login_url='login')
def create_interest(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        if not name:
            messages.error(request, "Interest is required ❌")
            return redirect('interest_dashboard')

        InterestService.create(request.POST)

        messages.success(request, "Interest added successfully ✅")
        return redirect('interest_dashboard')


@staff_required
@login_required(login_url='login')
def update_interest(request, interest_id):
    if request.method == 'POST':
        InterestService.update(interest_id, request.POST)
        messages.success(request, "Updated successfully ✅")

    return redirect('interest_dashboard')


@staff_required
@login_required(login_url='login')
def delete_interest(request, interest_id):
    InterestService.delete(interest_id)
    messages.success(request, "Deleted successfully ✅")

    return redirect('interest_dashboard')