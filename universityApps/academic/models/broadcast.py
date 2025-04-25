import uuid
import hashlib
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class LectureBroadcast(models.Model):
    class BroadcastStatus(models.TextChoices):
        SCHEDULED  = 'scheduled', _('Scheduled')
        LIVE = 'live', _('Live')
        ENDED = 'ended', _('Ended')
        CANCELED = 'canceled', _('Canceled')

    schedule = models.OneToOneField(
        'academic.GroupSchedule',
        on_delete=models.CASCADE,
        related_name='broadcast',
        verbose_name=_("Group Schedule")
    )

    stream_key = models.CharField(
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        verbose_name=_("Stream Key")
    )

    status = models.CharField(
        max_length=10,
        choices=BroadcastStatus.choices,
        default=BroadcastStatus.SCHEDULED,
        verbose_name=_("Status")
    )

    start_time = models.DateTimeField(blank=True, null=True, verbose_name=_("Start Time"))
    end_time = models.DateTimeField(blank=True, null=True, verbose_name=_("End Time"))
    viewer_count = models.PositiveIntegerField(default=0, verbose_name=_("Viewer Count"))
    record_path = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Recording Path"))

    playback_token = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("Playback Token"))
    token_expiry = models.DateTimeField(blank=True, null=True, verbose_name=_("Token Expiry"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Lecture Broadcast")
        verbose_name_plural = _("Lecture Broadcasts")
        indexes = [
            models.Index(fields=['status'], name='broadcast_status_idx'),
        ]

    def __str__(self):
        return f"{self.schedule} - {self.status.upper()}"

    # 🔗 RTMP URL for OBS (input)
    def get_rtmp_url(self):
        return f"rtmp://localhost:1935/live/{self.stream_key}"

    # 📺 HLS playback URL for frontend (output)
    def get_hls_url(self):
        return f"http://localhost:8080/hls/{self.stream_key}.m3u8"

    # 🔐 Generate secure playback token for students
    def generate_token(self):
        seed = f"{self.stream_key}{timezone.now().timestamp()}"
        self.playback_token = hashlib.sha256(seed.encode()).hexdigest()
        self.token_expiry = timezone.now() + timedelta(hours=2)
        self.save()

    # ✅ Verify student token is still valid
    def is_token_valid(self, token):
        return (
            self.playback_token == token and
            self.token_expiry and
            self.token_expiry > timezone.now()
        )

    # 🔍 Returns whether the stream is supposed to be live now
    def is_now_live(self):
        return self.status == self.BroadcastStatus.LIVE

    def active_viewer_count(self):
        return self.attendance_logs.filter(leave_time__isnull=True).count()

class Classroom(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Classroom Name"),
        help_text=_("e.g., Room A101, Virtual Lab 3")
    )
    building = models.CharField(
        max_length=100,
        verbose_name=_("Building"),
        blank=True,
        null=True,
        help_text=_("e.g., Main Campus, Online, Engineering Block")
    )
    floor = models.CharField(
        max_length=10,
        verbose_name=_("Floor"),
        blank=True,
        null=True,
        help_text=_("e.g., 1st, Ground, Online")
    )
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum Capacity"),
        help_text=_("Maximum number of students allowed")
    )
    is_lab = models.BooleanField(
        default=False,
        verbose_name=_("Is Lab"),
        help_text=_("Mark this if the room is used for lab sessions")
    )
    is_virtual = models.BooleanField(
        default=False,
        verbose_name=_("Is Virtual Room"),
        help_text=_("Use for online/streaming spaces")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck to disable scheduling in this room")
    )

    class Meta:
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = ['building', 'name']
        indexes = [
            models.Index(fields=['building', 'floor'], name='idx_classroom_location'),
            models.Index(fields=['is_lab'], name='idx_classroom_is_lab'),
            models.Index(fields=['is_virtual'], name='idx_classroom_virtual'),
        ]

    def __str__(self):
        return f"{self.name} ({'Virtual' if self.is_virtual else self.building})"

    def full_location(self):
        return f"{self.building or ''} - Floor {self.floor or '?'}"

class LiveAttendanceLog(models.Model):
    broadcast = models.ForeignKey('academic.LectureBroadcast', on_delete=models.CASCADE, related_name='attendance_logs')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='live_attendance')
    join_time = models.DateTimeField(auto_now_add=True)
    leave_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("Live Attendance Log")
        verbose_name_plural = _("Live Attendance Logs")
        unique_together = ['broadcast', 'student']

    def __str__(self):
        return f"{self.student.user.get_full_name()} @ {self.broadcast.schedule}"
