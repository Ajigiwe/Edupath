import uuid
from django.db import models
from django.conf import settings

class Ownership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
     return self.name


class InstitutionType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    typename = models.CharField(max_length=100)
    ownership = models.ForeignKey(Ownership, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.typename

class Level(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    levelsname = models.CharField(max_length=100)  # Degree, Diploma, etc
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.levelsname

class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institutionname = models.CharField(max_length=100)
    institutiontype = models.ForeignKey(InstitutionType, on_delete=models.CASCADE)

    level = models.ForeignKey(Level, on_delete=models.CASCADE)  # ✅ ADD THIS

    location = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institutionname

class SHSStream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    strengths = models.TextField(blank=True, help_text="Comma-separated strengths profile")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    CATEGORY_CHOICES = [
        ('CORE', 'Core'),
        ('ELECTIVE', 'Elective'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='ELECTIVE')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SHSStreamSubject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stream = models.ForeignKey(SHSStream, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_core = models.BooleanField(default=True)

    class Meta:
        unique_together = ['stream', 'subject']

    def __str__(self):
        return f"{self.stream.name} → {self.subject.name}"


class ProgramPrerequisite(models.Model):
    LEVEL_CHOICES = [
        ('REQ', 'Required'),
        ('PRE', 'Preferred'),
        ('NIC', 'Nice to have'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey('Program', on_delete=models.CASCADE, related_name='prerequisites')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    requirement_level = models.CharField(max_length=3, choices=LEVEL_CHOICES, default='REQ')
    min_grade = models.IntegerField(default=6, help_text="WAEC scale: 1=A1 … 6=C6 (lower is better)")

    class Meta:
        unique_together = ['program', 'subject']

    def __str__(self):
        return f"{self.program.programname} needs {self.subject.name} ({self.get_requirement_level_display()})"


class ProgramAdmissionTier(models.Model):
    GENDER_CHOICES = [
        ('ANY', 'Any'),
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_details = models.ForeignKey('ProgramDetails', on_delete=models.CASCADE, related_name='admission_tiers')
    tier_name = models.CharField(max_length=50, default='Regular')
    cutoff_aggregate = models.IntegerField(help_text="Max WASSCE aggregate allowed")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='ANY')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['program_details', 'tier_name', 'gender']

    def __str__(self):
        return f"{self.program_details} — {self.tier_name} ({self.get_gender_display()}, ≤{self.cutoff_aggregate})"


class AlternativePathway(models.Model):
    PATHWAY_CHOICES = [
        ('MATURE', 'Mature Entry (25+)'),
        ('HND_DIPLOMA', 'HND / Diploma Holders'),
        ('ACCESS', 'Access Course'),
        ('INTERNATIONAL', 'International Credentials'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_details = models.ForeignKey('ProgramDetails', on_delete=models.CASCADE, related_name='alternative_pathways')
    pathway_type = models.CharField(max_length=20, choices=PATHWAY_CHOICES)
    description = models.TextField(help_text="Requirements and process")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.program_details} — {self.get_pathway_type_display()}"


class Interest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # Science, Business, Arts, Technology
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    programname = models.CharField(max_length=100)
    interests = models.ManyToManyField(Interest, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.programname

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coursename = models.CharField(max_length=100)

    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    interests = models.ManyToManyField(Interest, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.coursename

class SchoolLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level_number = models.IntegerField()  # 100, 200, 300
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.level_number)
    


class ProgramDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    cutoff_point = models.IntegerField()

    is_active = models.BooleanField(default=True)  # soft delete support

    # ✅ NEW FIELDS
    description = models.TextField(null=True, blank=True)
    career_path = models.TextField(null=True, blank=True)

    job_score = models.IntegerField(null=True, blank=True)  # e.g. 80, 60, 90

    JOB_CHANCES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    job_chances = models.CharField(
        max_length=10,
        choices=JOB_CHANCES,
        default='MEDIUM'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['program', 'institution'],
                name='unique_program_institution'
            )
        ]

    def __str__(self):
        return f"{self.program} - {self.institution} ({self.cutoff_point})"


# ================= THEORY QUESTIONS =================
class TheoryQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)  # ✅ ADD THIS
    school_level = models.ForeignKey(SchoolLevel, on_delete=models.CASCADE, null=True, blank=True)
    
    question = models.TextField()
    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]


# ================= MCQ QUESTIONS =================
class MCQQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    school_level = models.ForeignKey(SchoolLevel, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]


# ================= MCQ OPTIONS =================
class MCQOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    question = models.ForeignKey(MCQQuestion, related_name="options", on_delete=models.CASCADE)

    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# ── Subscription / Pricing ──

class PlanFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    codename = models.CharField(max_length=100, unique=True, help_text="Used in code for feature gating (e.g. 'past_questions')")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly price in GHS")
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Yearly price in GHS")
    features = models.ManyToManyField(PlanFeature, through='PlanFeatureThrough', blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    badge_label = models.CharField(max_length=50, blank=True, help_text="e.g. 'Most Popular', 'Best Value'")
    color = models.CharField(max_length=7, default='#1e3a5f', help_text="Hex color for plan branding (e.g. #1e3a5f)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class PlanFeatureThrough(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    feature = models.ForeignKey(PlanFeature, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['plan', 'feature']

    def __str__(self):
        return f"{self.plan.name} → {self.feature.name}"


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('TRIAL', 'Trial'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='TRIAL')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.plan.name if self.plan else 'None'} ({self.status})"


class Payment(models.Model):
    PROVIDER_CHOICES = [
        ('PAYSTACK', 'Paystack'),
        ('MANUAL', 'Manual Transfer'),
        ('FREE', 'Free Grant'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default='MANUAL')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — GHS{self.amount} ({self.status})"


class SiteSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paystack_public_key = models.CharField(max_length=255, blank=True, help_text="Live Paystack public key")
    paystack_secret_key = models.CharField(max_length=255, blank=True, help_text="Live Paystack secret key (keep secret)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk='00000000-0000-0000-0000-000000000001')
        return obj


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('SEARCH', 'Path Search'),
        ('VIEW_PROGRAM', 'Program View'),
        ('VIEW_PASTQ', 'Past Question View'),
        ('PLAN_CHANGE', 'Plan Change'),
        ('LOGIN', 'Login'),
        ('SIGNUP', 'Sign Up'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='OTHER')
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'

    def __str__(self):
        return f"{self.user.username} — {self.get_activity_type_display()} ({self.created_at:%Y-%m-%d})"