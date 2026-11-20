"""Tests for django-crm CRM app."""

from datetime import date, timedelta

import pytest
from crmapp.models import (
    Activity,
    Company,
    Contact,
    Lead,
    Opportunity,
    PipelineStage,
    RevenueForecast,
)
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


# ------------------------------------------------------------------
# Models: Company
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_company_str():
    c = Company.objects.create(name="Acme Corp", industry="Tech")
    assert str(c) == "Acme Corp"


# ------------------------------------------------------------------
# Models: Contact
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_contact_str():
    company = Company.objects.create(name="Acme", industry="Tech")
    c = Contact.objects.create(
        company=company, first_name="Jane", last_name="Doe", email="jane@acme.com"
    )
    assert str(c) == "Jane Doe"


# ------------------------------------------------------------------
# Models: Lead
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_lead_str():
    lead = Lead.objects.create(name="Big Lead", status="new")
    assert str(lead) == "Big Lead"


# ------------------------------------------------------------------
# Models: PipelineStage
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_pipeline_stage_str():
    s = PipelineStage.objects.create(
        name="Proposal", slug="proposal", probability=50, position=1
    )
    assert str(s) == "Proposal"


# ------------------------------------------------------------------
# Models: Opportunity
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_opportunity_str_and_weighted():
    stage = PipelineStage.objects.create(
        name="Negotiation", slug="negotiation", probability=75, position=2
    )
    opp = Opportunity.objects.create(name="Big Deal", stage=stage, value=10000.00)
    assert str(opp) == "Big Deal"
    assert opp.weighted_value() == 7500.00


# ------------------------------------------------------------------
# Models: Activity
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_activity_str_and_completed():
    stage = PipelineStage.objects.create(
        name="Qualification", slug="qualification", probability=20, position=0
    )
    opp = Opportunity.objects.create(name="Opp", stage=stage, value=5000.00)
    act = Activity.objects.create(
        opportunity=opp, type="call", subject="Follow up call"
    )
    assert str(act) == "Call: Follow up call"
    assert act.is_completed() is False
    act.completed_at = timezone.now()
    act.save()
    assert act.is_completed() is True


# ------------------------------------------------------------------
# Models: RevenueForecast
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_revenue_forecast_str():
    rf = RevenueForecast.objects.create(
        month=date(2026, 1, 1), total_weighted=50000.00, total_pipeline=100000.00
    )
    assert "2026" in str(rf)
    assert "January" in str(rf)


# ------------------------------------------------------------------
# Views: Dashboard
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_dashboard_view(client):
    User.objects.create_user(username="agent", password="pass123")
    client.login(username="agent", password="pass123")
    url = reverse("crmapp:dashboard")
    response = client.get(url)
    assert response.status_code == 200
    assert b"CRM Dashboard" in response.content


# ------------------------------------------------------------------
# Views: Company CRUD
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_company_list_view(client):
    User.objects.create_user(username="viewer", password="pass123")
    client.login(username="viewer", password="pass123")
    Company.objects.create(name="Alpha", industry="Tech")
    Company.objects.create(name="Beta", industry="Retail")
    url = reverse("crmapp:company_list")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Alpha" in response.content
    assert b"Beta" in response.content


@pytest.mark.django_db
def test_company_create(client):
    User.objects.create_user(username="admin", password="pass123")
    client.login(username="admin", password="pass123")
    url = reverse("crmapp:company_create")
    response = client.post(
        url,
        {
            "name": "NewCo",
            "website": "https://newco.com",
            "phone": "555-0100",
            "address": "123 Main St",
            "industry": "Finance",
        },
    )
    assert response.status_code == 302
    assert Company.objects.filter(name="NewCo").exists()


# ------------------------------------------------------------------
# Views: Contact
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_contact_create(client):
    company = Company.objects.create(name="TestCo", industry="Tech")
    User.objects.create_user(username="admin2", password="pass123")
    client.login(username="admin2", password="pass123")
    url = reverse("crmapp:contact_create")
    response = client.post(
        url,
        {
            "company": company.pk,
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@testco.com",
            "phone": "555-0200",
            "role": "Manager",
        },
    )
    assert response.status_code == 302
    assert Contact.objects.filter(first_name="John", last_name="Smith").exists()


# ------------------------------------------------------------------
# Views: Lead
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_lead_create(client):
    company = Company.objects.create(name="LeadCo", industry="Tech")
    User.objects.create_user(username="leadowner", password="pass123")
    client.login(username="leadowner", password="pass123")
    url = reverse("crmapp:lead_create")
    response = client.post(
        url,
        {
            "name": "Cold Lead",
            "company": company.pk,
            "email": "cold@leadco.com",
            "source": "Website",
            "status": "new",
            "notes": "Just inquired",
            "owner": "",
        },
    )
    assert response.status_code == 302
    assert Lead.objects.filter(name="Cold Lead").exists()


# ------------------------------------------------------------------
# Views: Opportunity
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_opportunity_create(client):
    company = Company.objects.create(name="OppCo", industry="Tech")
    stage = PipelineStage.objects.create(
        name="Prospecting", slug="prospecting", probability=10, position=0
    )
    User.objects.create_user(username="oppowner", password="pass123")
    client.login(username="oppowner", password="pass123")
    url = reverse("crmapp:opportunity_create")
    response = client.post(
        url,
        {
            "name": "Big Opp",
            "company": company.pk,
            "stage": stage.pk,
            "value": "25000.00",
            "expected_close_date": "2026-12-31",
            "description": "Big deal",
            "owner": "",
        },
    )
    assert response.status_code == 302
    opp = Opportunity.objects.get(name="Big Opp")
    assert opp.value == 25000.00
    assert opp.stage == stage


# ------------------------------------------------------------------
# Views: Pipeline Kanban
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_pipeline_kanban_view(client):
    User.objects.create_user(username="kanbanuser", password="pass123")
    client.login(username="kanbanuser", password="pass123")
    stage = PipelineStage.objects.create(
        name="Demo", slug="demo", probability=40, position=1
    )
    company = Company.objects.create(name="KanbanCo", industry="Tech")
    Opportunity.objects.create(
        name="Kanban Opp", company=company, stage=stage, value=8000.00
    )
    url = reverse("crmapp:pipeline_kanban")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Kanban Opp" in response.content
    assert b"Demo" in response.content


# ------------------------------------------------------------------
# Views: Opportunity Change Stage
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_opportunity_change_stage(client):
    User.objects.create_user(username="mover", password="pass123")
    client.login(username="mover", password="pass123")
    stage1 = PipelineStage.objects.create(
        name="Stage 1", slug="stage-1", probability=10, position=0
    )
    stage2 = PipelineStage.objects.create(
        name="Stage 2", slug="stage-2", probability=50, position=1
    )
    company = Company.objects.create(name="MoveCo", industry="Tech")
    opp = Opportunity.objects.create(
        name="Movable", company=company, stage=stage1, value=1000.00
    )
    url = reverse("crmapp:opportunity_change_stage", args=[opp.pk])
    response = client.post(url, {"stage_id": stage2.pk})
    assert response.status_code == 302
    opp.refresh_from_db()
    assert opp.stage == stage2


# ------------------------------------------------------------------
# Views: Add Activity
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_add_activity(client):
    User.objects.create_user(username="actor", password="pass123")
    client.login(username="actor", password="pass123")
    stage = PipelineStage.objects.create(
        name="Call", slug="call", probability=5, position=0
    )
    opp = Opportunity.objects.create(name="Activity Opp", stage=stage, value=2000.00)
    url = reverse("crmapp:add_activity", args=[opp.pk])
    response = client.post(
        url,
        {
            "type": "email",
            "subject": "Follow up",
            "notes": "Sent proposal",
            "due_date": "2026-12-01T10:00",
        },
    )
    assert response.status_code == 302
    act = Activity.objects.get(opportunity=opp)
    assert act.subject == "Follow up"
    assert act.type == "email"


# ------------------------------------------------------------------
# Views: Revenue Forecast
# ------------------------------------------------------------------
@pytest.mark.django_db
def test_revenue_forecast_view(client):
    User.objects.create_user(username="forecaster", password="pass123")
    client.login(username="forecaster", password="pass123")
    stage = PipelineStage.objects.create(
        name="Closed Won",
        slug="closed-won",
        probability=100,
        position=5,
        is_closed_won=True,
    )
    company = Company.objects.create(name="ForecastCo", industry="Tech")
    future = date.today() + timedelta(days=30)
    Opportunity.objects.create(
        name="Future Deal",
        company=company,
        stage=stage,
        value=10000.00,
        expected_close_date=future,
    )
    url = reverse("crmapp:revenue_forecast")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Revenue Forecast" in response.content


# ------------------------------------------------------------------
# CLI / management
# ------------------------------------------------------------------
def test_manage_py_exists():
    import os

    assert os.path.exists("manage.py")
