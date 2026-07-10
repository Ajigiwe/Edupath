from django.contrib import admin
from django.utils.html import format_html
from .models import *


# ── Inlines ──

class SHSStreamSubjectInline(admin.TabularInline):
    model = SHSStreamSubject
    extra = 1
    autocomplete_fields = ['subject']


class ProgramPrerequisiteInline(admin.TabularInline):
    model = ProgramPrerequisite
    extra = 1
    autocomplete_fields = ['subject']
    verbose_name = 'Prerequisite'
    verbose_name_plural = 'Prerequisites'


class ProgramAdmissionTierInline(admin.TabularInline):
    model = ProgramAdmissionTier
    extra = 1
    verbose_name = 'Admission Tier'
    verbose_name_plural = 'Admission Tiers'


class AlternativePathwayInline(admin.TabularInline):
    model = AlternativePathway
    extra = 1
    verbose_name = 'Alternative Pathway'
    verbose_name_plural = 'Alternative Pathways'


class MCQOptionInline(admin.TabularInline):
    model = MCQOption
    extra = 1
    verbose_name = 'Option'
    verbose_name_plural = 'Options'


# ── SHS Configuration ──

@admin.register(SHSStream)
class SHSStreamAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subject_count', 'is_active']
    search_fields = ['name', 'slug']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SHSStreamSubjectInline]

    def subject_count(self, obj):
        return obj.subjects.count()
    subject_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


# ── Institution Setup ──

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(InstitutionType)
class InstitutionTypeAdmin(admin.ModelAdmin):
    list_display = ['typename', 'ownership', 'is_active']
    list_filter = ['ownership', 'is_active']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['levelsname', 'is_active']
    list_filter = ['is_active']


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['institutionname', 'institutiontype', 'level', 'location', 'is_active']
    list_filter = ['institutiontype', 'level', 'location', 'is_active']
    search_fields = ['institutionname', 'location']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'is_active']
    list_filter = ['institution', 'is_active']
    search_fields = ['name']
    autocomplete_fields = ['institution']


# ── Program Management ──

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['programname', 'interest_list', 'is_active']
    list_filter = ['interests', 'is_active']
    search_fields = ['programname']
    filter_horizontal = ['interests']
    inlines = [ProgramPrerequisiteInline]

    def interest_list(self, obj):
        return ', '.join(i.name for i in obj.interests.all()[:3])
    interest_list.short_description = 'Interests'


@admin.register(ProgramDetails)
class ProgramDetailsAdmin(admin.ModelAdmin):
    list_display = ['program', 'institution', 'cutoff_point', 'job_score', 'job_chances', 'is_active']
    list_filter = ['job_chances', 'is_active', 'institution__institutiontype', 'institution__level']
    search_fields = ['program__programname', 'institution__institutionname']
    autocomplete_fields = ['program', 'institution']
    inlines = [ProgramAdmissionTierInline, AlternativePathwayInline]
    list_select_related = ['program', 'institution']


# ── Subscription / Pricing Admin ──

class PlanFeatureThroughInline(admin.TabularInline):
    model = PlanFeatureThrough
    extra = 0
    autocomplete_fields = ['feature']
    verbose_name = 'Feature'
    verbose_name_plural = 'Included Features'


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'codename', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'codename']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly', 'price_yearly', 'sort_order', 'badge_label', 'color_display', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlanFeatureThroughInline]
    list_editable = ['sort_order']

    def color_display(self, obj):
        return format_html('<span style="display:inline-block;width:20px;height:20px;border-radius:6px;background:{};border:1px solid #d6d3d1"></span>', obj.color)
    color_display.short_description = 'Color'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew']
    list_filter = ['status', 'plan', 'auto_renew']
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user', 'plan']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'provider', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'provider', 'currency']
    search_fields = ['user__username', 'transaction_id']
    autocomplete_fields = ['user', 'subscription']


@admin.register(ProgramPrerequisite)
class ProgramPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['program', 'subject', 'requirement_level', 'min_grade']
    list_filter = ['requirement_level']
    search_fields = ['program__programname', 'subject__name']
    autocomplete_fields = ['program', 'subject']


@admin.register(ProgramAdmissionTier)
class ProgramAdmissionTierAdmin(admin.ModelAdmin):
    list_display = ['program_details', 'tier_name', 'cutoff_aggregate', 'gender', 'is_active']
    list_filter = ['tier_name', 'gender', 'is_active']
    search_fields = ['program_details__program__programname']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'program_details__program', 'program_details__institution'
        )


@admin.register(AlternativePathway)
class AlternativePathwayAdmin(admin.ModelAdmin):
    list_display = ['program_details', 'pathway_type', 'is_active']
    list_filter = ['pathway_type', 'is_active']
    search_fields = ['program_details__program__programname']


# ── Questions ──

@admin.register(SchoolLevel)
class SchoolLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'is_active']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['coursename', 'department', 'interest_list', 'is_active']
    list_filter = ['department__institution', 'is_active']
    search_fields = ['coursename']
    filter_horizontal = ['interests']
    autocomplete_fields = ['department']

    def interest_list(self, obj):
        return ', '.join(i.name for i in obj.interests.all()[:3])
    interest_list.short_description = 'Interests'


@admin.register(TheoryQuestion)
class TheoryQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'course', 'department', 'level', 'school_level']
    list_filter = ['course', 'department', 'level', 'school_level']
    search_fields = ['question']
    autocomplete_fields = ['course', 'department']

    def question_preview(self, obj):
        return obj.question[:60]
    question_preview.short_description = 'Question'


@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'course', 'department', 'level', 'school_level', 'option_count']
    list_filter = ['course', 'department', 'level', 'school_level']
    search_fields = ['question']
    autocomplete_fields = ['course', 'department']
    inlines = [MCQOptionInline]

    def question_preview(self, obj):
        return obj.question[:60]
    question_preview.short_description = 'Question'

    def option_count(self, obj):
        return obj.options.count()
    option_count.short_description = 'Options'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Paystack Configuration', {
            'fields': ('paystack_public_key', 'paystack_secret_key'),
            'description': 'Enter your live Paystack API keys here. These are used for processing payments.'
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
