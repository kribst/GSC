from django.contrib import admin
from tinymce.widgets import TinyMCE
from django import forms
from .models import CustomerUser, Departement, TitreDescription, RapportIndividuel, RapportEquippe, Comptabilite, \
    Boncomtoir, Marqueting, Variant, SubComptoir, Generaux, Technique_ext, Technique_int, Technique, Marketing, \
    SubMarketing


class AdminCustomerUser(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'genre', 'email', 'pays', 'telephone', 'image',)
    search_fields = ('username', 'first_name', 'last_name', 'genre',)
    list_filter = ('genre', 'email',)
    list_per_page = 13


#

class AdminCustomerUser(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'genre', 'email', 'pays', 'telephone', 'image',)
    search_fields = ('username', 'first_name', 'last_name', 'genre',)
    list_filter = ('genre', 'email',)
    list_per_page = 13

class AdminDepartement(admin.ModelAdmin):
    list_display = ('nom', 'chef', 'get_utilisateur')
    search_fields = ('nom', 'chef__username',)  # Utiliser chef__username pour rechercher par nom d'utilisateur
    list_filter = ('nom',)
    list_per_page = 5

    def get_utilisateur(self, obj):
        return ", ".join([str(user) for user in obj.utilisateur.all()])
    get_utilisateur.short_description = 'Utilisateurs'


#
#
class AdminRapportEquippe(admin.ModelAdmin):
    list_display = ('titre', 'chef', 'superviseur', 'statut', 'afficher_travailleurs', 'date', 'afficher_departement')
    search_fields = ('titre', 'objectif', 'statut', 'departement__nom', 'chef__utilisateur', 'superviseur__utilisateur')
    list_filter = ('statut',)

    def afficher_travailleurs(self, obj):
        return ", ".join([str(travailleur) for travailleur in obj.travailleur.all()])
    afficher_travailleurs.short_description = 'Travailleurs'

    def afficher_departement(self, obj):
        return ", ".join([str(dept) for dept in obj.departement.all()])
    afficher_departement.short_description = 'Départements'


class TitreDescriptionInline(admin.TabularInline):
    model = TitreDescription
    extra = 1  # Nombre de formulaires vides à afficher

class RapportIndividuelAdmin(admin.ModelAdmin):
    inlines = [TitreDescriptionInline]




#-------------------------------------------comptabilité--------------------------------/



class ComptabiliteAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'date',
        'statut',
        'quantite_Facture_etablies',
        'quantite_Devis',
        'quantite_Demande_de_cotation',
        'quantite_Livraison_Expedition',
        'quantite_Cheques_recus',
        'quantite_Depots_cheques',
        'quantite_Bon_de_Commande',
        'quantite_Recouvrements_creances',
        'quantite_Recharge_carte_UBA',
        'quantite_Recharge_carte_ACCESS',
        'quantite_Receptions_mails',
        'quantite_Mails_envoyes',
        'quantite_Saisir_ecritures_logiciel_Sage',
        'quantite_Teledeclaration_impot',
        'quantite_Depot_de_facture_en_presentiels',
    )
    search_fields = ('objectif',)
    list_filter = ('date',)

  # Ajoute TitreComptable comme inline


#-------------------------------------------fin comptabilité--------------------------------/

#-----------------------------------------boncomptoir----------------------------------------------------/


class SubComptoirInline(admin.TabularInline):
    model = SubComptoir
    extra = 1  # Nombre de formulaires vides à afficher

class BoncomtoirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date', 'statut_qte_produit_sheet')
    search_fields = ('titre',)
    inlines = [SubComptoirInline]  # Ajout de l'inline ici

admin.site.register(Boncomtoir, BoncomtoirAdmin)

# -----------------------------------------fin boncomptoir----------------------------------------------------/





# -----------------------------------------departement technique_____________________________________________________/



# -----------------------------------------fin departement technique_____________________________________________________/
class TechniqueExtInline(admin.TabularInline):  # Utilisation de TabularInline pour un affichage en tableau
    model = Technique_ext
    extra = 1  # Nombre de formulaires vides supplémentaires
    can_delete = True


# Inline pour Technique_int (activités internes)
class TechniqueIntInline(admin.TabularInline):
    model = Technique_int
    extra = 1
    can_delete = True


# Admin principal pour Technique
@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date')  # Champs affichés dans la liste des objets
    inlines = [TechniqueExtInline, TechniqueIntInline]

# -----------------------------------------genraux____________________________________________________/


class GenerauxAdminForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Generaux
        fields = ['titre', 'date', 'description']

@admin.register(Generaux)
class GenerauxAdmin(admin.ModelAdmin):
    form = GenerauxAdminForm
    list_display = ('titre', 'date')
    search_fields = ('titre',)




class SubMarketingInline(admin.TabularInline):  # ou admin.StackedInline pour un affichage en colonne
    model = SubMarketing
    extra = 3  # Nombre de sous-formulaires vides affichés par défaut
    min_num = 1  # Minimum requis
    can_delete = True  # Permet de supprimer des sous-éléments

class MarketingAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date')  # Affichage des colonnes principales
    search_fields = ('titre',)  # Ajout d'une barre de recherche
    list_filter = ('date',)  # Ajout de filtres par date
    inlines = [SubMarketingInline]  # Associe les SubMarketing au Marketing

# -----------------------------------------fin genraux____________________________________________________/

admin.site.register(Comptabilite, ComptabiliteAdmin)
admin.site.register(RapportIndividuel, RapportIndividuelAdmin)
admin.site.register(CustomerUser, AdminCustomerUser)
admin.site.register(Departement, AdminDepartement)
admin.site.register(RapportEquippe, AdminRapportEquippe)
admin.site.register(Marketing, MarketingAdmin)
