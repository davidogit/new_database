from rest_framework import serializers
from .models import StaffAPI, Contribution, Membership, InvestmentScheme, Tenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class InvestmentSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentScheme
        fields = '__all__'

class ContributionForAPISerializer(serializers.ModelSerializer):
    """Serializer that matches the expected API format for your main system"""
    scheme_id = serializers.IntegerField(source='investment_scheme.id')
    
    class Meta:
        model = Contribution
        fields = [
            'scheme_id', 'month', 'year', 'employee_amount', 'employer_amount',
            'retro_employee_amount', 'retro_employer_amount', 'contribution_date'
        ]

class ContributionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.__str__', read_only=True)
    scheme_name = serializers.CharField(source='investment_scheme.name', read_only=True)
    
    class Meta:
        model = Contribution
        fields = [
            'id', 'member', 'member_name', 'investment_scheme', 'scheme_name',
            'month', 'year', 'employee_amount', 'employer_amount',
            'retro_employee_amount', 'retro_employer_amount', 'total_contribution',
            'contribution_date', 'approved_contribution'
        ]

class MembershipSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.__str__', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'staff', 'staff_name', 'scheme', 'scheme_name',
            'total_earnings', 'estimated_profit', 'enrolled_at'
        ]
class StaffAPIForMainSystemSerializer(serializers.ModelSerializer):
    """Serializer that matches the exact format expected by your Celery task"""
    contributions = ContributionForAPISerializer(source='contribution', many=True, read_only=True)
    
    class Meta:
        model = StaffAPI
        fields = [
            'Id', 'first_name', 'last_name', 'staff_number', 'status',
            'fund_type', 'exited_flag', 'contributions'
        ]

class StaffAPISerializer(serializers.ModelSerializer):
    contributions_list = ContributionSerializer(source='contribution', many=True, read_only=True)
    memberships = MembershipSerializer(source='membership', many=True, read_only=True)
    investment_schemes = InvestmentSchemeSerializer(source='investment_scheme', many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = StaffAPI
        fields = [
            'Id', 'first_name', 'last_name', 'staff_number', 'date_joined',
            'status', 'fund_type', 'contributions', 'estimated_profit',
            'actual_amount', 'total_amount', 'subscription_date', 'exited_date',
            'exited_flag', 'bank_name', 'bank_branch', 'bank_account_number',
            'investment_schemes', 'contributions_list', 'memberships'
        ]

class StaffAPISummarySerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField()
    contribution_count = serializers.SerializerMethodField()
    latest_contribution = serializers.SerializerMethodField()
    
    def get_contribution_count(self, obj):
        return obj.contribution.count()
    
    def get_latest_contribution(self, obj):
        latest = obj.contribution.order_by('-contribution_date').first()
        return ContributionSerializer(latest).data if latest else None
    
    class Meta:
        model = StaffAPI
        fields = [
            'Id', 'first_name', 'last_name', 'staff_number', 'status',
            'fund_type', 'contributions', 'estimated_profit', 'actual_amount',
            'total_amount', 'contribution_count', 'latest_contribution'
        ]