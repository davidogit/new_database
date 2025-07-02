from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from .models import StaffAPI, Contribution, Membership, InvestmentScheme, Tenant
from .serializers import (
    StaffAPISerializer, StaffAPISummarySerializer, ContributionSerializer,
    MembershipSerializer, InvestmentSchemeSerializer, TenantSerializer,
    StaffAPIForMainSystemSerializer
)

class StaffAPIViewSet(viewsets.ModelViewSet):
    queryset = StaffAPI.objects.all()
    serializer_class = StaffAPISerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StaffAPISummarySerializer
        elif self.action == 'api_format':
            return StaffAPIForMainSystemSerializer
        return StaffAPISerializer
    
    def get_queryset(self):
        queryset = StaffAPI.objects.all()
        status_filter = self.request.query_params.get('status', None)
        fund_type = self.request.query_params.get('fund_type', None)
        search = self.request.query_params.get('search', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if fund_type:
            queryset = queryset.filter(fund_type=fund_type)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(staff_number__icontains=search)
            )
        
        return queryset.order_by('-date_joined')
    
    @action(detail=False, methods=['get'])
    def api_format(self, request):
        """
        Special endpoint that returns data in the exact format expected by your Celery task
        This mimics the API format your main system expects
        """
        queryset = self.get_queryset()
        serializer = StaffAPIForMainSystemSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def contributions(self, request, pk=None):
        staff = self.get_object()
        contributions = staff.contribution.all().order_by('-contribution_date')
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_members = StaffAPI.objects.count()
        active_members = StaffAPI.objects.filter(status='active').count()
        total_contributions = StaffAPI.objects.aggregate(
            total=Sum('contributions')
        )['total'] or 0
        
        return Response({
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': total_members - active_members,
            'total_contributions': total_contributions,
        })

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    
    def get_queryset(self):
        queryset = Contribution.objects.all()
        member_id = self.request.query_params.get('member', None)
        scheme_id = self.request.query_params.get('scheme', None)
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        if scheme_id:
            queryset = queryset.filter(investment_scheme_id=scheme_id)
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month__icontains=month)
        
        return queryset.order_by('-contribution_date')

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

class InvestmentSchemeViewSet(viewsets.ModelViewSet):
    queryset = InvestmentScheme.objects.all()
    serializer_class = InvestmentSchemeSerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
