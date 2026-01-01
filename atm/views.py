from django.shortcuts import render

# Create your views here.
"""
Bank IT Operations Monitoring and Support System (BIOMSS)
Class-Based Views for CRUD Operations

This module provides comprehensive class-based views for all models in the BIOMSS platform.
All views implement proper authentication, authorization, and follow Django best practices.
"""

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from .models import (
    User, Branch, ATM, POSTerminal, SystemMonitoring,
    SupportTicket, TicketComment, SecurityEvent, Alert,
    PerformanceReport, AuditLog
)


class HomeView(View):
    template_name = 'home.html'
    def get(self, request):
        return render(request, self.template_name)
# ============================================================================
# MIXIN CLASSES FOR ROLE-BASED ACCESS CONTROL
# ============================================================================

class AdminRequiredMixin(UserPassesTestMixin):
    """Restrict access to administrators only."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')


class ITStaffRequiredMixin(UserPassesTestMixin):
    """Restrict access to IT staff (IT Officers and Support Technicians)."""
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.role in ['ADMIN', 'IT_OFFICER', 'SUPPORT_TECH'])
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')


class SecurityOfficerRequiredMixin(UserPassesTestMixin):
    """Restrict access to security officers and admins."""
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.role in ['ADMIN', 'SECURITY_OFFICER'])
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')


class AuditLogMixin:
    """Mixin to automatically log actions to audit trail."""
    
    def log_action(self, action, obj, description=None):
        """Create an audit log entry."""
        if description is None:
            description = f"{action} {obj._meta.model_name}: {str(obj)}"
        
        AuditLog.objects.create(
            user=self.request.user,
            action=action,
            model_name=obj._meta.model_name,
            object_id=str(obj.pk),
            description=description,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def get_client_ip(self):
        """Get client IP address from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


# ============================================================================
# USER MANAGEMENT VIEWS
# ============================================================================

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all users with filtering and search."""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.select_related('branch').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(employee_id__icontains=search_query)
            )
        
        # Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active_staff=(is_active == 'true'))
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = User.ROLE_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active_staff=True).count()
        return context


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Display detailed information about a user."""
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Get user statistics
        context['tickets_created'] = SupportTicket.objects.filter(created_by=user).count()
        context['tickets_assigned'] = SupportTicket.objects.filter(assigned_to=user).count()
        context['recent_activities'] = AuditLog.objects.filter(user=user).order_by('-timestamp')[:10]
        context['security_events'] = SecurityEvent.objects.filter(user=user).order_by('-detected_at')[:5]
        
        return context


