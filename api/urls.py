
from django.urls import path
from .views import *


urlpatterns = [


    path("dashboard/stats/", dashboard_stats),

    # Classe
    path('classes/', ClasseListCreateAPIView.as_view()),
    path('classes/<int:pk>/', ClasseRetrieveUpdateDestroyAPIView.as_view()),

    # Type Transaction
    path('types/', TypeTransactionListCreateAPIView.as_view()),
    path('types/<int:pk>/', TypeTransactionRetrieveUpdateDestroyAPIView.as_view()),

    # Compte
    path('comptes/', CompteListCreateAPIView.as_view()),
    path('comptes/<int:pk>/', CompteRetrieveUpdateDestroyAPIView.as_view()),

    # Etudiant
    path('etudiants/', EtudiantListCreateAPIView.as_view()),
    path('etudiants/<int:pk>/', EtudiantRetrieveUpdateDestroyAPIView.as_view()),
    path('etudiants/custom/', EtudiantCustomListAPIView.as_view()),
    path("etudiants/import/", ImportEtudiantsAPIView.as_view()),

    # Transaction
    path('transactions/', TransactionListCreateAPIView.as_view()),
    path('transactions/<int:pk>/', TransactionRetrieveUpdateDestroyAPIView.as_view()),
    path('transactions/custom/', TransactionCustomListAPIView.as_view()),

    path('connexion/', SeConnecter.as_view(), name='connexion'),
    path('profil/', Utilisateur_profil, name='profile-view'),
    path('modifier_informations/', modifier_informations, name='modifier-informations'),
    path('modifier_mot_de_passe/', modifier_mot_de_passe, name='modifier-mot-passe'),
]
