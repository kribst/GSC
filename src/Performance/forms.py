from django.contrib.auth.forms import UserCreationForm
from .models import CustomerUser, RapportIndividuel, TitreDescription, RapportEquippe, Comptabilite, Boncomtoir, \
    Marqueting, Variant, SubComptoir, Technique, Generaux, Technique_ext, Technique_int, Marketing, SubMarketing
from django import forms
from django.forms import  inlineformset_factory
from tinymce.widgets import TinyMCE
from django.forms import modelformset_factory



class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomerUser
        fields = ['email', 'username', 'first_name', 'last_name', 'genre', 'pays', 'telephone', 'image', 'departement', 'poste']


    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
            })



class RapportIndividuelForm(forms.ModelForm):
    class Meta:
        model = RapportIndividuel
        fields = ['titre', 'departement', 'statut', 'date', 'description', 'rapport',]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            })
        }

    def __init__(self, *args, **kwargs):
        super(RapportIndividuelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
            })





class TitreDescriptionForm(forms.ModelForm):
    class Meta:
        model = TitreDescription
        fields = ['titre', 'description', 'rapport']



# rubrique rapport individuel

class RapportEquippeForm(forms.ModelForm):
    class Meta:
        model = RapportEquippe
        fields = '__all__'
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(RapportEquippeForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
            })


# fin rubrique rapport individuel



# comptabilite



class ComptabiliteForm(forms.ModelForm):
    objectif = forms.CharField(widget=TinyMCE(attrs={
        'class': 'form-control',
        'placeholder': 'Entrez les objectifs',
    }))
    class Meta:
        model = Comptabilite
        fields = '__all__'
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'quantite_Facture_etablies': forms.NumberInput(attrs={
                'placeholder': 'Entrez la quantité'  # Ajout du placeholder
            }),
            'total_Facture_etablies': forms.NumberInput(attrs={
                'placeholder': 'Entrez le total'  # Ajout du placeholder
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description_autre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ce champ est optionnel et peut rester vide',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ComptabiliteForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
            })





#-----------------------------------------------boncomptoir-----------------------------------------------------/

# Formulaire personnalisé pour SubComptoir
class SubComptoirForm(forms.ModelForm):
    class Meta:
        model = SubComptoir
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SubComptoirForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Appliquer 'form-control' à chaque champ
            })



# Formulaire pour Boncomtoir

class BoncomtoirForm(forms.ModelForm):
    class Meta:
        model = Boncomtoir
        fields = '__all__'
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(BoncomtoirForm, self).__init__(*args, **kwargs)
        boncomptoir_users = CustomerUser.objects.filter(departement='BON_COMPTOIR')
        person_fields = ['nombre_personne', 'personne_en_charge_le_sheet', 'Nombre_presonne_importer',
                         'personne_en_charge_importer', 'Nombre_presonne_flyers', 'personne_en_charge_flyers']

        for field in person_fields:
            if field in self.fields:
                self.fields[field].queryset = boncomptoir_users
                self.fields[field].widget.attrs.update({'class': 'form-control'})

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe appliquée à tous les champs
            })


class SubComptoirForm(forms.ModelForm):
    class Meta:
        model = SubComptoir
        fields = '__all__'
        widgets = {
            'activite': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'quantite_total': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'pourcentage_de_charge_individuel': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(SubComptoirForm, self).__init__(*args, **kwargs)
        boncomptoir_users = CustomerUser.objects.filter(departement='BON_COMPTOIR')
        self.fields['personne_en_charge'].queryset = boncomptoir_users
        self.fields['Nombre_de_personne'].queryset = boncomptoir_users

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
            })


SubComptoirFormSet = inlineformset_factory(
    Boncomtoir , SubComptoir,
    form=SubComptoirForm,  # Utiliser le formulaire personnalisé
    fields='__all__',
    extra=25,  # Nombre de formulaires vides supplémentaires affichés
    can_delete=True
)


#-----------------------------------------fin boncomptoir----------------------------------------------------/



class MarquetingForm(forms.ModelForm):
    class Meta:
        model = Marqueting
        fields = "__all__"
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(MarquetingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['titre', 'date','autre']:  # Exclure 'titre' et 'date'
                field.widget.attrs.update({
                    'class': 'form-control',
                    'style': 'width: 150px;',  # Appliquer uniquement aux autres champs
                })
            else:
                # Pour s'assurer que la classe 'form-control' est bien présente sur tous les champs
                field.widget.attrs.update({
                    'class': 'form-control',
                })



class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        exclude = ['Marqueting']
        # fields = ['autre_un','objectifs','quantites','Total','acteur','Activites','Entreprises','Particuliers','Services','Consommables','materiel_informatique','Formation','Statut','Difficultes_rencontrees','echec_de_l_objectif','Actions_correctives']


    def __init__(self, *args, **kwargs):
        super(VariantForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
                'style': 'width: 150px;',
            })
