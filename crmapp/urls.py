"""CRM URLs."""

from django.urls import path

from . import views

app_name = "crmapp"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("companies/", views.company_list, name="company_list"),
    path("company/<int:pk>/", views.company_detail, name="company_detail"),
    path("company/new/", views.company_create, name="company_create"),
    path("contacts/", views.contact_list, name="contact_list"),
    path("contact/<int:pk>/", views.contact_detail, name="contact_detail"),
    path("contact/new/", views.contact_create, name="contact_create"),
    path("leads/", views.lead_list, name="lead_list"),
    path("lead/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("lead/new/", views.lead_create, name="lead_create"),
    path("opportunities/", views.opportunity_list, name="opportunity_list"),
    path("opportunity/<int:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path("opportunity/new/", views.opportunity_create, name="opportunity_create"),
    path(
        "opportunity/<int:pk>/stage/",
        views.opportunity_change_stage,
        name="opportunity_change_stage",
    ),
    path("opportunity/<int:pk>/activity/", views.add_activity, name="add_activity"),
    path("pipeline/", views.pipeline_kanban, name="pipeline_kanban"),
    path("forecast/", views.revenue_forecast, name="revenue_forecast"),
]
