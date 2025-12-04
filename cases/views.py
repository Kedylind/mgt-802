"""
Views for case management.
"""
from django.shortcuts import render, get_object_or_404, redirect
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


@login_required
def generate_case_view(request):
    """Generate a new case using AI."""
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        case_type = request.POST.get('case_type', 'consulting')
        
        if not topic:
            from django.contrib import messages
            messages.error(request, 'Please provide a topic for the case.')
            return render(request, 'cases/generate.html', {'error': 'Topic is required'})
        
        try:
            # Initialize agent
            from agents.case_generator import CaseGenerator
            generator = CaseGenerator()
            
            # Generate content (this may take 30-60 seconds)
            case_data = generator.generate_case(topic, case_type)
            
            # Validate case data
            if not case_data or case_data.get('title', '').startswith('Error'):
                from django.contrib import messages
                messages.error(request, 'Failed to generate case. Please try again with a different topic.')
                return render(request, 'cases/generate.html', {'error': 'Generation failed'})
            
            # Save to database
            case = Case.objects.create(
                title=case_data.get('title', f"{topic} Case"),
                case_type=case_data.get('case_type', case_type),
                prompt=case_data.get('prompt', ''),
                context=case_data.get('context', {}),
                exhibits=case_data.get('exhibits', []),
                generated_by=request.user
            )
            
            from django.contrib import messages
            messages.success(request, f'Case "{case.title}" generated successfully!')
            return redirect('case_detail', case_id=case.id)
            
        except ValueError as e:
            # API key missing
            from django.contrib import messages
            error_msg = str(e)
            if 'OPENAI_API_KEY' in error_msg:
                error_msg = (
                    "OpenAI API key not configured. To fix this:\n\n"
                    "1. Create a .env file in the project root\n"
                    "2. Add: OPENAI_API_KEY=your-api-key-here\n"
                    "3. Or set it as an environment variable\n\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            messages.error(request, error_msg)
            return render(request, 'cases/generate.html', {'error': error_msg})
        except Exception as e:
            # Other errors
            import traceback
            print(f"Error in generate_case_view: {e}")
            traceback.print_exc()
            from django.contrib import messages
            messages.error(request, f'An error occurred: {str(e)}. Please try again.')
            return render(request, 'cases/generate.html', {'error': str(e)})
        
    return render(request, 'cases/generate.html')