# Créer un inline formset pour Variant
VariantFormSet = inlineformset_factory(Marqueting, Variant, form=VariantForm, extra=5, can_delete=True)


# -----------------------------------------departement technique_____________________________________________________/




# -----------------------------------------genraux____________________________________________________/

class GenerauxForm(forms.ModelForm):
    class Meta:
        model = Generaux
        fields = ['titre', 'date', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }


    def __init__(self, *args, **kwargs):
        super(GenerauxForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Classe à appliquer à tous les champs
            })


# -----------------------------------------genraux____________________________________________________/



# -----------------------------------------technique____________________________________________________/
class SubTechnique_extForm(forms.ModelForm):
    class Meta:
        model = Technique_ext
        fields = '__all__'  # ✅ Inclure tous les champs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Récupérer uniquement les utilisateurs appartenant au département TECHNIQUE
        self.fields['ext_intervenant'].queryset = CustomerUser.objects.filter(departement='TECHNIQUE')


class SubTechnique_intForm(forms.ModelForm):
    class Meta:
        model = Technique_int
        fields = '__all__'  # ✅ Inclure tous les champs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Récupérer uniquement les utilisateurs appartenant au département TECHNIQUE
        self.fields['int_intervenant'].queryset = CustomerUser.objects.filter(departement='TECHNIQUE')


class TechniqueForm(forms.ModelForm):
    class Meta:
        model = Technique
        fields = '__all__'  # ✅ Inclure tous les champs
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez un titre au rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'autre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ce champ est optionnel et peut rester vide',
            }),
            'Laptops_Entree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer un nombre',
            }),
            'Laptop_en_Attente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer un nombre',
            }),
            'Facturation_Paiement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'nombres_interventions_externe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer un nombre',
            }),
            'Intervention_en_attente_externe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer un nombre',
            }),
            'Facturation_Paiement_externe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'liste': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'champ_un': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'champ_deux': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'champ_trois': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
            'champ_quatre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrer du texte',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs.setdefault('class', 'form-control')
                field.widget.attrs['style'] = 'width: 200px;'

        # Récupérer uniquement les utilisateurs appartenant au département TECHNIQUE
        technique_users = CustomerUser.objects.filter(departement='TECHNIQUE')
        self.fields['intervenant_externe'].queryset = technique_users
        self.fields['intervenant_interne'].queryset = technique_users


SubTechniqueExtFormSet = inlineformset_factory(
    Technique, Technique_ext,
    form=SubTechnique_extForm,
    fields='__all__',
    extra=30,  # Ajuster selon le besoin
    can_delete=True
)

SubTechniqueIntFormSet = inlineformset_factory(
    Technique, Technique_int,
    form=SubTechnique_intForm,
    fields='__all__',
    extra=30,  # Ajuster selon le besoin
    can_delete=True
)

#-----------------------------------------fin technique----------------------------------------------------/


class MarketingForm(forms.ModelForm):
    class Meta:
        model = Marketing
        fields = '__all__'
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre du rapport',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'autre': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super(MarketingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ["date", "titre", "autre"]:  # Exclure "date" et "titre"
                field.widget.attrs.update({
                    'class': 'form-control',
                    'style': 'width: 150px; text-align: center;',
                })

# Formulaire pour SubMarketing
class SubMarketingForm(forms.ModelForm):
    class Meta:
        model = SubMarketing
        fields = '__all__'
        widgets = {
            'indicateur': forms.TextInput(attrs={'class': 'form-control'}),
            'objectifs': forms.TextInput(attrs={'class': 'form-control'}),
            'quantites': forms.NumberInput(attrs={'class': 'form-control'}),
            'Total': forms.NumberInput(attrs={'class': 'form-control'}),
            'acteur': forms.TextInput(attrs={'class': 'form-control'}),
            'Activites': forms.TextInput(attrs={'class': 'form-control'}),
            'Entreprises': forms.TextInput(attrs={'class': 'form-control'}),
            'Particuliers': forms.TextInput(attrs={'class': 'form-control'}),
            'Services': forms.TextInput(attrs={'class': 'form-control'}),
            'Consommables': forms.TextInput(attrs={'class': 'form-control'}),
            'materiel_informatique': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.TextInput(attrs={'class': 'form-control'}),
            'Statut': forms.TextInput(attrs={'class': 'form-control'}),
            'Difficultes_rencontrees': forms.TextInput(attrs={'class': 'form-control'}),
            'Raisons_e_l_echec_de_l_objectif': forms.TextInput(attrs={'class': 'form-control'}),
            'Actions_correctives': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SubMarketingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs['style'] = 'width: 150px;'

# Formset pour gérer les SubMarketing liés à un Marketing
SubMarketingFormSet = inlineformset_factory(
    Marketing, SubMarketing,
    form=SubMarketingForm,
    fields='__all__',
    extra=5,  # Nombre de formulaires vides supplémentaires affichés
    can_delete=True
)
