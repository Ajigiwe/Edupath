from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import Institution
 # you can rename later


# def institutions_list(request):
#     institutions = Institution.objects.filter(is_active=True)
#     return render(request, 'institutions_list.html', {
#         'institutions': institutions
#     })

def institutions_list(request):
    all_institutions = Institution.objects.filter(is_active=True)

    seen = set()
    unique_institutions = []

    for inst in all_institutions:
        if inst.institutionname not in seen:
            seen.add(inst.institutionname)
            unique_institutions.append(inst)

    return render(request, 'institutions_list.html', {
        'institutions': unique_institutions
    })