class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, CreateView):
    """Create a new user."""
    model = User
    template_name = 'users/user_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'role', 
              'phone_number', 'employee_id', 'department', 'branch', 'is_active_staff']
    success_url = reverse_lazy('user-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'User {self.object.username} created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing user."""
    model = User
    template_name = 'users/user_form.html'
    fields = ['email', 'first_name', 'last_name', 'role', 
              'phone_number', 'employee_id', 'department', 'branch', 'is_active_staff']
    success_url = reverse_lazy('user-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'User {self.object.username} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update User'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a user (soft delete recommended)."""
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'User {self.object.username} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# BRANCH MANAGEMENT VIEWS
# ============================================================================

class BranchListView(LoginRequiredMixin, ListView):
    """List all branches with filtering."""
    model = Branch
    template_name = 'branches/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Branch.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(branch_code__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(region__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by branch type
        branch_type = self.request.GET.get('branch_type')
        if branch_type:
            queryset = queryset.filter(branch_type=branch_type)
        
        # Filter by region
        region = self.request.GET.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Branch.STATUS_CHOICES
        context['branch_type_choices'] = Branch.BRANCH_TYPE_CHOICES
        context['regions'] = Branch.objects.values_list('region', flat=True).distinct()
        context['total_branches'] = Branch.objects.count()
        context['active_branches'] = Branch.objects.filter(status='ACTIVE').count()
        return context


class BranchDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a branch."""
    model = Branch
    template_name = 'branches/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch = self.get_object()
        
        # Get branch statistics
        context['total_atms'] = branch.atms.count()
        context['online_atms'] = branch.atms.filter(status='ONLINE').count()
        context['total_pos'] = branch.pos_terminals.count()
        context['active_pos'] = branch.pos_terminals.filter(status='ACTIVE').count()
        context['total_users'] = branch.users.count()
        context['open_tickets'] = branch.support_tickets.filter(status='OPEN').count()
        context['recent_tickets'] = branch.support_tickets.order_by('-created_at')[:5]
        context['monitored_systems'] = branch.monitored_systems.all()
        context['recent_alerts'] = branch.alerts.filter(status='ACTIVE').order_by('-created_at')[:5]
        
        return context


class BranchCreateView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, CreateView):
    """Create a new branch."""
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['branch_code', 'name', 'branch_type', 'status', 'region', 'city',
              'address', 'phone_number', 'email', 'manager_name', 'opening_date',
              'latitude', 'longitude']
    success_url = reverse_lazy('branch-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'Branch {self.object.name} created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Branch'
        return context


class BranchUpdateView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing branch."""
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['name', 'branch_type', 'status', 'region', 'city',
              'address', 'phone_number', 'email', 'manager_name', 'opening_date',
              'latitude', 'longitude']
    success_url = reverse_lazy('branch-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'Branch {self.object.name} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Branch'
        return context


class BranchDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a branch."""
    model = Branch
    template_name = 'branches/branch_confirm_delete.html'
    success_url = reverse_lazy('branch-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'Branch {self.object.name} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ATM MANAGEMENT VIEWS
# ============================================================================

class ATMListView(LoginRequiredMixin, ListView):
    """List all ATMs with filtering."""
    model = ATM
    template_name = 'atms/atm_list.html'
    context_object_name = 'atms'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ATM.objects.select_related('branch').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(atm_code__icontains=search_query) |
                Q(location_description__icontains=search_query) |
                Q(branch__name__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active == 'true'))
        
        # Filter by cash level
        cash_level = self.request.GET.get('cash_level')
        if cash_level == 'low':
            queryset = queryset.filter(cash_level__lt=20000)
        elif cash_level == 'critical':
            queryset = queryset.filter(cash_level__lt=10000)
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ATM.STATUS_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['total_atms'] = ATM.objects.count()
        context['online_atms'] = ATM.objects.filter(status='ONLINE').count()
        context['offline_atms'] = ATM.objects.filter(status='OFFLINE').count()
        context['low_cash_atms'] = ATM.objects.filter(cash_level__lt=20000).count()
        return context


class ATMDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about an ATM."""
    model = ATM
    template_name = 'atms/atm_detail.html'
    context_object_name = 'atm'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atm = self.get_object()
        
        # Get ATM statistics
        context['open_tickets'] = atm.tickets.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
        context['recent_tickets'] = atm.tickets.order_by('-created_at')[:5]
        context['recent_alerts'] = atm.alerts.order_by('-created_at')[:5]
        context['cash_percentage'] = atm.cash_percentage
        
        return context


class ATMCreateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, CreateView):

    model = ATM
    template_name = 'atms/atm_form.html'
    fields = ['atm_code', 'branch', 'location_description', 'model', 'manufacturer',
              'serial_number', 'ip_address', 'status', 'cash_level', 'max_cash_capacity',
              'installation_date', 'is_active']
    success_url = reverse_lazy('atm-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'ATM {self.object.atm_code} created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register New ATM'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class ATMUpdateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing ATM."""
    model = ATM
    template_name = 'atms/atm_form.html'
    fields = ['branch', 'location_description', 'model', 'manufacturer',
              'ip_address', 'status', 'cash_level', 'max_cash_capacity',
              'last_maintenance_date', 'next_maintenance_date', 'uptime_percentage', 'is_active']
    success_url = reverse_lazy('atm-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'ATM {self.object.atm_code} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update ATM'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class ATMDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete an ATM."""
    model = ATM
    template_name = 'atms/atm_confirm_delete.html'
    success_url = reverse_lazy('atm-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'ATM {self.object.atm_code} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# POS TERMINAL MANAGEMENT VIEWS
# ============================================================================

class POSTerminalListView(LoginRequiredMixin, ListView):
    """List all POS terminals with filtering."""
    model = POSTerminal
    template_name = 'pos/pos_list.html'
    context_object_name = 'pos_terminals'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = POSTerminal.objects.select_related('branch').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(terminal_id__icontains=search_query) |
                Q(merchant_name__icontains=search_query) |
                Q(merchant_code__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active == 'true'))
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = POSTerminal.STATUS_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['total_pos'] = POSTerminal.objects.count()
        context['active_pos'] = POSTerminal.objects.filter(status='ACTIVE').count()
        context['faulty_pos'] = POSTerminal.objects.filter(status='FAULTY').count()
        return context


class POSTerminalDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a POS terminal."""
    model = POSTerminal
    template_name = 'pos/pos_detail.html'
    context_object_name = 'pos_terminal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pos = self.get_object()
        
        # Get POS statistics
        context['open_tickets'] = pos.tickets.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
        context['recent_tickets'] = pos.tickets.order_by('-created_at')[:5]
        context['recent_alerts'] = pos.alerts.order_by('-created_at')[:5]
        
        return context


class POSTerminalCreateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, CreateView):
    """Create a new POS terminal."""
    model = POSTerminal
    template_name = 'pos/pos_form.html'
    fields = ['terminal_id', 'merchant_name', 'merchant_code', 'branch', 'location',
              'model', 'serial_number', 'status', 'deployment_date', 'is_active']
    success_url = reverse_lazy('pos-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'POS Terminal {self.object.terminal_id} created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register New POS Terminal'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class POSTerminalUpdateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing POS terminal."""
    model = POSTerminal
    template_name = 'pos/pos_form.html'
    fields = ['merchant_name', 'merchant_code', 'branch', 'location', 'model',
              'status', 'last_maintenance_date', 'is_active']
    success_url = reverse_lazy('pos-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'POS Terminal {self.object.terminal_id} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update POS Terminal'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class POSTerminalDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a POS terminal."""
    model = POSTerminal
    template_name = 'pos/pos_confirm_delete.html'
    success_url = reverse_lazy('pos-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'POS Terminal {self.object.terminal_id} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# SYSTEM MONITORING VIEWS
# ============================================================================

class SystemMonitoringListView(LoginRequiredMixin, ITStaffRequiredMixin, ListView):
    """List all monitored systems with filtering."""
    model = SystemMonitoring
    template_name = 'systems/system_list.html'
    context_object_name = 'systems'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SystemMonitoring.objects.select_related('branch').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(system_name__icontains=search_query) |
                Q(hostname__icontains=search_query) |
                Q(ip_address__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by system type
        system_type = self.request.GET.get('system_type')
        if system_type:
            queryset = queryset.filter(system_type=system_type)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by monitored status
        is_monitored = self.request.GET.get('is_monitored')
        if is_monitored:
            queryset = queryset.filter(is_monitored=(is_monitored == 'true'))
        
        return queryset.order_by('-last_check')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = SystemMonitoring.STATUS_CHOICES
        context['system_type_choices'] = SystemMonitoring.SYSTEM_TYPE_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['total_systems'] = SystemMonitoring.objects.count()
        context['operational_systems'] = SystemMonitoring.objects.filter(status='OPERATIONAL').count()
        context['critical_systems'] = SystemMonitoring.objects.filter(status='CRITICAL').count()
        context['down_systems'] = SystemMonitoring.objects.filter(status='DOWN').count()
        return context


class SystemMonitoringDetailView(LoginRequiredMixin, ITStaffRequiredMixin, DetailView):
    """Display detailed information about a monitored system."""
    model = SystemMonitoring
    template_name = 'systems/system_detail.html'
    context_object_name = 'system'


class SystemMonitoringCreateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, CreateView):
    """Add a new system to monitoring."""
    model = SystemMonitoring
    template_name = 'systems/system_form.html'
    fields = ['system_name', 'system_type', 'branch', 'ip_address', 'hostname',
              'status', 'is_monitored', 'notes']
    success_url = reverse_lazy('system-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'System {self.object.system_name} added to monitoring.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add System to Monitoring'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class SystemMonitoringUpdateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, UpdateView):
    """Update a monitored system."""
    model = SystemMonitoring
    template_name = 'systems/system_form.html'
    fields = ['system_name', 'system_type', 'branch', 'ip_address', 'hostname',
              'status', 'cpu_usage', 'memory_usage', 'disk_usage', 'network_latency',
              'uptime_hours', 'is_monitored', 'notes']
    success_url = reverse_lazy('system-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'System {self.object.system_name} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update System'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class SystemMonitoringDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Remove a system from monitoring."""
    model = SystemMonitoring
    template_name = 'systems/system_confirm_delete.html'
    success_url = reverse_lazy('system-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'System {self.object.system_name} removed from monitoring.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# SUPPORT TICKET VIEWS
# ============================================================================

class SupportTicketListView(LoginRequiredMixin, ListView):
    """List all support tickets with filtering."""
    model = SupportTicket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SupportTicket.objects.select_related(
            'branch', 'created_by', 'assigned_to', 'atm', 'pos_terminal'
        ).all()
        
        # Filter by user role
        user = self.request.user
        if user.role == 'BRANCH_MANAGER':
            queryset = queryset.filter(branch=user.branch)
        elif user.role in ['IT_OFFICER', 'SUPPORT_TECH']:
            queryset = queryset.filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            )
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(ticket_number__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by assigned user
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = SupportTicket.STATUS_CHOICES
        context['priority_choices'] = SupportTicket.PRIORITY_CHOICES
        context['category_choices'] = SupportTicket.CATEGORY_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['it_staff'] = User.objects.filter(role__in=['IT_OFFICER', 'SUPPORT_TECH'])
        
        # Ticket statistics
        context['total_tickets'] = SupportTicket.objects.count()
        context['open_tickets'] = SupportTicket.objects.filter(status='OPEN').count()
        context['in_progress_tickets'] = SupportTicket.objects.filter(status='IN_PROGRESS').count()
        context['resolved_tickets'] = SupportTicket.objects.filter(status='RESOLVED').count()
        context['critical_tickets'] = SupportTicket.objects.filter(priority='CRITICAL').count()
        
        return context


class SupportTicketDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a support ticket."""
    model = SupportTicket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.get_object()
        
        # Get ticket comments
        context['comments'] = ticket.comments.select_related('user').order_by('created_at')
        context['it_staff'] = User.objects.filter(role__in=['IT_OFFICER', 'SUPPORT_TECH'])
        
        return context


class SupportTicketCreateView(LoginRequiredMixin, AuditLogMixin, CreateView):
    """Create a new support ticket."""
    model = SupportTicket
    template_name = 'tickets/ticket_form.html'
    fields = ['title', 'description', 'category', 'priority', 'branch', 'atm', 'pos_terminal']
    success_url = reverse_lazy('ticket-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, f'Ticket {self.object.ticket_number} created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Support Ticket'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class SupportTicketUpdateView(LoginRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing support ticket."""
    model = SupportTicket
    template_name = 'tickets/ticket_form.html'
    fields = ['title', 'description', 'category', 'priority', 'status', 
              'assigned_to', 'resolution_notes']
    success_url = reverse_lazy('ticket-list')
    
    def form_valid(self, form):
        # Auto-set resolved_at timestamp when status changes to RESOLVED
        if form.instance.status == 'RESOLVED' and not form.instance.resolved_at:
            form.instance.resolved_at = timezone.now()
            if form.instance.created_at:
                form.instance.resolution_time = timezone.now() - form.instance.created_at
        
        # Auto-set closed_at timestamp when status changes to CLOSED
        if form.instance.status == 'CLOSED' and not form.instance.closed_at:
            form.instance.closed_at = timezone.now()
        
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, f'Ticket {self.object.ticket_number} updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Ticket'
        context['it_staff'] = User.objects.filter(role__in=['IT_OFFICER', 'SUPPORT_TECH'])
        return context


class SupportTicketDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a support ticket."""
    model = SupportTicket
    template_name = 'tickets/ticket_confirm_delete.html'
    success_url = reverse_lazy('ticket-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, f'Ticket {self.object.ticket_number} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# TICKET COMMENT VIEWS
# ============================================================================

class TicketCommentCreateView(LoginRequiredMixin, AuditLogMixin, CreateView):
    """Add a comment to a support ticket."""
    model = TicketComment
    template_name = 'tickets/comment_form.html'
    fields = ['comment', 'is_internal']
    
    def form_valid(self, form):
        form.instance.ticket_id = self.kwargs['ticket_pk']
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.log_action('CREATE', self.object, f'Added comment to ticket {form.instance.ticket.ticket_number}')
        messages.success(self.request, 'Comment added successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('ticket-detail', kwargs={'pk': self.kwargs['ticket_pk']})


class TicketCommentDeleteView(LoginRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a ticket comment."""
    model = TicketComment
    template_name = 'tickets/comment_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ticket_pk = self.object.ticket.pk
        self.log_action('DELETE', self.object)
        messages.success(request, 'Comment deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('ticket-detail', kwargs={'pk': self.object.ticket.pk})


# ============================================================================
# SECURITY EVENT VIEWS
# ============================================================================

class SecurityEventListView(LoginRequiredMixin, SecurityOfficerRequiredMixin, ListView):
    """List all security events with filtering."""
    model = SecurityEvent
    template_name = 'security/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SecurityEvent.objects.select_related(
            'branch', 'user', 'assigned_to'
        ).all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(affected_system__icontains=search_query)
            )
        
        # Filter by severity
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        return queryset.order_by('-detected_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['severity_choices'] = SecurityEvent.SEVERITY_CHOICES
        context['status_choices'] = SecurityEvent.STATUS_CHOICES
        context['event_type_choices'] = SecurityEvent.EVENT_TYPE_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        
        # Security statistics
        context['total_events'] = SecurityEvent.objects.count()
        context['new_events'] = SecurityEvent.objects.filter(status='NEW').count()
        context['critical_events'] = SecurityEvent.objects.filter(severity='CRITICAL').count()
        context['investigating_events'] = SecurityEvent.objects.filter(status='INVESTIGATING').count()
        
        return context


class SecurityEventDetailView(LoginRequiredMixin, SecurityOfficerRequiredMixin, DetailView):
    """Display detailed information about a security event."""
    model = SecurityEvent
    template_name = 'security/event_detail.html'
    context_object_name = 'event'


class SecurityEventCreateView(LoginRequiredMixin, SecurityOfficerRequiredMixin, AuditLogMixin, CreateView):
    """Create a new security event."""
    model = SecurityEvent
    template_name = 'security/event_form.html'
    fields = ['event_type', 'severity', 'status', 'source_ip', 'target_ip',
              'branch', 'user', 'description', 'affected_system', 'action_taken', 'assigned_to']
    success_url = reverse_lazy('security-event-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, 'Security event logged successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Log Security Event'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['security_officers'] = User.objects.filter(role='SECURITY_OFFICER')
        return context


class SecurityEventUpdateView(LoginRequiredMixin, SecurityOfficerRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing security event."""
    model = SecurityEvent
    template_name = 'security/event_form.html'
    fields = ['event_type', 'severity', 'status', 'description', 'affected_system',
              'action_taken', 'assigned_to']
    success_url = reverse_lazy('security-event-list')
    
    def form_valid(self, form):
        # Auto-set resolved_at timestamp when status changes to RESOLVED
        if form.instance.status == 'RESOLVED' and not form.instance.resolved_at:
            form.instance.resolved_at = timezone.now()
        
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, 'Security event updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Security Event'
        context['security_officers'] = User.objects.filter(role='SECURITY_OFFICER')
        return context


class SecurityEventDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a security event."""
    model = SecurityEvent
    template_name = 'security/event_confirm_delete.html'
    success_url = reverse_lazy('security-event-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, 'Security event deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ALERT VIEWS
# ============================================================================

class AlertListView(LoginRequiredMixin, ListView):
    """List all alerts with filtering."""
    model = Alert
    template_name = 'alerts/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Alert.objects.select_related(
            'branch', 'atm', 'pos_terminal', 'security_event', 'acknowledged_by'
        ).all()
        
        # Filter by user role
        user = self.request.user
        if user.role == 'BRANCH_MANAGER':
            queryset = queryset.filter(branch=user.branch)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by alert type
        alert_type = self.request.GET.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Alert.STATUS_CHOICES
        context['alert_type_choices'] = Alert.ALERT_TYPE_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        
        # Alert statistics
        context['total_alerts'] = Alert.objects.count()
        context['active_alerts'] = Alert.objects.filter(status='ACTIVE').count()
        context['acknowledged_alerts'] = Alert.objects.filter(status='ACKNOWLEDGED').count()
        
        return context


class AlertDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about an alert."""
    model = Alert
    template_name = 'alerts/alert_detail.html'
    context_object_name = 'alert'


class AlertCreateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, CreateView):
    """Create a new alert."""
    model = Alert
    template_name = 'alerts/alert_form.html'
    fields = ['alert_type', 'title', 'message', 'branch', 'atm', 'pos_terminal', 'security_event']
    success_url = reverse_lazy('alert-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, 'Alert created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Alert'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class AlertUpdateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing alert."""
    model = Alert
    template_name = 'alerts/alert_form.html'
    fields = ['status', 'message']
    success_url = reverse_lazy('alert-list')
    
    def form_valid(self, form):
        # Auto-set acknowledged fields when status changes to ACKNOWLEDGED
        if form.instance.status == 'ACKNOWLEDGED' and not form.instance.acknowledged_at:
            form.instance.acknowledged_by = self.request.user
            form.instance.acknowledged_at = timezone.now()
        
        # Auto-set resolved_at timestamp when status changes to RESOLVED
        if form.instance.status == 'RESOLVED' and not form.instance.resolved_at:
            form.instance.resolved_at = timezone.now()
        
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, 'Alert updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Alert'
        return context


class AlertDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete an alert."""
    model = Alert
    template_name = 'alerts/alert_confirm_delete.html'
    success_url = reverse_lazy('alert-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, 'Alert deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# PERFORMANCE REPORT VIEWS
# ============================================================================

class PerformanceReportListView(LoginRequiredMixin, ListView):
    """List all performance reports with filtering."""
    model = PerformanceReport
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PerformanceReport.objects.select_related('branch', 'generated_by').all()
        
        # Filter by report type
        report_type = self.request.GET.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filter by branch
        branch_id = self.request.GET.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        return queryset.order_by('-report_period_end')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_type_choices'] = PerformanceReport.REPORT_TYPE_CHOICES
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        context['total_reports'] = PerformanceReport.objects.count()
        return context


class PerformanceReportDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a performance report."""
    model = PerformanceReport
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'


class PerformanceReportCreateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, CreateView):
    """Generate a new performance report."""
    model = PerformanceReport
    template_name = 'reports/report_form.html'
    fields = ['report_type', 'title', 'report_period_start', 'report_period_end',
              'branch', 'total_tickets', 'resolved_tickets', 'average_resolution_time',
              'atm_uptime_percentage', 'pos_uptime_percentage', 'security_incidents',
              'system_downtime_hours', 'report_data']
    success_url = reverse_lazy('report-list')
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        response = super().form_valid(form)
        self.log_action('CREATE', self.object)
        messages.success(self.request, 'Performance report generated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate Performance Report'
        context['branches'] = Branch.objects.filter(status='ACTIVE')
        return context


class PerformanceReportUpdateView(LoginRequiredMixin, ITStaffRequiredMixin, AuditLogMixin, UpdateView):
    """Update an existing performance report."""
    model = PerformanceReport
    template_name = 'reports/report_form.html'
    fields = ['title', 'total_tickets', 'resolved_tickets', 'average_resolution_time',
              'atm_uptime_percentage', 'pos_uptime_percentage', 'security_incidents',
              'system_downtime_hours', 'report_data']
    success_url = reverse_lazy('report-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('UPDATE', self.object)
        messages.success(self.request, 'Performance report updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Performance Report'
        return context


class PerformanceReportDeleteView(LoginRequiredMixin, AdminRequiredMixin, AuditLogMixin, DeleteView):
    """Delete a performance report."""
    model = PerformanceReport
    template_name = 'reports/report_confirm_delete.html'
    success_url = reverse_lazy('report-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action('DELETE', self.object)
        messages.success(request, 'Performance report deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# AUDIT LOG VIEWS
# ============================================================================

class AuditLogListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all audit logs with filtering."""
    model = AuditLog
    template_name = 'audit/audit_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(model_name__icontains=search_query)
            )
        
        # Filter by action
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by model
        model_name = self.request.GET.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_choices'] = AuditLog.ACTION_CHOICES
        context['users'] = User.objects.all()
        context['model_names'] = AuditLog.objects.values_list('model_name', flat=True).distinct()
        context['total_logs'] = AuditLog.objects.count()
        return context


class AuditLogDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Display detailed information about an audit log entry."""
    model = AuditLog
    template_name = 'audit/audit_detail.html'
    context_object_name = 'log'