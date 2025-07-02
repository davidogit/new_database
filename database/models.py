from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
import uuid

class Tenant(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    api_endpoint_member = models.URLField(null=True)
    api_endpoint_contribution = models.URLField(null=True)
    tel_number = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    address = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}\'s Account'

class InvestmentScheme(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=15, default='')
    name = models.CharField(max_length=255, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StaffAPI(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    FUND_TYPE_CHOICES = [
        ('pension', 'Pension Fund'),
        ('provident', 'Provident Fund'),
        ('gratuity', 'Gratuity Fund'),
        ('savings', 'Savings Fund'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        related_name='staff_api'
    )
    investment_scheme = models.ManyToManyField(
        InvestmentScheme,
        related_name='staff_api'
    )
    Id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )
    first_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    staff_number = models.CharField(
        unique=True,
        max_length=20
    )
    date_joined = models.DateField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    fund_type = models.CharField(
        max_length=50,
        choices=FUND_TYPE_CHOICES
    )
    contributions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00
    )
    exited_date = models.DateField(
        null=True,
        blank=True
    )
    exited_flag = models.BooleanField(
        default=False
    )
    estimated_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    actual_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    subscription_date = models.DateField(
        null=True
    )
    updated_date = models.DateTimeField(
        auto_now=True
    )
    last_withdrawal_date = models.DateTimeField(
        null=True,
        blank=True
    )
    bank_name = models.CharField(
        max_length=255,
        default='',
        null=True,
        blank=True
    )
    bank_branch = models.CharField(
        max_length=255,
        default='',
        null=True,
        blank=True
    )
    bank_account_number = models.CharField(
        max_length=255,
        default='',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
    
    @property
    def total_amount(self):
        return (self.contributions + self.actual_amount)

class Contribution(models.Model):
    investment_scheme = models.ForeignKey(
        InvestmentScheme,
        on_delete=models.CASCADE,
        null=True
    )
    member = models.ForeignKey(
        StaffAPI,
        related_name='contribution',
        on_delete=models.CASCADE
    )
    month = models.CharField(
        max_length=20
    )
    year = models.CharField(
        max_length=4
    )
    employee_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    employer_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    retro_employee_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    retro_employer_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    contribution_date = models.DateField()
    approved_contribution = models.BooleanField(default=False)
    total_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.member.last_name}'s - {self.month} {self.year}"

    def save(self, *args, **kwargs):
        if self.contribution_date:
            self.month = self.contribution_date.strftime('%B')
            self.year = str(self.contribution_date.year)
        
        self.total_contribution = (
            self.employee_amount +
            self.employer_amount +
            self.retro_employee_amount +
            self.retro_employer_amount
        )

        super().save(*args, **kwargs)

        if self.member:
            # Update member's total contributions
            total_contributions = Contribution.objects.filter(
                member=self.member
            ).aggregate(total=Sum('total_contribution'))['total'] or Decimal(0.0)
            
            self.member.contributions = total_contributions
            self.member.save()

class Membership(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=False,
        related_name='membership'
    )
    staff = models.ForeignKey(
        StaffAPI,
        on_delete=models.CASCADE,
        null=False,
        related_name='membership'
    )
    scheme = models.ForeignKey(
        InvestmentScheme,
        on_delete=models.CASCADE,
        null=False,
        related_name='membership'
    )
    total_earnings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
    )
    estimated_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True
    )
    enrolled_at = models.DateField(
        auto_now_add=True,
        null=False,
        blank=False
    )

    class Meta:
        unique_together = ('staff', 'scheme')

    def __str__(self):
        return f'{self.staff.first_name} - Membership'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        total_earnings = Membership.objects.filter(
            staff=self.staff,
        ).aggregate(total=Sum('total_earnings'))['total'] or Decimal(0.0)

        estimated_profit = Membership.objects.filter(
            staff=self.staff,
        ).aggregate(total=Sum('estimated_profit'))['total'] or Decimal(0.0)
        
        self.staff.actual_amount = total_earnings
        self.staff.estimated_profit = estimated_profit
        self.staff.save()
