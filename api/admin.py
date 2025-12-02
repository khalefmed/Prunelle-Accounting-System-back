from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import *

# Register your models here.



from django.contrib import admin
from .models import *

class ClasseAdmin(admin.ModelAdmin):
    list_display = ("id", "nom_classe")

class TypeTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "nom_type", "is_debiteur")

class CompteAdmin(admin.ModelAdmin):
    list_display = ("id", "nom_compte", "solde")

class EtudiantAdmin(admin.ModelAdmin):
    list_display = (
        "id", "matricule", "prenom", "nom",
        "date_naissance", "solde", "contact", "classe"
    )
    list_filter = ("classe",)
    search_fields = ("matricule", "prenom", "nom")

class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "montant", "date", "note",
        "compte", "type", "etudiant"
    )
    list_filter = ("type", "compte", "date")
    search_fields = ("note",)

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = (
        "username", "telephone",
        "is_staff", "is_active", "date_joined"
    )
    search_fields = ("username", "telephone")
    list_filter = ("is_staff", "is_active")



admin.site.site_header = "Les prunelles"

admin.site.register(Classe, ClasseAdmin)
admin.site.register(TypeTransaction, TypeTransactionAdmin)
admin.site.register(Compte, CompteAdmin)
admin.site.register(Etudiant, EtudiantAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)

