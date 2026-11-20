"""CRM admin."""

from django.contrib import admin

from .models import (
    Activity,
    Company,
    Contact,
    Lead,
    Opportunity,
    PipelineStage,
    RevenueForecast,
)


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "phone", "created_at")
    list_filter = ("industry", "created_at")
    search_fields = ("name", "website")
    inlines = [ContactInline]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "company", "email", "phone", "role")
    list_filter = ("company", "role")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "status", "source", "owner", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("name", "email", "company__name")


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "position",
        "probability",
        "color",
        "is_closed_won",
        "is_closed_lost",
    )
    list_editable = ("position", "probability")
    list_filter = ("is_closed_won", "is_closed_lost")
    ordering = ["position"]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "stage",
        "value",
        "owner",
        "expected_close_date",
        "created_at",
    )
    list_filter = ("stage", "owner", "expected_close_date")
    search_fields = ("name", "company__name", "contact__first_name")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "type",
        "opportunity",
        "owner",
        "due_date",
        "is_completed",
    )
    list_filter = ("type", "completed_at", "due_date")
    search_fields = ("subject", "notes")


@admin.register(RevenueForecast)
class RevenueForecastAdmin(admin.ModelAdmin):
    list_display = ("month", "total_weighted", "total_pipeline", "created_at")
