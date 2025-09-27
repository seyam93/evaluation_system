from django.contrib import admin
from .models import TestCategory, CandidateTest, CandidateTestSummary, Previoustests, PreviousTestTemplate


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'examination_type', 'max_score', 'is_active', 'created_at']
    list_filter = ['examination_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'max_score']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'examination_type', 'description')
        }),
        ('Settings', {
            'fields': ('max_score', 'is_active')
        }),
    )


@admin.register(CandidateTest)
class CandidateTestAdmin(admin.ModelAdmin):
    list_display = ['person', 'test_category', 'score', 'max_possible_score', 'get_percentage', 'get_grade', 'is_previous_test', 'test_date']
    list_filter = ['test_category', 'is_previous_test', 'test_date', 'created_at']
    search_fields = ['person__student_name', 'test_category__name', 'notes']
    date_hierarchy = 'test_date'

    fieldsets = (
        ('Test Information', {
            'fields': ('person', 'test_category', 'is_previous_test', 'test_date')
        }),
        ('Scores', {
            'fields': ('score', 'max_possible_score')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def get_percentage(self, obj):
        return f"{obj.percentage_score}%"
    get_percentage.short_description = 'Percentage'
    get_percentage.admin_order_field = 'score'

    def get_grade(self, obj):
        return obj.grade
    get_grade.short_description = 'Grade'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update candidate test summary after saving a test
        summary, created = CandidateTestSummary.objects.get_or_create(person=obj.person)
        summary.update_summary()


@admin.register(CandidateTestSummary)
class CandidateTestSummaryAdmin(admin.ModelAdmin):
    list_display = ['person', 'total_tests_taken', 'get_average_score', 'highest_score', 'lowest_score', 'overall_grade', 'last_test_date']
    list_filter = ['overall_grade', 'last_test_date']
    search_fields = ['person__student_name']
    readonly_fields = ['total_tests_taken', 'average_score', 'highest_score', 'lowest_score', 'last_test_date', 'overall_grade', 'updated_at']

    fieldsets = (
        ('Candidate', {
            'fields': ('person',)
        }),
        ('Test Statistics', {
            'fields': ('total_tests_taken', 'average_score', 'highest_score', 'lowest_score', 'overall_grade', 'last_test_date')
        }),
        ('System Information', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

    def get_average_score(self, obj):
        return f"{round(obj.average_score, 2)}%"
    get_average_score.short_description = 'Average Score'
    get_average_score.admin_order_field = 'average_score'

    actions = ['update_summaries']

    def update_summaries(self, request, queryset):
        for summary in queryset:
            summary.update_summary()
        self.message_user(request, f"Updated {queryset.count()} test summaries.")
    update_summaries.short_description = "Update selected test summaries"


@admin.register(Previoustests)
class PrevioustestsAdmin(admin.ModelAdmin):
    list_display = ['person', 'english_degree', 'it_degree', 'information_degree', 'nafsy_degree', 'security_degree']
    list_filter = ['english_degree', 'it_degree', 'information_degree', 'nafsy_degree', 'security_degree']
    search_fields = ['person__student_name']

    def get_queryset(self, request):
        # Show a warning that this model is deprecated
        return super().get_queryset(request)

    class Media:
        css = {
            'all': ('admin/css/deprecated.css',)
        }


@admin.register(PreviousTestTemplate)
class PreviousTestTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_arabic', 'max_score', 'is_active', 'order']
    list_filter = ['is_active', 'max_score']
    search_fields = ['name', 'name_arabic']
    list_editable = ['is_active', 'order', 'max_score']
    ordering = ['order', 'name']

    fieldsets = (
        ('Test Information', {
            'fields': ('name', 'name_arabic', 'max_score')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )
