import pytest
from rest_framework import status
from signals.models import Signal

@pytest.mark.django_db
class TestMultiTenantSecurity:
    
    def test_user_cannot_see_other_company_signals(self, api_client, user_factory, company_factory):
        comp_a = company_factory(name="Company A")
        comp_b = company_factory(name="Company B")
        
        user_a = user_factory(username="user_a", company=comp_a)
        
        Signal.objects.create(company=comp_a, severity="high")
        Signal.objects.create(company=comp_b, severity="low")
        
        api_client.force_authenticate(user=user_a)
        
        url = "/api/v1/signals/" 
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        assert response.data['count'] == 1 
        assert len(response.data['results']) == 1