from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import candidate_manager_required
from .models import PreviousTestTemplate, TestCategory, CandidateTest
from django import forms


class PreviousTestTemplateForm(forms.ModelForm):
    class Meta:
        model = PreviousTestTemplate
        fields = ['name', 'name_arabic', 'max_score', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_arabic': forms.TextInput(attrs={'class': 'form-control'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '1000'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


@candidate_manager_required
def test_templates_list(request):
    """List all previous test templates"""
    templates = PreviousTestTemplate.objects.all().order_by('order', 'name')

    context = {
        'templates': templates,
        'title': 'إدارة قوالب الاختبارات السابقة'
    }

    return render(request, 'examinations/test_templates_list.html', context)


@candidate_manager_required
def test_template_create(request):
    """Create a new test template"""
    if request.method == 'POST':
        form = PreviousTestTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'تم إنشاء قالب الاختبار "{template.name_arabic}" بنجاح.')
            return redirect('examinations:test_templates_list')
    else:
        form = PreviousTestTemplateForm()

    context = {
        'form': form,
        'title': 'إضافة قالب اختبار جديد',
        'submit_text': 'إنشاء القالب'
    }

    return render(request, 'examinations/test_template_form.html', context)


@candidate_manager_required
def test_template_update(request, pk):
    """Update an existing test template"""
    template = get_object_or_404(PreviousTestTemplate, pk=pk)

    if request.method == 'POST':
        form = PreviousTestTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'تم تحديث قالب الاختبار "{template.name_arabic}" بنجاح.')
            return redirect('examinations:test_templates_list')
    else:
        form = PreviousTestTemplateForm(instance=template)

    context = {
        'form': form,
        'template': template,
        'title': f'تعديل {template.name_arabic}',
        'submit_text': 'تحديث القالب'
    }

    return render(request, 'examinations/test_template_form.html', context)


@candidate_manager_required
def test_template_delete(request, pk):
    """Delete a test template"""
    if request.method == 'POST':
        template = get_object_or_404(PreviousTestTemplate, pk=pk)
        template_name = template.name_arabic
        template.delete()
        messages.success(request, f'تم حذف قالب الاختبار "{template_name}" بنجاح.')

    return redirect('examinations:test_templates_list')


@candidate_manager_required
def test_template_toggle_active(request, pk):
    """Toggle active status of a test template"""
    if request.method == 'POST':
        template = get_object_or_404(PreviousTestTemplate, pk=pk)
        template.is_active = not template.is_active
        template.save()

        status = "تم تفعيله" if template.is_active else "تم إلغاء تفعيله"
        messages.success(request, f'قالب الاختبار "{template.name_arabic}" {status}.')

        return JsonResponse({
            'success': True,
            'is_active': template.is_active,
            'message': f'{template.name_arabic} {status}'
        })

    return JsonResponse({'success': False})
