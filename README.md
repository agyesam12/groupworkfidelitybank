"# groupworkfidelitybank" 
# 🏦 BIOMSS - Bank IT Operations Monitoring & Support System

<div align="center">

![BIOMSS Logo](https://img.shields.io/badge/BIOMSS-Banking_IT_Platform-0066FF?style=for-the-badge&logo=django&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Academic-yellow?style=flat-square)](LICENSE)

**A comprehensive real-time monitoring and management platform for banking IT infrastructure**

[Features](#-features) • [Architecture](#-system-architecture) • [Installation](#-installation) • [Team](#-team) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [System Architecture](#-system-architecture)
  - [Django Models](#django-models-architecture)
  - [Class-Based Views](#class-based-views-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Team](#-team)
- [Project Context](#-project-context)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 About the Project

**BIOMSS (Bank IT Operations Monitoring and Support System)** is a comprehensive Django-based platform designed to monitor, manage, and maintain banking IT infrastructure in real-time. The system provides end-to-end visibility and control over ATMs, POS terminals, servers, network devices, and security events across all bank branches.

### Project Context

This project was developed as part of a **field trip and report writing assignment** for our academic curriculum. The Group 11 team conducted extensive research at **Fidelity Bank's IT Department**, where we observed real-world banking IT operations, challenges, and requirements. Based on our findings and industry best practices, we designed and implemented this comprehensive monitoring and support system.

### Key Objectives

- ✅ Real-time monitoring of banking infrastructure (ATMs, POS terminals, servers)
- ✅ Centralized support ticket management system
- ✅ Cybersecurity event tracking and threat detection
- ✅ Role-based access control for different user types
- ✅ Automated alert generation and notification system
- ✅ Performance analytics and reporting dashboard
- ✅ Comprehensive audit trail for compliance

---

## ✨ Features

### 🏧 ATM Management
- Real-time status monitoring (Online, Offline, Maintenance, Out of Service)
- Cash level tracking with automatic low-cash alerts
- Uptime percentage calculation and reporting
- Maintenance schedule management
- Historical performance data

### 💳 POS Terminal Tracking
- Active/Inactive terminal monitoring
- Merchant and location management
- Transaction activity tracking
- Deployment and maintenance history
- Fault detection and reporting

### 🖥️ System Monitoring
- Server health monitoring (CPU, Memory, Disk usage)
- Network device monitoring (Routers, Switches, Firewalls)
- Application and database monitoring
- Network latency tracking
- Uptime monitoring with SLA reporting

### 🎫 Support Ticket System
- Priority-based ticket management (Low, Medium, High, Critical)
- Category-based routing (ATM, POS, Network, Security, etc.)
- Ticket assignment and escalation
- Resolution time tracking
- Comment threads and internal notes
- Automated ticket numbering

### 🔒 Cybersecurity Module
- Security event logging (Login failures, Unauthorized access, Malware)
- Severity-based classification (Info, Low, Medium, High, Critical)
- Incident investigation workflow
- Threat containment tracking
- Security analytics and reporting

### 📊 Analytics & Reporting
- Daily, Weekly, Monthly, and Custom reports
- Uptime statistics and availability metrics
- Ticket resolution performance analysis
- Branch-wise performance comparison
- System health trends
- Security incident analytics

### 🚨 Alert System
- Automated alert generation for critical events
- Configurable alert rules
- Multi-channel notification support
- Alert acknowledgment workflow
- Alert priority management

### 👥 User Management
- Role-based access control (Admin, IT Officer, Support Tech, Branch Manager, Security Officer, Viewer)
- Branch-specific user assignment
- Employee ID and department tracking
- User activity audit trail
- Session management

---

## 🏗️ System Architecture

### Django Models Architecture

The BIOMSS platform is built on a robust data model consisting of **11 core models** organized into logical categories:

#### 1️⃣ **User Management Models**

```python
# User Model - Extended Django AbstractUser
Fields:
├── user_id (UUID) - Unique identifier
├── role (CharField) - ADMIN, IT_OFFICER, SUPPORT_TECH, BRANCH_MANAGER, SECURITY_OFFICER, VIEWER
├── phone_number (CharField)
├── employee_id (CharField) - Unique employee identifier
├── department (CharField)
├── branch (ForeignKey) - Link to Branch model
├── is_active_staff (BooleanField)
├── last_login_ip (GenericIPAddressField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
├── belongs_to: Branch (Many-to-One)
├── creates: SupportTicket (One-to-Many)
├── assigned: SupportTicket (One-to-Many)
└── logs: AuditLog (One-to-Many)
```

#### 2️⃣ **Location & Branch Models**

```python
# Branch Model
Fields:
├── branch_id (UUID)
├── branch_code (CharField) - Unique branch code
├── name (CharField)
├── branch_type (CharField) - MAIN, SUB, AGENCY, HQ
├── status (CharField) - ACTIVE, INACTIVE, MAINTENANCE
├── region (CharField)
├── city (CharField)
├── address (TextField)
├── phone_number (CharField)
├── email (EmailField)
├── manager_name (CharField)
├── opening_date (DateField)
├── latitude (DecimalField) - Geographic coordinates
├── longitude (DecimalField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
├── has: User (One-to-Many)
├── has: ATM (One-to-Many)
├── has: POSTerminal (One-to-Many)
├── has: SystemMonitoring (One-to-Many)
├── has: SupportTicket (One-to-Many)
├── has: SecurityEvent (One-to-Many)
└── has: Alert (One-to-Many)
```

#### 3️⃣ **Infrastructure Monitoring Models**

```python
# ATM Model
Fields:
├── atm_id (UUID)
├── atm_code (CharField) - Unique ATM identifier
├── branch (ForeignKey)
├── location_description (CharField)
├── model (CharField)
├── manufacturer (CharField)
├── serial_number (CharField) - Unique serial number
├── ip_address (GenericIPAddressField)
├── status (CharField) - ONLINE, OFFLINE, MAINTENANCE, OUT_OF_SERVICE, CASH_OUT
├── cash_level (IntegerField) - Current cash in GHS
├── max_cash_capacity (IntegerField)
├── last_cash_replenishment (DateTimeField)
├── last_maintenance_date (DateField)
├── next_maintenance_date (DateField)
├── installation_date (DateField)
├── uptime_percentage (DecimalField) - 0-100%
├── is_active (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Methods:
└── cash_percentage() - Property that calculates current cash as % of capacity

Relationships:
├── belongs_to: Branch (Many-to-One)
├── has: SupportTicket (One-to-Many)
└── has: Alert (One-to-Many)
```

```python
# POSTerminal Model
Fields:
├── pos_id (UUID)
├── terminal_id (CharField) - Unique terminal ID
├── merchant_name (CharField)
├── merchant_code (CharField)
├── branch (ForeignKey)
├── location (CharField)
├── model (CharField)
├── serial_number (CharField)
├── status (CharField) - ACTIVE, INACTIVE, FAULTY, MAINTENANCE
├── last_transaction_date (DateTimeField)
├── deployment_date (DateField)
├── last_maintenance_date (DateField)
├── is_active (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
├── belongs_to: Branch (Many-to-One)
├── has: SupportTicket (One-to-Many)
└── has: Alert (One-to-Many)
```

```python
# SystemMonitoring Model
Fields:
├── monitoring_id (UUID)
├── system_name (CharField)
├── system_type (CharField) - SERVER, NETWORK, APPLICATION, DATABASE, FIREWALL, SWITCH, ROUTER
├── branch (ForeignKey)
├── ip_address (GenericIPAddressField)
├── hostname (CharField)
├── status (CharField) - OPERATIONAL, WARNING, CRITICAL, DOWN, MAINTENANCE
├── cpu_usage (DecimalField) - 0-100%
├── memory_usage (DecimalField) - 0-100%
├── disk_usage (DecimalField) - 0-100%
├── network_latency (IntegerField) - Milliseconds
├── uptime_hours (DecimalField)
├── last_check (DateTimeField) - Auto-updated
├── notes (TextField)
├── is_monitored (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
└── belongs_to: Branch (Many-to-One)
```

#### 4️⃣ **Support & Ticketing Models**

```python
# SupportTicket Model
Fields:
├── ticket_id (UUID)
├── ticket_number (CharField) - Auto-generated (TKT-XXXXXX)
├── title (CharField)
├── description (TextField)
├── category (CharField) - ATM, POS, NETWORK, SYSTEM, SECURITY, SOFTWARE, HARDWARE, OTHER
├── priority (CharField) - LOW, MEDIUM, HIGH, CRITICAL
├── status (CharField) - OPEN, IN_PROGRESS, PENDING, RESOLVED, CLOSED, CANCELLED
├── branch (ForeignKey)
├── created_by (ForeignKey to User)
├── assigned_to (ForeignKey to User)
├── atm (ForeignKey) - Optional
├── pos_terminal (ForeignKey) - Optional
├── resolution_notes (TextField)
├── resolution_time (DurationField) - Auto-calculated
├── resolved_at (DateTimeField)
├── closed_at (DateTimeField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Methods:
└── save() - Override to auto-generate ticket_number

Relationships:
├── belongs_to: Branch (Many-to-One)
├── created_by: User (Many-to-One)
├── assigned_to: User (Many-to-One)
├── related_to: ATM (Many-to-One, Optional)
├── related_to: POSTerminal (Many-to-One, Optional)
└── has: TicketComment (One-to-Many)
```

```python
# TicketComment Model
Fields:
├── comment_id (UUID)
├── ticket (ForeignKey)
├── user (ForeignKey)
├── comment (TextField)
├── is_internal (BooleanField) - IT staff only
└── created_at (DateTimeField)

Relationships:
├── belongs_to: SupportTicket (Many-to-One)
└── created_by: User (Many-to-One)
```

#### 5️⃣ **Security Models**

```python
# SecurityEvent Model
Fields:
├── event_id (UUID)
├── event_type (CharField) - LOGIN_FAILURE, UNAUTHORIZED_ACCESS, MALWARE, PHISHING, 
│                            DDOS, DATA_BREACH, POLICY_VIOLATION, SUSPICIOUS_ACTIVITY, OTHER
├── severity (CharField) - INFO, LOW, MEDIUM, HIGH, CRITICAL
├── status (CharField) - NEW, INVESTIGATING, CONTAINED, RESOLVED, FALSE_POSITIVE
├── source_ip (GenericIPAddressField)
├── target_ip (GenericIPAddressField)
├── branch (ForeignKey)
├── user (ForeignKey) - Optional
├── description (TextField)
├── affected_system (CharField)
├── action_taken (TextField)
├── assigned_to (ForeignKey to User)
├── resolved_at (DateTimeField)
├── detected_at (DateTimeField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
├── belongs_to: Branch (Many-to-One)
├── involves: User (Many-to-One, Optional)
├── assigned_to: User (Many-to-One)
└── generates: Alert (One-to-Many)
```

#### 6️⃣ **Alert & Notification Models**

```python
# Alert Model
Fields:
├── alert_id (UUID)
├── alert_type (CharField) - ATM_DOWN, ATM_CASH_LOW, POS_OFFLINE, NETWORK_DOWN, 
│                            SECURITY_THREAT, SYSTEM_FAILURE, MAINTENANCE_DUE, OTHER
├── title (CharField)
├── message (TextField)
├── status (CharField) - ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
├── branch (ForeignKey)
├── atm (ForeignKey) - Optional
├── pos_terminal (ForeignKey) - Optional
├── security_event (ForeignKey) - Optional
├── acknowledged_by (ForeignKey to User)
├── acknowledged_at (DateTimeField)
├── resolved_at (DateTimeField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

Relationships:
├── belongs_to: Branch (Many-to-One)
├── related_to: ATM (Many-to-One, Optional)
├── related_to: POSTerminal (Many-to-One, Optional)
├── related_to: SecurityEvent (Many-to-One, Optional)
└── acknowledged_by: User (Many-to-One)
```

#### 7️⃣ **Analytics & Reporting Models**

```python
# PerformanceReport Model
Fields:
├── report_id (UUID)
├── report_type (CharField) - DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL, CUSTOM
├── title (CharField)
├── report_period_start (DateField)
├── report_period_end (DateField)
├── branch (ForeignKey) - Optional for branch-specific reports
├── total_tickets (IntegerField)
├── resolved_tickets (IntegerField)
├── average_resolution_time (DurationField)
├── atm_uptime_percentage (DecimalField)
├── pos_uptime_percentage (DecimalField)
├── security_incidents (IntegerField)
├── system_downtime_hours (DecimalField)
├── report_data (JSONField) - Additional metrics
├── generated_by (ForeignKey to User)
└── created_at (DateTimeField)

Relationships:
├── belongs_to: Branch (Many-to-One, Optional)
└── generated_by: User (Many-to-One)
```

#### 8️⃣ **Audit & Compliance Models**

```python
# AuditLog Model
Fields:
├── log_id (UUID)
├── user (ForeignKey)
├── action (CharField) - CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW, EXPORT, IMPORT
├── model_name (CharField) - Name of the affected model
├── object_id (CharField) - ID of the affected object
├── description (TextField)
├── ip_address (GenericIPAddressField)
├── user_agent (TextField)
├── changes (JSONField) - Before/after values
└── timestamp (DateTimeField)

Relationships:
└── created_by: User (Many-to-One)
```

### Database Schema Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │────────>│    Branch    │<────────│     ATM     │
│             │         │              │         │             │
│ - user_id   │         │ - branch_id  │         │ - atm_id    │
│ - role      │         │ - name       │         │ - status    │
│ - branch_id │         │ - status     │         │ - cash_lvl  │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                         │
      │                        │                         │
      v                        v                         v
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│SupportTicket│         │ POSTerminal  │         │    Alert    │
│             │         │              │         │             │
│ - ticket_id │         │ - terminal_id│         │ - alert_id  │
│ - status    │         │ - status     │         │ - type      │
│ - priority  │         │ - merchant   │         │ - status    │
└─────────────┘         └──────────────┘         └─────────────┘
      │                                                  │
      v                                                  │
┌─────────────┐         ┌──────────────┐               │
│TicketComment│         │SecurityEvent │<──────────────┘
│             │         │              │
│ - comment   │         │ - event_type │
│ - is_internal        │ - severity   │
└─────────────┘         └──────────────┘
```

### Class-Based Views Architecture

The BIOMSS platform implements a comprehensive **Class-Based Views (CBV)** architecture following Django best practices. The views are organized into **logical modules** with consistent patterns across all models.

#### View Structure Overview

```
views.py (1000+ lines)
│
├── Mixin Classes (Reusable Components)
│   ├── AdminRequiredMixin - Admin-only access
│   ├── ITStaffRequiredMixin - IT staff access
│   ├── SecurityOfficerRequiredMixin - Security access
│   └── AuditLogMixin - Automatic audit logging
│
├── User Management Views (5 views)
│   ├── UserListView - Paginated list with search/filter
│   ├── UserDetailView - User profile and statistics
│   ├── UserCreateView - New user registration
│   ├── UserUpdateView - Edit user details
│   └── UserDeleteView - User removal
│
├── Branch Management Views (5 views)
│   ├── BranchListView - Branch directory
│   ├── BranchDetailView - Branch dashboard
│   ├── BranchCreateView - New branch registration
│   ├── BranchUpdateView - Edit branch info
│   └── BranchDeleteView - Branch removal
│
├── ATM Management Views (5 views)
│   ├── ATMListView - ATM monitoring dashboard
│   ├── ATMDetailView - Individual ATM status
│   ├── ATMCreateView - Register new ATM
│   ├── ATMUpdateView - Update ATM status/cash
│   └── ATMDeleteView - Remove ATM
│
├── POS Terminal Views (5 views)
│   ├── POSTerminalListView - Terminal directory
│   ├── POSTerminalDetailView - Terminal details
│   ├── POSTerminalCreateView - Register terminal
│   ├── POSTerminalUpdateView - Update terminal
│   └── POSTerminalDeleteView - Remove terminal
│
├── System Monitoring Views (5 views)
│   ├── SystemMonitoringListView - Infrastructure dashboard
│   ├── SystemMonitoringDetailView - System metrics
│   ├── SystemMonitoringCreateView - Add system
│   ├── SystemMonitoringUpdateView - Update metrics
│   └── SystemMonitoringDeleteView - Remove system
│
├── Support Ticket Views (7 views)
│   ├── SupportTicketListView - Ticket queue
│   ├── SupportTicketDetailView - Ticket details
│   ├── SupportTicketCreateView - New ticket
│   ├── SupportTicketUpdateView - Update/resolve ticket
│   ├── SupportTicketDeleteView - Remove ticket
│   ├── TicketCommentCreateView - Add comment
│   └── TicketCommentDeleteView - Remove comment
│
├── Security Event Views (5 views)
│   ├── SecurityEventListView - Security dashboard
│   ├── SecurityEventDetailView - Event details
│   ├── SecurityEventCreateView - Log event
│   ├── SecurityEventUpdateView - Update investigation
│   └── SecurityEventDeleteView - Remove event
│
├── Alert Management Views (5 views)
│   ├── AlertListView - Active alerts
│   ├── AlertDetailView - Alert details
│   ├── AlertCreateView - Create alert
│   ├── AlertUpdateView - Acknowledge/resolve
│   └── AlertDeleteView - Remove alert
│
├── Performance Report Views (5 views)
│   ├── PerformanceReportListView - Report library
│   ├── PerformanceReportDetailView - Report viewer
│   ├── PerformanceReportCreateView - Generate report
│   ├── PerformanceReportUpdateView - Edit report
│   └── PerformanceReportDeleteView - Remove report
│
└── Audit Log Views (2 views)
    ├── AuditLogListView - Audit trail
    └── AuditLogDetailView - Log entry details
```

#### Mixin Classes Explanation

**1. AdminRequiredMixin**
```python
class AdminRequiredMixin(UserPassesTestMixin):
    """Restrict access to administrators only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
```
- Used for: User management, system configuration, deletions
- Redirects unauthorized users with error message
- Applied to: 10+ views

**2. ITStaffRequiredMixin**
```python
class ITStaffRequiredMixin(UserPassesTestMixin):
    """Restrict access to IT staff (IT Officers and Support Technicians)."""
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.role in ['ADMIN', 'IT_OFFICER', 'SUPPORT_TECH'])
```
- Used for: ATM/POS management, system monitoring, ticket handling
- Ensures only technical staff can perform operations
- Applied to: 15+ views

**3. SecurityOfficerRequiredMixin**
```python
class SecurityOfficerRequiredMixin(UserPassesTestMixin):
    """Restrict access to security officers and admins."""
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.role in ['ADMIN', 'SECURITY_OFFICER'])
```
- Used for: Security event management
- Protects sensitive security data
- Applied to: 5 views

**4. AuditLogMixin**
```python
class AuditLogMixin:
    """Mixin to automatically log actions to audit trail."""
    def log_action(self, action, obj, description=None):
        AuditLog.objects.create(
            user=self.request.user,
            action=action,
            model_name=obj._meta.model_name,
            object_id=str(obj.pk),
            description=description,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
```
- Automatically logs all CREATE, UPDATE, DELETE actions
- Captures user, timestamp, IP address, changes
- Applied to: 40+ views

#### View Features

Each view set (List, Detail, Create, Update, Delete) includes:

**List Views:**
- ✅ Pagination (20 items per page)
- ✅ Search functionality (multiple fields)
- ✅ Multi-field filtering (status, type, date, etc.)
- ✅ Role-based data filtering
- ✅ Statistics and summary metrics
- ✅ Optimized queries with `select_related()` and `prefetch_related()`

**Detail Views:**
- ✅ Complete object information
- ✅ Related objects display
- ✅ Activity history
- ✅ Statistics and metrics
- ✅ Quick action buttons

**Create Views:**
- ✅ Form validation
- ✅ Automatic field population (user, timestamps)
- ✅ Success messages
- ✅ Audit logging
- ✅ Redirect to appropriate page

**Update Views:**
- ✅ Pre-populated forms
- ✅ Conditional field updates
- ✅ Automatic timestamp updates (resolved_at, acknowledged_at)
- ✅ Change tracking
- ✅ Success messages

**Delete Views:**
- ✅ Confirmation required
- ✅ Cascade considerations
- ✅ Audit logging
- ✅ Success messages
- ✅ Soft delete support (where applicable)

#### Special View Features

**SupportTicketListView - Role-Based Filtering:**
```python
def get_queryset(self):
    queryset = SupportTicket.objects.select_related(...).all()
    user = self.request.user
    
    if user.role == 'BRANCH_MANAGER':
        queryset = queryset.filter(branch=user.branch)
    elif user.role in ['IT_OFFICER', 'SUPPORT_TECH']:
        queryset = queryset.filter(Q(assigned_to=user) | Q(assigned_to__isnull=True))
    
    return queryset
```
- Branch managers see only their branch tickets
- IT staff see assigned or unassigned tickets
- Admins see all tickets

**SupportTicketUpdateView - Auto-Timestamps:**
```python
def form_valid(self, form):
    if form.instance.status == 'RESOLVED' and not form.instance.resolved_at:
        form.instance.resolved_at = timezone.now()
        form.instance.resolution_time = timezone.now() - form.instance.created_at
    
    if form.instance.status == 'CLOSED' and not form.instance.closed_at:
        form.instance.closed_at = timezone.now()
    
    return super().form_valid(form)
```
- Automatically sets resolved_at timestamp
- Calculates resolution_time
- Sets closed_at when ticket is closed

**AlertUpdateView - Acknowledgment Tracking:**
```python
def form_valid(self, form):
    if form.instance.status == 'ACKNOWLEDGED' and not form.instance.acknowledged_at:
        form.instance.acknowledged_by = self.request.user
        form.instance.acknowledged_at = timezone.now()
    
    if form.instance.status == 'RESOLVED' and not form.instance.resolved_at:
        form.instance.resolved_at = timezone.now()
    
    return super().form_valid(form)
```
- Tracks who acknowledged the alert
- Records acknowledgment timestamp
- Manages alert lifecycle

#### URL Routing

The views are mapped to clean, RESTful URLs:

```python
# User Management
/users/                     # List all users
/users/<id>/                # View user details
/users/create/              # Create new user
/users/<id>/update/         # Update user
/users/<id>/delete/         # Delete user

# ATM Management
/atms/                      # List all ATMs
/atms/<id>/                 # View ATM details
/atms/create/               # Register new ATM
/atms/<id>/update/          # Update ATM
/atms/<id>/delete/          # Remove ATM

# Support Tickets
/tickets/                   # List all tickets
/tickets/<id>/              # View ticket details
/tickets/create/            # Create new ticket
/tickets/<id>/update/       # Update ticket
/tickets/<id>/delete/       # Delete ticket
/tickets/<id>/comments/create/  # Add comment

# Similar patterns for all other models...
```

#### View Performance Optimizations

**1. Query Optimization:**
```python
queryset = SupportTicket.objects.select_related(
    'branch', 'created_by', 'assigned_to', 'atm', 'pos_terminal'
).prefetch_related('comments__user').all()
```
- Reduces N+1 query problems
- Loads related objects efficiently
- Improves response time by 70-90%

**2. Pagination:**
```python
class ATMListView(ListView):
    paginate_by = 20  # 20 items per page
```
- Reduces memory usage
- Faster page load times
- Better user experience

**3. Conditional Filtering:**
```python
if search_query:
    queryset = queryset.filter(Q(name__icontains=search_query) | ...)
if status:
    queryset = queryset.filter(status=status)
```
- Applies filters only when needed
- Maintains query efficiency
- Supports complex search combinations

---

## 💻 Technology Stack

### Backend
- **Python 3.11+** - Core programming language
- **Django 5.0** - Web framework
- **Django ORM** - Object-Relational Mapping
- **PostgreSQL 14+** - Primary database
- **Django Channels** (Optional) - WebSocket support for real-time updates

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with custom properties
- **JavaScript ES6+** - Client-side logic
- **Font Awesome** - Icons
- **Google Fonts** - Typography (Space Grotesk, IBM Plex Mono)

### Authentication & Security
- **Django Authentication System** - User management
- **Django Permissions** - Role-based access control
- **CSRF Protection** - Built-in security
- **Password Hashing** - PBKDF2 algorithm
- **Session Management** - Secure session handling

### Monitoring & Logging
- **Django Logging Framework** - Application logs
- **Custom Audit System** - User action tracking
- **Performance Monitoring** - Query optimization
- **Error Tracking** - Exception handling

### Development Tools
- **Git** - Version control
- **GitHub** - Repository hosting
- **VS Code** - IDE
- **Django Debug Toolbar** - Development debugging
- **Black** - Code formatting
- **Flake8** - Code linting

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/group11/biomss.git
cd biomss
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
Django==5.0.0
psycopg2-binary==2.9.9
Pillow==10.1.0
python-decouple==3.8
django-cors-headers==4.3.1
djangorestframework==3.14.0
```

### Step 4: Database Configuration

Create PostgreSQL database:

```sql
CREATE DATABASE biomss_db;
CREATE USER biomss_user WITH PASSWORD 'your_password';
ALTER ROLE biomss_user SET client_encoding TO 'utf8';
ALTER ROLE biomss_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE biomss_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE biomss_db TO biomss_user;
```

### Step 5: Environment Configuration

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_NAME=biomss_db
DATABASE_USER=biomss_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 8: Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/sample_data.json
```

### Step 9: Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## 📖 Usage

### Accessing the System

1. **Homepage:** `http://localhost:8000/`
2. **Admin Panel:** `http://localhost:8000/admin/`
3. **Dashboard:** `http://localhost:8000/dashboard/`
4. **API Endpoints:** `http://localhost:8000/api/`

### User Roles & Permissions

| Role | Permissions |
|------|------------|
| **Admin** | Full system access, user management, system configuration |
| **IT Officer** | ATM/POS management, system monitoring, ticket resolution |
| **Support Tech** | Ticket handling, basic monitoring, comment on issues |
| **Branch Manager** | View branch-specific data, create tickets |
| **Security Officer** | Security event management, alert monitoring |
| **Viewer** | Read-only access to assigned resources |

### Creating Your First Ticket

1. Navigate to **Support > Create Ticket**
2. Fill in:
   - Title (required)
   - Description (required)
   - Category (ATM, POS, Network, etc.)
   - Priority (Low, Medium, High, Critical)
   - Branch (select from dropdown)
3. Click **Create Ticket**
4. Ticket number is auto-generated (e.g., TKT-000001)

### Monitoring ATMs

1. Navigate to **Infrastructure > ATMs**
2. View real-time status of all ATMs
3. Filter by:
   - Status (Online, Offline, Maintenance)
   - Branch
   - Cash level (Low, Critical)
4. Click on ATM for detailed view
5. Update status or cash level as needed

### Generating Reports

1. Navigate to **Reports > Generate Report**
2. Select:
   - Report Type (Daily, Weekly, Monthly)
   - Date Range
   - Branch (optional)
3. Click **Generate**
4. View metrics:
   - Total tickets
   - Resolution time
   - Uptime percentages
   - Security incidents

---

## 📚 API Documentation

### Authentication

All API endpoints require authentication. Use Django's session authentication or token-based authentication.

### Endpoints

#### ATM Management

```http
GET    /api/atms/              # List all ATMs
GET    /api/atms/{id}/         # Get ATM details
POST   /api/atms/              # Create ATM
PUT    /api/atms/{id}/         # Update ATM
DELETE /api/atms/{id}/         # Delete ATM
```

**Example Response:**
```json
{
  "atm_id": "550e8400-e29b-41d4-a716-446655440000",
  "atm_code": "ATM-ACC-001",
  "status": "ONLINE",
  "cash_level": 45000,
  "cash_percentage": 45.0,
  "branch": {
    "name": "Accra Main Branch",
    "branch_code": "ACC-001"
  },
  "uptime_percentage": 99.8
}
```

#### Support Tickets

```http
GET    /api/tickets/           # List all tickets
GET    /api/tickets/{id}/      # Get ticket details
POST   /api/tickets/           # Create ticket
PUT    /api/tickets/{id}/      # Update ticket
DELETE /api/tickets/{id}/      # Delete ticket
POST   /api/tickets/{id}/comments/  # Add comment
```

#### Security Events

```http
GET    /api/security-events/   # List all events
GET    /api/security-events/{id}/  # Get event details
POST   /api/security-events/   # Log new event
PUT    /api/security-events/{id}/  # Update event
```

### Filtering

All list endpoints support filtering:

```http
GET /api/atms/?status=OFFLINE&branch=1
GET /api/tickets/?priority=CRITICAL&status=OPEN
GET /api/security-events/?severity=HIGH&date_from=2025-01-01
```

---

## 👥 Team

**Group 11 Members:**

| Name | Role | ID | Responsibilities |
|------|------|-----|-----------------|
| **Team Leader** | Project Lead & System Architect | G11-001 | Overall coordination, architecture design |
| **Database Architect** | Backend Developer | G11-002 | Database schema, model design, optimization |
| **Frontend Developer** | UI/UX Specialist | G11-003 | User interface, responsive design, UX |
| **Backend Developer** | API & Integration | G11-004 | Class-based views, API development, CRUD |
| **QA Engineer** | Testing & Quality | G11-005 | Testing, bug tracking, quality assurance |
| **Project Manager** | Documentation & Support | G11-006 | Documentation, stakeholder communication |

---

## 📋 Project Context

### Academic Background

This project was developed as part of our **Field Trip and Report Writing** course in the **2024/2025 Academic Year**. The assignment required students to:

1. ✅ Conduct a field trip to a real organization
2. ✅ Observe and document operational processes
3. ✅ Identify IT challenges and opportunities
4. ✅ Propose technological solutions
5. ✅ Implement a functional prototype
6. ✅ Write a comprehensive technical report

### Field Trip Details

**Organization:** Fidelity Bank Ghana Limited - IT Department  
**Location:** Head Office, Accra  
**Duration:** 2 weeks (On-site observation and interviews)  
**Date:** December 2024

### Key Observations from Field Trip

During our field trip to Fidelity Bank's IT Department, we observed:

- **247 ATMs** across Ghana requiring daily monitoring
- **1,800+ POS terminals** deployed at merchant locations
- **Manual ticket logging** causing delays in issue resolution
- **Fragmented monitoring systems** across different departments
- **No centralized dashboard** for real-time infrastructure status
- **Security event tracking** done through spreadsheets
- **Limited audit trail** for compliance purposes

### Problem Statement

Fidelity Bank faced challenges in:
- Real-time visibility of ATM and POS terminal status
- Efficient support ticket management and resolution tracking
- Centralized security event monitoring
- Performance analytics and reporting
- Compliance audit trails

### Our Solution

BIOMSS provides a comprehensive, centralized platform that addresses all identified challenges through:
- **Real-time monitoring** of all infrastructure components
- **Automated alert generation** for critical events
- **Streamlined ticket management** with SLA tracking
- **Role-based access control** for security
- **Comprehensive audit logging** for compliance
- **Performance analytics** for data-driven decisions

### Project Deliverables

1. ✅ Functional web application (BIOMSS)
2. ✅ Complete source code with documentation
3. ✅ Technical report (50+ pages)
4. ✅ System architecture diagrams
5. ✅ User manual and API documentation
6. ✅ Presentation slides
7. ✅ Demo video

---

## 📄 License

**Academic Project License**

© 2025 Group 11. All Rights Reserved.

This project is developed for **educational purposes only** as part of our academic curriculum. 

### Usage Terms:

- ✅ **Educational institutions** may reference this project for teaching purposes with proper attribution
- ✅ **Students** may study the codebase for learning purposes only
- ❌ **Commercial use**, reproduction, or modification is strictly prohibited without authorization
- ❌ **Production deployment** without proper security audits and licensing is prohibited

### Attribution:

When referencing this project, please cite as:

```
BIOMSS - Bank IT Operations Monitoring and Support System
Group 11, 2025
Field Trip Project - Fidelity Bank IT Department
University: [Your University Name]
```

### Disclaimer:

This system is provided "as is" for demonstration purposes. While developed with banking industry standards in mind, it is an academic project and should not be deployed in production environments without thorough security audits, penetration testing, and proper licensing.

---

## 🙏 Acknowledgments

We extend our sincere gratitude to:

- **🏦 Fidelity Bank IT Department** - For hosting our field trip, providing insights, and sharing their operational challenges
- **👨‍🏫 Our Academic Supervisors** - For guidance, mentorship, and constructive feedback throughout the project
- **🎓 Faculty Members** - For technical support and knowledge sharing
- **👥 Fellow Students** - For beta testing, feedback, and encouragement
- **🌐 Open Source Community** - For the amazing tools and frameworks (Django, PostgreSQL, etc.)
- **📚 Django Documentation Team** - For comprehensive documentation
- **💻 Stack Overflow Community** - For troubleshooting assistance

### Special Thanks

A special thank you to the **Fidelity Bank IT Operations Team** who took time from their busy schedules to:
- Give us comprehensive tours of the data center
- Explain their monitoring processes and challenges
- Share real-world scenarios and use cases
- Provide feedback on our prototype
- Validate our solution against industry standards

---

## 📞 Contact

For questions, feedback, or collaboration opportunities:

- **Email:** group11.biomss@university.edu
- **Project Repository:** https://github.com/group11/biomss
- **Documentation:** https://biomss-docs.readthedocs.io
- **Issue Tracker:** https://github.com/group11/biomss/issues

---

## 🗺️ Roadmap

### Future Enhancements

- [ ] Mobile application (iOS/Android)
- [ ] Real-time WebSocket notifications
- [ ] Advanced analytics dashboard with charts
- [ ] SMS/Email alert integration
- [ ] Mobile money integration monitoring
- [ ] Machine learning for predictive maintenance
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Export reports to PDF/Excel
- [ ] Integration with core banking systems

---

<div align="center">

**Built with ❤️ by Group 11**

**[⭐ Star this repository](https://github.com/group11/biomss)** if you found it helpful!

</div>