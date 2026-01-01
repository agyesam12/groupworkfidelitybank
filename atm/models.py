from django.db import models

# Create your models here.
"""
Bank IT Operations Monitoring and Support System (BIOMSS)
Django Models Architecture

This module defines the core data models for the BIOMSS platform.
All models follow Django best practices and include comprehensive documentation.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


# ============================================================================
# USER MANAGEMENT MODELS
# ============================================================================

class User(AbstractUser):
    """
    Extended User model with role-based access control.
    Inherits from Django's AbstractUser for authentication.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('IT_OFFICER', 'IT Officer'),
        ('SUPPORT_TECH', 'Support Technician'),
        ('BRANCH_MANAGER', 'Branch Manager'),
        ('SECURITY_OFFICER', 'Security Officer'),
        ('VIEWER', 'Viewer'),
    ]
    
    user_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='VIEWER'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    is_active_staff = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'is_active_staff']),
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


# ============================================================================
# BRANCH & LOCATION MODELS
# ============================================================================

class Branch(models.Model):
    """
    Represents a physical branch location of Fidelity Bank.
    """
    BRANCH_TYPE_CHOICES = [
        ('MAIN', 'Main Branch'),
        ('SUB', 'Sub Branch'),
        ('AGENCY', 'Agency'),
        ('HQ', 'Headquarters'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    branch_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    branch_code = models.CharField(
        max_length=10,
        unique=True
    )
    name = models.CharField(max_length=200)
    branch_type = models.CharField(
        max_length=10,
        choices=BRANCH_TYPE_CHOICES,
        default='SUB'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    manager_name = models.CharField(max_length=200, blank=True, null=True)
    opening_date = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        ordering = ['name']
        indexes = [
            models.Index(fields=['branch_code']),
            models.Index(fields=['status', 'branch_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.branch_code})"


# ============================================================================
# ATM & POS MONITORING MODELS
# ============================================================================

class ATM(models.Model):
    """
    Represents ATM machines across all branches.
    """
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OUT_OF_SERVICE', 'Out of Service'),
        ('CASH_OUT', 'Cash Depleted'),
    ]
    
    atm_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    atm_code = models.CharField(
        max_length=20,
        unique=True
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='atms'
    )
    location_description = models.CharField(max_length=255)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    serial_number = models.CharField(
        max_length=100,
        unique=True
    )
    ip_address = models.GenericIPAddressField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ONLINE'
    )
    cash_level = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Current cash in the ATM (in GHS)"
    )
    max_cash_capacity = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=100000
    )
    last_cash_replenishment = models.DateTimeField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    installation_date = models.DateField()
    uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'atms'
        ordering = ['branch', 'atm_code']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['branch', 'status']),
            models.Index(fields=['atm_code']),
        ]
        verbose_name = 'ATM'
        verbose_name_plural = 'ATMs'

    def __str__(self):
        return f"ATM {self.atm_code} - {self.branch.name}"

    @property
    def cash_percentage(self):
        """Calculate current cash level as percentage of capacity."""
        if self.max_cash_capacity > 0:
            return (self.cash_level / self.max_cash_capacity) * 100
        return 0


