from datetime import timedelta
from rest_framework import generics
import csv, io

from api.permissions import *
from .models import *
from .serializers import *

from django.db import transaction as db_transaction

from django.db.models.functions import TruncMonth

import pandas as pd

from rest_framework.decorators import api_view, permission_classes
from django.utils.crypto import get_random_string

from django.http import HttpRequest
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from rest_framework.pagination import PageNumberPagination

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from django.db.models import Q, Avg, Sum, Count
from django.core.files.storage import default_storage
from django.db.models import Sum, Count, Q, FloatField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import calendar

@api_view(["GET"])
def dashboard_stats(request):
    # Existing stats
    total_soldes = Compte.objects.aggregate(total=Sum("solde"))["total"] or 0
    total_entrees = Transaction.objects.filter(type__is_debiteur=False).aggregate(total=Sum("montant"))["total"] or 0
    total_sorties = Transaction.objects.filter(type__is_debiteur=True).aggregate(total=Sum("montant"))["total"] or 0
    etudiants_negatifs = Etudiant.objects.filter(solde__lt=0).count()

    # === NEW USEFUL STATS ===

    # 1. Total number of students
    total_etudiants = Etudiant.objects.count()

    # 2. Number of students with positive balance
    etudiants_positifs = Etudiant.objects.filter(solde__gt=0).count()

    # 3. Number of students with zero balance
    etudiants_zero = Etudiant.objects.filter(solde=0).count()

    # 4. Average student balance
    avg_solde = Etudiant.objects.aggregate(avg=Coalesce(models.Avg('solde'), 0.0))['avg']

    # 5. Total student debt (sum of negative balances)
    total_dette = Etudiant.objects.filter(solde__lt=0).aggregate(
        total=Coalesce(Sum('solde'), 0.0)
    )['total'] or 0

    # 6. Total student credit (sum of positive balances)
    total_credit = Etudiant.objects.filter(solde__gt=0).aggregate(
        total=Coalesce(Sum('solde'), 0.0)
    )['total'] or 0

    # 7. Number of transactions today
    today = datetime.today().date()
    transactions_aujourdhui = Transaction.objects.filter(date=today).count()

    # 8. Total entries today
    entrees_aujourdhui = Transaction.objects.filter(
        date=today, type__is_debiteur=False
    ).aggregate(total=Sum('montant'))['total'] or 0

    # 9. Total exits today
    sorties_aujourdhui = Transaction.objects.filter(
        date=today, type__is_debiteur=True
    ).aggregate(total=Sum('montant'))['total'] or 0

    # 10. Number of students per class (top 5 largest classes)
    classes_stats = list(Classe.objects.annotate(
        nb_etudiants=Count('etudiants')
    ).values('nom_classe', 'nb_etudiants').order_by('-nb_etudiants')[:5])

    # 11. Most used transaction types (top 5)
    top_transaction_types = list(TypeTransaction.objects.annotate(
        nb_transactions=Count('transactions'),
        total_montant=Sum('transactions__montant')
    ).values('nom_type', 'nb_transactions', 'total_montant', 'is_debiteur')
      .order_by('-nb_transactions')[:5])

    # 12. Monthly entries vs exits (current month)
    current_month = today.month
    current_year = today.year
    
    monthly_entrees = Transaction.objects.filter(
        date__month=current_month,
        date__year=current_year,
        type__is_debiteur=False
    ).aggregate(total=Sum('montant'))['total'] or 0

    monthly_sorties = Transaction.objects.filter(
        date__month=current_month,
        date__year=current_year,
        type__is_debiteur=True
    ).aggregate(total=Sum('montant'))['total'] or 0

    # 13. Number of new students this month
    new_students_this_month = Etudiant.objects.filter(
        transactions__date__month=current_month,
        transactions__date__year=current_year
    ).distinct().count()

    return Response({
        # Existing
        "total_soldes": total_soldes,
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "etudiants_negatifs": etudiants_negatifs,

        # New ones
        "total_etudiants": total_etudiants,
        "etudiants_positifs": etudiants_positifs,
        "etudiants_zero": etudiants_zero,
        "etudiants_negatifs": etudiants_negatifs,
        "moyenne_solde_etudiant": round(avg_solde, 2),
        "total_dette_etudiants": abs(total_dette),  # positive value
        "total_credit_etudiants": total_credit,

        "transactions_aujourdhui": transactions_aujourdhui,
        "entrees_aujourdhui": entrees_aujourdhui,
        "sorties_aujourdhui": sorties_aujourdhui,

        "entrees_ce_mois": monthly_entrees,
        "sorties_ce_mois": monthly_sorties,

        "nouveaux_etudiants_ce_mois": new_students_this_month,

        "top_classes": classes_stats,
        "top_types_transactions": top_transaction_types,
    })

class ClasseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer


class ClasseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer




