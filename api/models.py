from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


class Classe(models.Model):
    nom_classe = models.CharField(max_length=50)

    def __str__(self):
        return str(self.nom_classe)


class TypeTransaction(models.Model):
    nom_type = models.CharField(max_length=50)
    is_debiteur = models.BooleanField()   # True = decrease, False = increase

    def __str__(self):
        return str(self.nom_type)


class Compte(models.Model):
    nom_compte = models.CharField(max_length=50)
    solde = models.FloatField(default=0)   # corrected from BooleanField

    def __str__(self):
        return str(self.nom_compte)


class Etudiant(models.Model):
    matricule = models.CharField(max_length=50, unique=True, blank=True)
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    date_naissance = models.DateField()
    solde = models.FloatField(default=0)
    contact = models.CharField(max_length=50)
    classe = models.ForeignKey(Classe, related_name='etudiants', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Générer le matricule seulement à la création
        if not self.matricule:
            last_student = Etudiant.objects.order_by('-id').first()
            if last_student and last_student.matricule.startswith("STU"):
                # Extraire le numéro
                last_number = int(last_student.matricule[3:])
            else:
                last_number = 0

            new_number = last_number + 1
            self.matricule = f"STU{new_number:04d}"  # format STU0001

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricule} - {self.prenom} {self.nom}"


class Transaction(models.Model):
    montant = models.FloatField()
    date = models.DateField(auto_now_add=True)   # ➜ Toujours la date actuelle
    note = models.CharField(max_length=100, blank=True, null=True)
    compte = models.ForeignKey(Compte, related_name='transactions', on_delete=models.CASCADE)
    type = models.ForeignKey(TypeTransaction, related_name='transactions', on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, related_name='transactions', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Utilisateur(AbstractUser):
    telephone = models.CharField(max_length=8, unique=True)

    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    # def save(self, *args, **kwargs):
    #     # hash password only during first creation
    #     if not self.pk and self.password:
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)