class POSTerminal(models.Model):
    """
    Represents Point of Sale terminals deployed at merchant locations.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('FAULTY', 'Faulty'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    pos_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    terminal_id = models.CharField(
        max_length=20,
        unique=True
    )
    merchant_name = models.CharField(max_length=255)
    merchant_code = models.CharField(max_length=50)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pos_terminals'
    )
    location = models.CharField(max_length=255)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(
        max_length=100,
        unique=True
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    deployment_date = models.DateField()
    last_maintenance_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pos_terminals'
        ordering = ['merchant_name', 'terminal_id']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['terminal_id']),
            models.Index(fields=['merchant_code']),
        ]
        verbose_name = 'POS Terminal'
        verbose_name_plural = 'POS Terminals'

    def __str__(self):
        return f"POS {self.terminal_id} - {self.merchant_name}"


# ============================================================================
# SYSTEM MONITORING MODELS
# ============================================================================

class SystemMonitoring(models.Model):
    """
    Real-time monitoring of IT systems including servers, networks, and applications.
    """
    SYSTEM_TYPE_CHOICES = [
        ('SERVER', 'Server'),
        ('NETWORK', 'Network Device'),
        ('APPLICATION', 'Application'),
        ('DATABASE', 'Database'),
        ('FIREWALL', 'Firewall'),
        ('SWITCH', 'Switch'),
        ('ROUTER', 'Router'),
    ]
    
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('DOWN', 'Down'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    monitoring_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    system_name = models.CharField(max_length=255)
    system_type = models.CharField(
        max_length=20,
        choices=SYSTEM_TYPE_CHOICES
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitored_systems'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='OPERATIONAL'
    )
    cpu_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    memory_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    disk_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    network_latency = models.IntegerField(
        null=True,
        blank=True,
        help_text="Network latency in milliseconds"
    )
    uptime_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    last_check = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    is_monitored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_monitoring'
        ordering = ['-last_check']
        indexes = [
            models.Index(fields=['status', 'system_type']),
            models.Index(fields=['branch', 'status']),
        ]
        verbose_name = 'System Monitoring Entry'
        verbose_name_plural = 'System Monitoring Entries'

    def __str__(self):
        return f"{self.system_name} ({self.system_type}) - {self.status}"


# ============================================================================
# SUPPORT TICKET MODELS
# ============================================================================

class SupportTicket(models.Model):
    """
    IT support ticket system for branch technical issues.
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('ATM', 'ATM Issue'),
        ('POS', 'POS Terminal Issue'),
        ('NETWORK', 'Network Issue'),
        ('SYSTEM', 'System Issue'),
        ('SECURITY', 'Security Issue'),
        ('SOFTWARE', 'Software Issue'),
        ('HARDWARE', 'Hardware Issue'),
        ('OTHER', 'Other'),
    ]
    
    ticket_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tickets_created'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_assigned'
    )
    atm = models.ForeignKey(
        ATM,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    pos_terminal = models.ForeignKey(
        POSTerminal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    resolution_notes = models.TextField(blank=True, null=True)
    resolution_time = models.DurationField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['branch', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['ticket_number']),
        ]

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number automatically
            last_ticket = SupportTicket.objects.order_by('-id').first()
            if last_ticket and last_ticket.ticket_number:
                last_number = int(last_ticket.ticket_number.split('-')[1])
                self.ticket_number = f"TKT-{last_number + 1:06d}"
            else:
                self.ticket_number = "TKT-000001"
        super().save(*args, **kwargs)


class TicketComment(models.Model):
    """
    Comments/updates on support tickets.
    """
    comment_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comments visible only to IT staff"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.user}"


# ============================================================================
# CYBERSECURITY MODELS
# ============================================================================

class SecurityEvent(models.Model):
    """
    Logs cybersecurity events and threats.
    """
    SEVERITY_CHOICES = [
        ('INFO', 'Informational'),
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('LOGIN_FAILURE', 'Login Failure'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
        ('MALWARE', 'Malware Detection'),
        ('PHISHING', 'Phishing Attempt'),
        ('DDOS', 'DDoS Attack'),
        ('DATA_BREACH', 'Data Breach'),
        ('POLICY_VIOLATION', 'Policy Violation'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('INVESTIGATING', 'Investigating'),
        ('CONTAINED', 'Contained'),
        ('RESOLVED', 'Resolved'),
        ('FALSE_POSITIVE', 'False Positive'),
    ]
    
    event_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    target_ip = models.GenericIPAddressField(null=True, blank=True)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    description = models.TextField()
    affected_system = models.CharField(max_length=255, blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_security_events'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    detected_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['event_type', 'detected_at']),
            models.Index(fields=['branch', 'severity']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.severity} ({self.detected_at})"


# ============================================================================
# NOTIFICATION & ALERT MODELS
# ============================================================================

class Alert(models.Model):
    """
    System alerts for critical events requiring immediate attention.
    """
    ALERT_TYPE_CHOICES = [
        ('ATM_DOWN', 'ATM Down'),
        ('ATM_CASH_LOW', 'ATM Cash Low'),
        ('POS_OFFLINE', 'POS Offline'),
        ('NETWORK_DOWN', 'Network Down'),
        ('SECURITY_THREAT', 'Security Threat'),
        ('SYSTEM_FAILURE', 'System Failure'),
        ('MAINTENANCE_DUE', 'Maintenance Due'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    alert_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    atm = models.ForeignKey(
        ATM,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    pos_terminal = models.ForeignKey(
        POSTerminal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    security_event = models.ForeignKey(
        SecurityEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'alert_type']),
            models.Index(fields=['branch', 'status']),
        ]

    def __str__(self):
        return f"{self.alert_type} - {self.title}"


# ============================================================================
# REPORTS & ANALYTICS MODELS
# ============================================================================

class PerformanceReport(models.Model):
    """
    Periodic performance reports for systems, ATMs, and branches.
    """
    REPORT_TYPE_CHOICES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('QUARTERLY', 'Quarterly Report'),
        ('ANNUAL', 'Annual Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    report_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    report_type = models.CharField(
        max_length=15,
        choices=REPORT_TYPE_CHOICES
    )
    title = models.CharField(max_length=255)
    report_period_start = models.DateField()
    report_period_end = models.DateField()
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_reports'
    )
    
    # Metrics
    total_tickets = models.IntegerField(default=0)
    resolved_tickets = models.IntegerField(default=0)
    average_resolution_time = models.DurationField(null=True, blank=True)
    atm_uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pos_uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    security_incidents = models.IntegerField(default=0)
    system_downtime_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    report_data = models.JSONField(
        default=dict,
        help_text="Additional report data in JSON format"
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'performance_reports'
        ordering = ['-report_period_end']
        indexes = [
            models.Index(fields=['report_type', 'branch']),
            models.Index(fields=['report_period_start', 'report_period_end']),
        ]

    def __str__(self):
        return f"{self.report_type} - {self.title} ({self.report_period_end})"


# ============================================================================
# AUDIT TRAIL MODEL
# ============================================================================

class AuditLog(models.Model):
    """
    Comprehensive audit trail for compliance and tracking.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]
    
    log_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    changes = models.JSONField(
        default=dict,
        help_text="JSON representation of changes made"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} ({self.timestamp})"