##### TYPE TRANSACTION
class TypeTransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = TypeTransaction.objects.all()
    serializer_class = TypeTransactionSerializer


class TypeTransactionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TypeTransaction.objects.all()
    serializer_class = TypeTransactionSerializer





##### COMPTE
class CompteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Compte.objects.all()
    serializer_class = CompteSerializer


class CompteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Compte.objects.all()
    serializer_class = CompteSerializer


##### ETUDIANT
class EtudiantListCreateAPIView(generics.ListCreateAPIView):
    queryset = Etudiant.objects.select_related('classe').all()
    serializer_class = EtudiantSerializer


class EtudiantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Etudiant.objects.select_related('classe').all()
    serializer_class = EtudiantSerializer


class EtudiantCustomListAPIView(generics.ListAPIView):
    queryset = Etudiant.objects.select_related('classe').all()
    serializer_class = EtudiantCustomSerializer



class TransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Transaction.objects.select_related('compte', 'type', 'etudiant').all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        with db_transaction.atomic():
            instance = serializer.save()  

            compte = instance.compte
            if instance.type.is_debiteur:
                compte.solde -= instance.montant
            else:
                compte.solde += instance.montant
            compte.save()

            if instance.etudiant:
                etudiant = instance.etudiant
                etudiant.solde += instance.montant
                etudiant.save()


class TransactionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.select_related('compte', 'type', 'etudiant').all()
    serializer_class = TransactionSerializer


class TransactionCustomListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.select_related('compte', 'type', 'etudiant').all()
    serializer_class = TransactionCustomSerializer





class ImportEtudiantsAPIView(APIView):

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "Aucun fichier fourni"}, status=status.HTTP_400_BAD_REQUEST)

        # Sauvegarder temporairement
        path = default_storage.save("temp/" + file.name, file)

        try:
            # Détecter extension
            if file.name.endswith(".csv"):
                df = pd.read_csv(path, sep=None, engine='python')   # auto detect ; or ,
            elif file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(path)
            else:
                return Response({"error": "Format non supporté"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Impossible de lire le fichier : {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Normaliser colonnes
        df.columns = df.columns.str.strip().str.lower()

        # Colonnes attendues
        required_cols = ["prenom", "nom", "naissance", "contact", "classe"]

        for col in required_cols:
            if col not in df.columns:
                return Response({"error": f"Colonne manquante : {col}"}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        errors = []

        for index, row in df.iterrows():
            try:
                classe_name = str(row["classe"]).strip()
                classe = Classe.objects.filter(nom_classe__iexact=classe_name).first()

                if not classe:
                    errors.append(f"Ligne {index+1}: Classe inconnue ({classe_name})")
                    continue

                Etudiant.objects.create(
                    prenom=row["prenom"],
                    nom=row["nom"],
                    date_naissance=pd.to_datetime(row["naissance"]).date(),
                    contact=str(row["contact"]),
                    classe=classe,
                    solde=0
                )
                created += 1
            
            except Exception as e:
                errors.append(f"Ligne {index+1} : {str(e)}")

        return Response({
            "created": created,
            "errors": errors,
        }, status=status.HTTP_201_CREATED)



class SeConnecter(TokenObtainPairView):
    serializer_class = ConnexionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telephone = serializer.validated_data['telephone']
        mot_de_passe = serializer.validated_data['mot_de_passe']

        utilisateur = Utilisateur.objects.filter(telephone=telephone).first()

        if utilisateur:

            utilisateur = authenticate(request, telephone=telephone, password=mot_de_passe)
            if utilisateur :
                
                refresh = RefreshToken.for_user(utilisateur)
                
                utilisateur = UtilisateurSerializer(utilisateur).data
                data = {
                    'token': str(refresh.access_token),
                    'utilisateur' : utilisateur,
                }
                
                return Response(data, status=status.HTTP_200_OK)
            
            else :
                return Response( status=401)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Utilisateur_profil(request):
    Utilisateur = request.user
    try:
        Utilisateur = UtilisateurSerializer(Utilisateur)
        return JsonResponse(Utilisateur.data)
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": f"Failed to load Utilisateurs profile {e}"
        })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_informations(request):
    user = request.user
    serializer = UtilisateurSerializer(user, data=request.data, partial=True)


    if serializer.is_valid() :
        serializer.save()
        return Response(serializer.data)
    return Response({"bad request"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_mot_de_passe(request):
    Utilisateur = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        ancien = data.get('ancien', {})
        nouveau = data.get('nouveau', {})

        if check_password(ancien, Utilisateur.password):
            Utilisateur.password = make_password(nouveau)
            Utilisateur.save()

            return Response({"message" : "Mot de passe modifié avec succés"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Mot de passe incorrecte"}, status=400)

    except Exception as e:
        return Response({"message" : "Une erreur est survenue"}, status=500)


