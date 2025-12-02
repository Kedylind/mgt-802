"""
Views for case management.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Case


@login_required
def case_list_view(request):
    """List all cases."""
    cases = Case.objects.all()
    return render(request, 'cases/list.html', {'cases': cases})


@login_required
def case_detail_view(request, case_id):
    """View details of a specific case."""
    case = get_object_or_404(Case, id=case_id)
    return render(request, 'cases/detail.html', {'case': case})

