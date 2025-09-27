from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_TYPES = [
        ('admin', 'System Administrator'),
        ('examiner', 'Examiner'),
        ('committee', 'Evaluation Committee Member'),
        ('examinee', 'Examinee/Candidate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='committee')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    is_active_evaluator = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_user_type_display()})"

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_examiner(self):
        return self.user_type == 'examiner'

    @property
    def is_committee_member(self):
        return self.user_type == 'committee'

    @property
    def is_examinee(self):
        return self.user_type == 'examinee'

    @property
    def can_manage_candidates(self):
        return self.user_type == 'admin'

    @property
    def can_manage_evaluation_sessions(self):
        return self.user_type in ['admin', 'examiner']

    @property
    def can_control_sessions(self):
        return self.user_type in ['admin', 'examiner']

    @property
    def can_evaluate_candidates(self):
        return self.user_type in ['admin', 'committee'] and self.is_active_evaluator

    @property
    def can_view_evaluation_queue(self):
        return self.user_type in ['admin', 'committee'] and self.is_active_evaluator

    @property
    def can_generate_reports(self):
        return self.user_type == 'admin'

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['user__first_name', 'user__last_name']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
