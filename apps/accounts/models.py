import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.permissions import ROLE_CHOICES, user_has_perm
from apps.core.storage import private_storage
from apps.core.validators import validate_image


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, matricule, password, **extra):
        if not matricule:
            raise ValueError("Le matricule est obligatoire.")
        matricule = matricule.strip().upper()
        if extra.get("email"):
            extra["email"] = self.normalize_email(extra["email"])
        else:
            extra["email"] = None
        user = self.model(matricule=matricule, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, matricule, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(matricule, password, **extra)

    def create_superuser(self, matricule, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("account_status", User.ACTIVE)
        extra.setdefault("email_verified", True)
        user = self._create(matricule, password, **extra)
        from .models import Role  # noqa
        role, _ = Role.objects.get_or_create(code="super_admin", defaults={"name": "Super administrateur"})
        user.roles.add(role)
        return user


class Role(models.Model):
    code = models.CharField(max_length=30, unique=True, choices=ROLE_CHOICES)
    name = models.CharField(max_length=80)

    class Meta:
        verbose_name = "rôle"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    PENDING, ACTIVE, REFUSED, SUSPENDED, DISABLED = "pending", "active", "refused", "suspended", "disabled"
    STATUS_CHOICES = [
        (PENDING, "En attente de validation"),
        (ACTIVE, "Actif"),
        (REFUSED, "Refusé"),
        (SUSPENDED, "Suspendu"),
        (DISABLED, "Désactivé"),
    ]
    SEX_CHOICES = [("F", "Féminin"), ("M", "Masculin")]

    username = None
    matricule = models.CharField("matricule", max_length=30, unique=True)
    email = models.EmailField("adresse e-mail", null=True, blank=True, unique=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone = models.CharField("téléphone", max_length=20)
    sex = models.CharField("sexe", max_length=1, choices=SEX_CHOICES, blank=True)
    photo = models.ImageField("photo d'identité", upload_to="photos/", storage=private_storage,
                              blank=True, validators=[validate_image])
    account_status = models.CharField("statut du compte", max_length=12, choices=STATUS_CHOICES, default=PENDING)
    email_verified = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, blank=True, related_name="users")

    USERNAME_FIELD = "matricule"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    class Meta:
        verbose_name = "utilisateur"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.matricule

    @property
    def full_name(self):
        return f"{self.last_name.upper()} {self.first_name}".strip()

    @property
    def short_name(self):
        return f"{self.first_name} {self.last_name[:1]}.".strip()

    @property
    def masked_matricule(self):
        m = self.matricule
        return "*" * max(len(m) - 3, 0) + m[-3:]

    @property
    def is_active_member(self):
        return self.is_active and self.account_status == self.ACTIVE

    @property
    def is_staff_member(self):
        if not self.pk:
            return False
        return self.roles.exists()

    def has_role(self, code):
        return self.roles.filter(code=code).exists()

    def can(self, code):
        return user_has_perm(self, code)

    def set_account_status(self, status):
        self.account_status = status
        self.is_active = status != self.DISABLED
        self.save(update_fields=["account_status", "is_active"])


class MemberProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    member_number = models.CharField("numéro de membre", max_length=20, unique=True)
    joined_year = models.PositiveIntegerField("année d'adhésion")

    class Meta:
        verbose_name = "profil membre"

    def __str__(self):
        return self.member_number


from apps.core.images import connect_optimizer  # noqa: E402

connect_optimizer(User, {"photo": 900})
