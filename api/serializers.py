from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

Utilisateur = get_user_model()


class ConnexionSerializer(serializers.Serializer):
    telephone = serializers.CharField()
    mot_de_passe = serializers.CharField(write_only=True)


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = '__all__'


class TypeTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTransaction
        fields = '__all__'


class CompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = '__all__'


class EtudiantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etudiant
        fields = '__all__'


class EtudiantCustomSerializer(serializers.ModelSerializer):
    classe = ClasseSerializer()

    class Meta:
        model = Etudiant
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionCustomSerializer(serializers.ModelSerializer):
    compte = CompteSerializer()
    type = TypeTransactionSerializer()
    etudiant = EtudiantSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'

class UtilisateurCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }



class EtudiantCSVSerializer(serializers.Serializer):
    prenom = serializers.CharField(max_length=50)
    nom = serializers.CharField(max_length=50)
    date_naissance = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    contact = serializers.CharField(max_length=50)
    classe = serializers.CharField(max_length=50)  # nom de la classe