from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
import pypandoc
import pdfkit
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
import locale
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from .forms import UserRegistrationForm, RapportIndividuelForm, RapportEquippeForm, ComptabiliteForm, \
    MarquetingForm, BoncomtoirForm, GenerauxForm, SubComptoirFormSet, VariantFormSet, TechniqueForm, \
    SubTechniqueExtFormSet, SubTechniqueIntFormSet, MarketingForm, SubMarketingFormSet
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import RapportIndividuel, RapportEquippe, Comptabilite, Boncomtoir, Marqueting, Variant, Technique, \
    Generaux, Marketing, SubMarketing

from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from datetime import timedelta
from babel.dates import format_date, format_datetime
from datetime import datetime
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
CustomerUser = get_user_model()




def is_admin(user):
    return user.is_staff or user.is_superuser



#----------------------------------rapports individuels-------------------------------------------------------/


# Liste des rapports individuels
@login_required
def rapport_listindividuel(request):
    rapports = RapportIndividuel.objects.all().order_by('-date')
    # Créer un objet Paginator
    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'fonctionnality/rapport_listindividuel.html', context)


# Créer un rapport
@login_required
def rapport_createindividuel(request):
    if request.method == 'POST':
        form = RapportIndividuelForm(request.POST)
        if form.is_valid():
            rapport = form.save(commit=False)  # Ne pas encore enregistrer
            rapport.auteur = request.user  # Assigner l'utilisateur connecté
            rapport.save()  # Maintenant, on sauvegarde
            return redirect('rapport_detail_individuel', pk=rapport.pk)  # Redirection vers le détail du rapport
    else:
        form = RapportIndividuelForm()

    return render(request, 'fonctionnality/rapport_createindividuel.html', {'form': form})




@login_required
def rapport_updateindividuel(request, pk):
    rapport = get_object_or_404(RapportIndividuel, pk=pk)

    # Vérifier si l'utilisateur est l'auteur ou un administrateur
    if request.user != rapport.auteur and not request.user.is_superuser:
        return render(request, 'fonctionnality/permission_denied.html', {"rapport": rapport})  # Page de refus d'accès

    if request.method == 'POST':
        form = RapportIndividuelForm(request.POST, instance=rapport)
        if form.is_valid():
            form.save()
            return redirect('rapport_detail_individuel', pk=rapport.pk)
    else:
        form = RapportIndividuelForm(instance=rapport)

    return render(request, 'fonctionnality/rapport_updateindividuel.html', {'form': form, 'rapport': rapport})






@login_required
def rapport_deleteindividuel(request, pk):
    rapport = get_object_or_404(RapportIndividuel, pk=pk)

    # Vérifier si l'utilisateur est l'auteur ou un administrateur
    if request.user != rapport.auteur and not request.user.is_superuser:
        return render(request, 'fonctionnality/permission_denied_delete.html', {"rapport": rapport})  # Page d'accès refusé

    if request.method == 'POST':
        rapport.delete()  # Supprime l'élément
        return redirect('rapport_listindividuel')  # Redirige vers la liste des rapports

    return render(request, 'fonctionnality/rapport_confirm_delete.html', {'rapport': rapport})



# Détails d'un rapport
@login_required
def rapport_detail_individuel(request, pk):
    rapport = get_object_or_404(RapportIndividuel, pk=pk)
    return render(request, 'fonctionnality/rapport_detail.html', {'rapport': rapport})




@login_required
def export_individuel_pdf(request, rapport_id):
    # Récupérer le rapport spécifique
    rapport = get_object_or_404(RapportIndividuel, id=rapport_id)

    # Vérifier et formater la date
    if not isinstance(rapport.date, datetime):
        report_date = rapport.date  # Suppose que rapport.date est un champ DateTimeField
    else:
        report_date = rapport.date.date()

    formatted_date = report_date.strftime('%d-%m-%Y')

    # Définir la locale en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'fr')

    # Calcul et formatage de la date du rapport hebdomadaire
    debut_semaine = report_date - timedelta(days=report_date.weekday())  # Lundi
    fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

    # Récupérer le type de rapport
    type_rapport = rapport.rapport if rapport.rapport else "Type_Inconnu"
    type_rapport = type_rapport.replace("'", "").replace(" ", "_")  # Nettoyage

    # Récupérer le nom de l'auteur
    if rapport.auteur:
        auteur_nom = f"{rapport.auteur.first_name}_{rapport.auteur.last_name}".strip()
        auteur_nom = auteur_nom.replace(" ", "_").replace("/", "-")  # Nettoyage
    else:
        auteur_nom = "Auteur_inconnu"

    # Générer le titre du rapport
    rapport_date = f"RAPPORT {type_rapport} DU {debut_semaine.strftime('%d/%m')} AU {fin_semaine.strftime('%d/%m/%Y')} - {rapport.auteur.first_name} {rapport.auteur.last_name}" if rapport.auteur else "Auteur inconnu"

    # Contexte pour le template
    context = {
        'rapport': rapport,
        'rapport_date': rapport_date,
        'base_url': request.build_absolute_uri('/'),  # Chemin Absolu pour Bootstrap + Images
    }

    # Charger le template et rendre le contexte
    template = get_template('fonctionnality/source_pdf.html')
    html = template.render(context)

    # Options pour pdfkit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)

    # Nom du fichier basé sur le type de rapport, l'auteur et la date
    filename = f"rapport_{type_rapport}_{auteur_nom}_{formatted_date}.pdf"
    print(f"Nom du fichier généré : {filename}")  # Debugging

    # Créer la réponse HTTP avec le PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


#----------------------------------------fin rapports individuels--------------------------------------------------------/




#----------------------------------------home et authentification--------------------------------------------------------/


def home(request):
    return render(request, 'home.html')




def signup(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            context['errors'] = form.errors
    else:
        form = UserRegistrationForm
    return render(request, 'accounts/signup.html', context={'form': form})





def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})






#----------------------------------------home et authentification--------------------------------------------------------/

@login_required
def dashboard(request):
    # Récupérer les 7 derniers utilisateurs connectés
    utilisateurs = CustomerUser.objects.filter(last_login__isnull=False).order_by('-last_login')[:6]
    dernier_technique = Technique.objects.last()

    total_rap_bc = Boncomtoir.objects.count()
    total_rap_comta = Comptabilite.objects.count()
    total_rap_Technique = Technique.objects.count()
    total_rap_Marqueting = Marketing.objects.count()

    # Derniers enregistrements pour chaque modèle
    dernier_rap_bc = Boncomtoir.objects.last()
    dernier_rap_comta = Comptabilite.objects.last()
    dernier_rap_technique = Technique.objects.last()
    dernier_rap_marqueting = Marketing.objects.last()
    dernier_rap_generaux = Generaux.objects.last()
    dernier_rap_individuel = RapportIndividuel.objects.last()
    dernier_rap_equipe = RapportEquippe.objects.last()

    # Créer une liste de tous les derniers rapports
    from django.urls import reverse

    rapports = [
        {'rapport': dernier_rap_bc, 'type': 'BON COMPTOIR',
         'url': reverse('boncomptoir_detail', args=[dernier_rap_bc.pk]) if dernier_rap_bc else None},
        {'rapport': dernier_rap_comta, 'type': 'COMPTABILITE',
         'url': reverse('detail_rapport', args=[dernier_rap_comta.pk]) if dernier_rap_comta else None},
        {'rapport': dernier_rap_technique, 'type': 'TECHNIQUE',
         'url': reverse('detailTechnique', args=[dernier_rap_technique.pk]) if dernier_rap_technique else None},
        {'rapport': dernier_rap_marqueting, 'type': 'MARKETING',
         'url': reverse('marketing_detail', args=[dernier_rap_marqueting.pk]) if dernier_rap_marqueting else None},
        {'rapport': dernier_rap_generaux, 'type': 'GENERAUX',
         'url': reverse('generaux_detail', args=[dernier_rap_generaux.pk]) if dernier_rap_generaux else None},
        {'rapport': dernier_rap_individuel, 'type': 'Rapport Individuel', 'url': reverse('rapport_detail_individuel',
                                                                                         args=[
                                                                                             dernier_rap_individuel.pk]) if dernier_rap_individuel else None},
        {'rapport': dernier_rap_equipe, 'type': 'Rapport Equipe',
         'url': reverse('rapport_detail_equippe', args=[dernier_rap_equipe.pk]) if dernier_rap_equipe else None},
    ]

    # Filtrer les rapports non nuls
    rapports = [r for r in rapports if r['rapport'] is not None]

    # Trier les rapports par date
    rapports.sort(key=lambda x: x['rapport'].date, reverse=True)

    # Récupérer l'avant-dernier enregistrement
    avant_dernier_enregistrement_bc = Boncomtoir.objects.order_by('-date').distinct()[:2]

    # Vérifier si nous avons au moins deux enregistrements
    if len(avant_dernier_enregistrement_bc ) == 2:
        avant_dernier_bc = avant_dernier_enregistrement_bc[1]  # L'avant-dernier
    else:
        avant_dernier_bc = None  # Pas assez d'enregistrements


    avant_dernier_enregistrement_tec = Technique.objects.order_by('-date').distinct()[:2]
    # Vérifier si nous avons au moins deux enregistrements
    if len(avant_dernier_enregistrement_tec) == 2:
        avant_dernier_tec = avant_dernier_enregistrement_tec[1]  # L'avant-dernier
    else:
        avant_dernier_tec = None  # Pas assez d'enregistrements

    avant_dernier_enregistrement_co = Comptabilite.objects.order_by('-date').distinct()[:2]
    # Vérifier si nous avons au moins deux enregistrements
    if len(avant_dernier_enregistrement_co) == 2:
        avant_dernier_co = avant_dernier_enregistrement_co[1]  # L'avant-dernier
    else:
        avant_dernier_co = None  # Pas assez d'enregistrements

    avant_dernier_enregistrement_ma = Marqueting.objects.order_by('-date').distinct()[:2]
    # Vérifier si nous avons au moins deux enregistrements
    if len(avant_dernier_enregistrement_ma) == 2:
        avant_dernier_ma = avant_dernier_enregistrement_ma[1]  # L'avant-dernier
    else:
        avant_dernier_ma = None  # Pas assez d'enregistrements



    pourcentage_total = 0
    if dernier_technique:
        pourcentage_total = dernier_technique.Pourcentage_Total()

    context = {
        'rapports': rapports,
        'total_rap_bc': total_rap_bc,
        'total_rap_Marqueting': total_rap_Marqueting,
        'total_rap_Technique': total_rap_Technique,
        'total_rap_comta': total_rap_comta,
        'utilisateurs': utilisateurs,
        'dernier_rap_bc': dernier_rap_bc,
        'dernier_rap_comta': dernier_rap_comta,
        'dernier_rap_technique': dernier_rap_technique,
        'dernier_rap_marqueting': dernier_rap_marqueting,
        'dernier_rap_generaux': dernier_rap_generaux,
        'dernier_rap_individuel': dernier_rap_individuel,
        'dernier_rap_equipe': dernier_rap_equipe,
        'pourcentage_total': pourcentage_total,
        'avant_dernier_bc': avant_dernier_bc,
        'avant_dernier_tec': avant_dernier_tec,
        'avant_dernier_co': avant_dernier_co,
        'avant_dernier_ma': avant_dernier_ma,
    }
    return render(request, 'fonctionnality/dashboard.html', context)

#----------------------------------------fin home et authentification--------------------------------------------------------/



# rubrique rapport individuel

@login_required
def rapport_list_equippe(request):
    rapports = RapportEquippe.objects.all().order_by('-date')
    # Créer un objet Paginator
    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'equippe/list.html', context)



@login_required
def rapport_create_equippe(request):
    if request.method == 'POST':
        form = RapportEquippeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rapport_list_equippe')
    else:
        form = RapportEquippeForm()
    return render(request, 'equippe/form.html', {'form': form})





def rapport_detail_equippe(request, pk):
    rapport = get_object_or_404(RapportEquippe, pk=pk)
    return render(request, 'equippe/detail.html', {'rapport': rapport})




@login_required
def export_equipe_pdf(request, rapport_id):
    # Récupérer le rapport spécifique
    rapport = get_object_or_404(RapportEquippe, id=rapport_id)

    # Vérifier et formater la date
    if not isinstance(rapport.date, datetime):
        report_date = rapport.date  # Suppose que rapport.date est un champ DateTimeField
    else:
        report_date = rapport.date.date()

    formatted_date = report_date.strftime('%d-%m-%Y')

    # Définir la locale en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'fr')

    # Calcul et formatage de la date du rapport hebdomadaire
    debut_semaine = report_date - timedelta(days=report_date.weekday())  # Lundi
    fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

    # Contexte pour le template
    context = {
        'rapport': rapport,
        'rapport_date': f"RAPPORT HEBDOMADAIRE DU {debut_semaine.strftime('%d/%m')} AU {fin_semaine.strftime('%d/%m/%Y')}",
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin Absolu pour Bootstrap + Images
    }

    # Charger le template et rendre le contexte
    template = get_template('equippe/rapport_equipe_pdf.html')
    html = template.render(context)

    # Options pour pdfkit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)

    # Nom du fichier basé sur la date d'enregistrement
    filename = f"rapport_equipe_{formatted_date}.pdf"

    # Créer la réponse HTTP avec le PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



@login_required
def rapport_update_equippe(request, pk):
    rapport = get_object_or_404(RapportEquippe, pk=pk)

    # Vérifier si l'utilisateur est le chef du projet ou un administrateur
    if request.user != rapport.chef and not request.user.is_superuser:
        return render(request, 'equippe/permission_denied.html', {"rapport": rapport})  # Page d'accès refusé

    if request.method == 'POST':
        form = RapportEquippeForm(request.POST, instance=rapport)
        if form.is_valid():
            form.save()
            return redirect('rapport_list_equippe')
    else:
        form = RapportEquippeForm(instance=rapport)

    return render(request, 'equippe/update.html', {'form': form, 'rapport': rapport})



@login_required
def rapport_delete_equippe(request, pk):
    rapport = get_object_or_404(RapportEquippe, pk=pk)

    # Vérifier si l'utilisateur est le chef du projet ou un administrateur
    if request.user != rapport.chef and not request.user.is_superuser:
        return render(request, 'equippe/permission_denied_delete.html', {"rapport": rapport})  # Page d'accès refusé

    if request.method == 'POST':
        rapport.delete()
        return redirect('rapport_list_equippe')

    return render(request, 'equippe/confirm_delete.html', {'rapport': rapport})



@login_required
def download_rapporte_equippe(request, pk):
    # Récupérer le rapport par PK
    rapport = get_object_or_404(RapportEquippe, pk=pk)

    # Rendre le template avec les détails du rapport
    html_string = render_to_string('equippe/rapport_detail.html', {'rapport': rapport})

    # Chemin temporaire pour le fichier Word
    output_file = f'temp_{rapport.titre}.docx'

    # Convertir le HTML en fichier Word
    pypandoc.convert_text(html_string, 'docx', outputfile=output_file, format='html')

    # Préparer la réponse HTTP pour le téléchargement
    with open(output_file, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{rapport.titre}.docx"'

    # Supprimer le fichier temporaire après l'envoi
    os.remove(output_file)

    return response



#----------------------------- fin rubrique rapport individuel------------------------------------------/

#----------------------------------------comptabilte--------------------------------------------------------/

# rubrique comptable

@login_required
def liste_comptabilite(request):
    rapports = Comptabilite.objects.all().order_by('-date')
    # Créer un objet Paginator
    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'comptabilite/liste.html', context)



@login_required
def detail_source(request, rapport_id):
    # Récupérer le rapport spécifique ou renvoyer une 404 si non trouvé
    rapport = get_object_or_404(Comptabilite, id=rapport_id)

    # Calculer le début et la fin de la semaine
    start_of_week = rapport.date - timedelta(days=rapport.date.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Formater les dates pour l'affichage
    start_date_str = start_of_week.strftime('%d/%m/%y')
    end_date_str = end_of_week.strftime('%d/%m/%y')

    context = {
        'rapport': rapport,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'comptabilite/source.html', context)



@login_required
def download_comptable(request, pk):
    # Récupérer le rapport par PK
    rapport = get_object_or_404(RapportEquippe, pk=pk)

    # Rendre le template avec les détails du rapport
    html_string = render_to_string('comptabilite/source.html', {'rapport': rapport})

    # Chemin temporaire pour le fichier Word
    output_file = f'temp_{rapport.titre}.docx'

    # Convertir le HTML en fichier Word
    pypandoc.convert_text(html_string, 'docx', outputfile=output_file, format='html')

    # Préparer la réponse HTTP pour le téléchargement
    with open(output_file, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{rapport.titre}.docx"'

    # Supprimer le fichier temporaire après l'envoi
    os.remove(output_file)

    return response




@login_required
def detail_rapport(request, rapport_id):
    # Récupérer le rapport spécifique ou renvoyer une 404 si non trouvé
    form = get_object_or_404(Comptabilite, id=rapport_id)

    # Calculer le début et la fin de la semaine
    start_of_week = form.date - timedelta(days=form.date.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Formater les dates pour l'affichage
    start_date_str = start_of_week.strftime('%d/%m/%y')
    end_date_str = end_of_week.strftime('%d/%m/%y')

    # Récupérer et nettoyer le contenu de l'objectif
    objectif_text = strip_tags(form.objectif)  # Assurez-vous que `objectif` existe dans votre modèle

    context = {
        'form': form,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'objectif_text': objectif_text,  # Ajoutez le texte formaté au contexte
    }
    return render(request, 'comptabilite/detail.html', context)


@login_required
def export_to_word(request, rapport_id):
    # Récupérer le rapport spécifique
    form = get_object_or_404(Comptabilite, id=rapport_id)

    # Collecter les données nécessaires
    context = {
        'form': form,
        'start_date': (form.date - timedelta(days=form.date.weekday())).strftime('%d/%m/%y'),
        'end_date': (form.date - timedelta(days=form.date.weekday()) + timedelta(days=6)).strftime('%d/%m/%y'),
        'statut': form.statut,
        'objectif': form.objectif,
        'description_autre': form.description_autre,
        'statut_Facture_etablies': form.statut_Facture_etablies,
        'quantite_Facture_etablies': form.quantite_Facture_etablies,
        'total_Facture_etablies': form.total_Facture_etablies,
        'statut_Devis': form.statut_Devis,
        'quantite_Devis': form.quantite_Devis,
        'total_Devis': form.total_Devis,
    }

    template = get_template('comptabilite/word_comptabilite.html')
    html = template.render(context)

    options = {
        'to': 'docx',  # Spécifiez le format de sortie
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'enable-local-file-access': None,  # Pour permettre l'accès aux fichiers locaux
    }

    words = pypandoc.convert_string(html, **options)

    response = HttpResponse(words, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="rapport_comptabilite.docx"'  # Utilisation de .docx
    return response


@login_required
def export_to_pdf(request, rapport_id):
    # Récupérer le rapport spécifique
    form = get_object_or_404(Comptabilite, id=rapport_id)

    # Utiliser la date d'enregistrement
    debut_semaine = form.date
    fin_semaine = debut_semaine + timedelta(days=6)
    mois = format_date(debut_semaine, 'MMMM', locale='fr').upper()
    date_string = f"SEMAINE DU {debut_semaine.day} AU {fin_semaine.day} {mois} {debut_semaine.year}"

    # Préparer les données du contexte
    context = {
        'form': form,
        'date_string': date_string,
        'start_date': (form.date - timedelta(days=form.date.weekday())).strftime('%d/%m/%y'),
        'end_date': (form.date - timedelta(days=form.date.weekday()) + timedelta(days=6)).strftime('%d/%m/%y'),
        'statut': form.statut,
        'objectif': form.objectif,
        'description_autre': form.description_autre,
        'statut_Facture_etablies': form.statut_Facture_etablies,
        'quantite_Facture_etablies': form.quantite_Facture_etablies,
        'total_Facture_etablies': form.total_Facture_etablies,
        'statut_Devis': form.statut_Devis,
        'quantite_Devis': form.quantite_Devis,
        'total_Devis': form.total_Devis,
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin Absolu pour Bootstrap + Images
    }

    # Affichage pour debug (à retirer après test)
    print(context)

    # Charger le template HTML
    template = get_template('comptabilite/word_comptabilite.html')
    html = template.render(context)

    # Options PdfKit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore',
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)
    filename = f"rapport_comptabilite_{debut_semaine.strftime('%Y-%m-%d')}.pdf"

    # Créer la réponse
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response




@login_required
def pdf_compta(template_source, context_dict={}):
    template = get_template(template_source)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    if pdf.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=400)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_comptabilite.pdf"'
    return response



@login_required
def supprimer_comptabilite(request, pk):
    rapports = get_object_or_404(Comptabilite, pk=pk)

    # Vérification des permissions
    if not (request.user.is_admin and request.user.departement == "COMPTABLE"):
        return render(request, "comptabilite/permission_denied_delete.html", {
            'rapports': rapports,  # 🔥 On passe l'objet pour le lien de retour
            'titre': rapports.titre
        }, status=403)

    if request.method == "POST":
        rapports.delete()
        return redirect('liste_comptabilite')
    return render(request, 'comptabilite/supprimer.html', {'rapport': rapports})



@login_required
def ajouter_comptabilite(request):
    user = request.user

    # Vérifie si l'utilisateur a les permissions requises
    if not ((user.is_admin or user.is_superuser) and user.departement == "COMPTABLE"):
        return render(request, "comptabilite/permission_denied_ajout.html", status=403)

    if request.method == "POST":
        form = ComptabiliteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_comptabilite')
    else:
        form = ComptabiliteForm()

    return render(request, 'comptabilite/ajouter.html', {'form': form})




@login_required
def modifier_comptabilite(request, pk):
    comptabilite = get_object_or_404(Comptabilite, pk=pk)

    # Vérification des permissions
    if not (request.user.is_admin and request.user.departement == "COMPTABLE"):
        return render(request, "comptabilite/permission_denied.html", {
            'rapports': comptabilite,  # 🔥 On passe l'objet pour le lien de retour
            'titre': comptabilite.titre
        }, status=403)

    if request.method == "POST":
        form = ComptabiliteForm(request.POST, instance=comptabilite)
        if form.is_valid():
            form.save()
            return redirect('liste_comptabilite')
        else:
            print(form.errors)  # Pour déboguer les erreurs
    else:
        form = ComptabiliteForm(instance=comptabilite)
    return render(request, 'comptabilite/modifier.html', {'form': form})

# rubrique marqueting




# boncomptoir
@login_required
def boncomtoir_list(request):
    rapports = Boncomtoir.objects.all().order_by('-date')
    # Créer un objet Paginator
    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'boncomptoir/boncomtoir_list.html', context)





# Création d'un Boncomtoir avec les SubComptoirs en inline
class BoncomtoirCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Boncomtoir
    form_class = BoncomtoirForm
    template_name = "boncomptoir/boncomptoir_form.html"
    success_url = reverse_lazy("boncomtoir_list")

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        # Vérifier si l'utilisateur est un superutilisateur
        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "BON_COMPTOIR"

    def handle_no_permission(self):

        return render(self.request, "boncomptoir/permission_denied_ajout.html", {
        }, status=403)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["subcomptoirs"] = SubComptoirFormSet(self.request.POST)
        else:
            data["subcomptoirs"] = SubComptoirFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        subcomptoirs = context["subcomptoirs"]
        self.object = form.save()
        if subcomptoirs.is_valid():
            subcomptoirs.instance = self.object
            subcomptoirs.save()
        return super().form_valid(form)




class BoncomtoirUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Boncomtoir
    form_class = BoncomtoirForm
    template_name = "boncomptoir/update_boncomptoir.html"
    success_url = reverse_lazy("boncomtoir_list")

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "BON_COMPTOIR"

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        boncomtoir_id = self.kwargs.get('pk')  # Récupérer l'ID de l'objet depuis l'URL
        boncomptoir = get_object_or_404(Boncomtoir, pk=boncomtoir_id)  # Récupérer l'objet

        return render(self.request, "boncomptoir/permission_denied.html", {
            'boncomptoir': boncomptoir,  # 🔥 Ajout de l'objet complet
            'titre': boncomptoir.titre
        }, status=403)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Ajouter le titre au contexte
        data["titre"] = self.object.titre

        if self.request.POST:
            data["subcomptoirs"] = SubComptoirFormSet(self.request.POST, instance=self.object)
        else:
            data["subcomptoirs"] = SubComptoirFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        # Sauvegarder l'objet principal d'abord
        self.object = form.save()

        # Récupérer le formset depuis le contexte
        context = self.get_context_data()
        subcomptoirs = context["subcomptoirs"]

        if subcomptoirs.is_valid():
            # Filtrer les formulaires vides avant de sauvegarder
            cleaned_forms = []
            for sub_form in subcomptoirs:
                # Vérifier si le formulaire est vide
                if any(sub_form.cleaned_data.get(field) not in [None, '', []] for field in sub_form.cleaned_data):
                    cleaned_forms.append(sub_form)

            if cleaned_forms:
                subcomptoirs.instance = self.object  # Associer le parent
                subcomptoirs.save()  # Sauvegarder uniquement les valides
        else:
            print("Erreurs du formset :")
            for form in subcomptoirs:
                if form.errors:
                    print(form.errors)

        return super().form_valid(form)





class BoncomtoirDetailView(LoginRequiredMixin, DetailView):
    model = Boncomtoir
    template_name = "boncomptoir/detail_boncomptoir.html"
    context_object_name = "boncomptoir"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fonction pour formater la liste des utilisateurs
        def format_user_list(user_queryset):
            return ", ".join([user.username for user in user_queryset if user.username]) or "Aucune personne assignée"

        # Récupérer les SubComptoirs
        subcomptoirs = self.object.subcomptoir_set.all()

        # Initialisation de la liste subcomptoirs_data
        subcomptoirs_data = []


        for subcomptoir in subcomptoirs:
            subcomptoir_data = {
                "activite": subcomptoir.activite,
                "quantite": subcomptoir.quantite,
                "Nombre_de_personne": format_user_list(subcomptoir.Nombre_de_personne.all()),
                "personne_en_charge": format_user_list(subcomptoir.personne_en_charge.all()),
                "pourcentage_activite": subcomptoir.pourcentage_activite,
                "pourcentage_de_charge_individuel": subcomptoir.pourcentage_de_charge_individuel,
                "statut": subcomptoir.statut,
            }
            subcomptoirs_data.append(subcomptoir_data)

        context["subcomptoirs_data"] = subcomptoirs_data
        context["personnes_en_charge"] = format_user_list(self.object.nombre_personne.all())
        context["personnes_en_charge_le_sheet"] = format_user_list(self.object.personne_en_charge_le_sheet.all())
        context["nombre_personne_importer"] = format_user_list(self.object.Nombre_presonne_importer.all())
        context["personne_en_charge_importer"] = format_user_list(self.object.personne_en_charge_importer.all())
        context["nombre_personne_flyers"] = format_user_list(self.object.Nombre_presonne_flyers.all())
        context["personne_en_charge_flyers"] = format_user_list(self.object.personne_en_charge_flyers.all())

        # Format Date
        debut_semaine = self.object.date
        fin_semaine = debut_semaine + timedelta(days=6)
        mois = format_date(debut_semaine, "MMMM", locale="fr").upper()
        context["date_semaine"] = f"SEMAINE DU {debut_semaine.day} AU {fin_semaine.day} {mois} {debut_semaine.year}"

        return context





@login_required
def boncomtoir_delete(request, pk):
    rapports = get_object_or_404(Boncomtoir, pk=pk)

    # Vérification si l'utilisateur est un super utilisateur
    if request.user.is_superuser:
        if request.method == 'POST':
            rapports.delete()
            return redirect('boncomtoir_list')

        return render(request, 'boncomptoir/boncomtoir_delete.html', {'rapport': rapports})

    # Vérification des permissions
    if not (request.user.is_admin and request.user.departement == "BON_COMPTOIR"):
        return render(request, "boncomptoir/permission_denied_delete.html", {
            'boncomptoir': rapports,  # 🔥 On passe l'objet pour le lien de retour
            'titre': rapports.titre
        }, status=403)

    if request.method == 'POST':
        rapports.delete()
        return redirect('boncomtoir_list')

    return render(request, 'boncomptoir/boncomtoir_delete.html', {'rapport': rapports})





@login_required
def export_boncomptoir_pdf(request, rapport_id):
    # Récupérer le rapport spécifique
    form = get_object_or_404(Boncomtoir, id=rapport_id)

    # Utiliser la date d'enregistrement
    debut_semaine = form.date
    fin_semaine = debut_semaine + timedelta(days=6)
    mois = format_date(debut_semaine, 'MMMM', locale='fr').upper()
    date_string = f"SEMAINE DU {debut_semaine.day} AU {fin_semaine.day} {mois} {debut_semaine.year}"

    # Récupérer les usernames
    nombre_presonne = form.nombre_personne.all()
    usernames = [user.username for user in nombre_presonne if user and user.username]

    personne_en_charge_le_sheet = form.personne_en_charge_le_sheet.all()
    usernames_personne_en_charge = [user.username for user in personne_en_charge_le_sheet if user and user.username]

    nombres_presonne_importer = form.Nombre_presonne_importer.all()
    usernames_nombre_presonne_importer = [user.username for user in nombres_presonne_importer if user and user.username]

    personne_en_charge_importer = form.personne_en_charge_importer.all()
    usernames_personne_en_charge_importer = [user.username for user in personne_en_charge_importer if user and user.username]

    nombres_presonne_flyers = form.Nombre_presonne_flyers.all()
    usernames_nombre_presonne_flyers = [user.username for user in nombres_presonne_flyers if user and user.username]

    personne_en_charge_flyers = form.personne_en_charge_flyers.all()
    usernames_personne_en_charge_flyers = [user.username for user in personne_en_charge_flyers if user and user.username]

    # Récupérer les données des SubComptoirs liés à ce Boncomptoir
    subcomptoirs = form.subcomptoir_set.all()
    subcomptoirs_data = []
    for subcomptoir in subcomptoirs:
        subcomptoir_data = {
            'activite': subcomptoir.activite,
            'quantite': subcomptoir.quantite,
            'Nombre_de_personne': [user.username for user in subcomptoir.Nombre_de_personne.all()],
            'pourcentage_activite': subcomptoir.pourcentage_activite,
            'personnes_en_charge': [user.username for user in subcomptoir.personne_en_charge.all()],
            'pourcentage_de_charge_individuel': subcomptoir.pourcentage_de_charge_individuel,
            'statut': subcomptoir.statut,
        }
        subcomptoirs_data.append(subcomptoir_data)

    # 🔥 Ajouter le base_url ici
    context = {
        'form': form,
        'date_string': date_string,
        'usernames': usernames,
        'nombre_presonne': nombre_presonne,
        'usernames_personne_en_charge': usernames_personne_en_charge,
        'usernames_nombre_presonne_importer': usernames_nombre_presonne_importer,
        'usernames_personne_en_charge_importer': usernames_personne_en_charge_importer,
        'usernames_nombre_presonne_flyers': usernames_nombre_presonne_flyers,
        'usernames_personne_en_charge_flyers': usernames_personne_en_charge_flyers,
        'subcomptoirs_data': subcomptoirs_data,  # 🔥 Ajout des données des SubComptoirs
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin Absolu pour Bootstrap + Images
    }

    # Affichage pour debug (à retirer après test)
    print(context)

    # Charger le template
    template = get_template('boncomptoir/pdf_boncomptoir.html')
    html = template.render(context)

    # Options PdfKit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',  # Ajuste la taille du contenu
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)
    filename = f"rapport_du_Hebdomadaire_Boncomptoir_{debut_semaine.strftime('%Y-%m-%d')}.pdf"

    # Créer la réponse
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



# fin boncomptoir




# Liste des objets
@login_required
def marqueting_list(request):
    rapports = Marqueting.objects.all().order_by('-date')

    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ajouter des dates de début et de fin de semaine à chaque rapport sur la page actuelle
    for rapport in page_obj:
        rapport.date_start_of_week = rapport.date - timedelta(days=rapport.date.weekday())
        rapport.date_end_of_week = rapport.date_start_of_week + timedelta(days=6)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'marqueting/marqueting_list.html', context)


# Supprimer un objet





@login_required
def create_marqueting(request):
    # Vérifiez si l'utilisateur est l'auteur ou un administrateur

    # Vérifiez si l'utilisateur est l'auteur ou un administrateur
    if not request.user.is_authenticated:
        return render(request, 'marqueting/permission_denied_ajout.html')

    # Vous pouvez vérifier si l'utilisateur a le droit de créer un marqueting
    if not request.user.is_superuser:
        # Ajoutez une logique ici pour vérifier si l'utilisateur a des droits spécifiques
        return render(request, 'marqueting/permission_denied_ajout.html')

    if request.method == 'POST':
        marqueting_form = MarquetingForm(request.POST)
        variant_formset = VariantFormSet(request.POST)  # Obtenez les données du formset

        if marqueting_form.is_valid() and variant_formset.is_valid():
            marqueting = marqueting_form.save()
            variants = variant_formset.save(commit=False)  # Ne pas sauvegarder immédiatement

            # Liste pour stocker les variantes valides
            valid_variants = []

            for variant in variants:
                # Vérifiez si au moins un champ est rempli
                if any([variant.autre_un, variant.objectifs, variant.quantites, variant.Total,
                         variant.acteur, variant.Activites, variant.Entreprises,
                         variant.Particuliers, variant.Services, variant.Consommables,
                         variant.materiel_informatique, variant.formation,
                         variant.Statut, variant.Difficultes_rencontrees,
                         variant.Raisons_e_l_echec_de_l_objectif, variant.Actions_correctives]):
                    variant.Marqueting = marqueting  # Associez la variante à marqueting
                    valid_variants.append(variant)  # Ajoutez à la liste des variantes valides

            # Sauvegardez uniquement les variantes valides
            for variant in valid_variants:
                variant.save()

            return redirect('marqueting_list')  # Redirigez vers la liste

    else:
        marqueting_form = MarquetingForm()
        variant_formset = VariantFormSet()  # Créez un nouveau formset vide

    return render(request, 'marqueting/marqueting_form.html', {
        'form': marqueting_form,
        'variant_formset': variant_formset,
    })



class MarquetingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Marqueting
    form_class = MarquetingForm
    template_name = 'marqueting/marqueting_modify.html'
    success_url = reverse_lazy('marqueting_list')

    def test_func(self):
        """Seuls les admins du département 'Marketing' peuvent modifier un Marqueting"""
        user = self.request.user
        return user.is_superuser or (user.is_admin and user.departement == "Marketing")

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        marketing = get_object_or_404(Marqueting, pk=self.kwargs.get('pk'))
        return render(self.request, "marqueting/permission_denied.html", {
            'Marketing': marketing,
            'titre': marketing.titre
        }, status=403)

    def get_context_data(self, **kwargs):
        """Charge le formset des variantes"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['variant_formset'] = VariantFormSet(self.request.POST, instance=self.object)
        else:
            context['variant_formset'] = VariantFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        """Sauvegarde le formulaire et le formset correctement"""
        self.object = form.save()  # Sauvegarde du Marqueting principal
        context = self.get_context_data()
        variant_formset = context['variant_formset']

        if variant_formset.is_valid():
            variants = variant_formset.save(commit=False)  # Récupère les variantes sans les enregistrer immédiatement

            for variant in variants:
                variant.Marqueting = self.object  # Associer la variante au Marqueting
                variant.save()  # Sauvegarde de chaque variante modifiée ou nouvelle

            # Supprimer les variantes marquées comme supprimées par l'utilisateur
            for deleted_variant in variant_formset.deleted_objects:
                deleted_variant.delete()

            # Sauvegarde finale des relations ManyToMany (si nécessaire)
            variant_formset.save_m2m()

        else:
            print("🚨 Erreurs dans le formset :", variant_formset.errors)  # Debug des erreurs

        return super().form_valid(form)


    


@login_required
def detail_marqueting(request, pk):
    # Récupérer l'objet Marqueting
    marqueting_instance = get_object_or_404(Marqueting, pk=pk)

    # Récupérer la date de création
    date_obj = marqueting_instance.date  # Assurez-vous que ce champ est bien un objet datetime

    # Trouver le lundi de la semaine de cette date
    start_of_week = date_obj - timedelta(days=date_obj.weekday())

    # Trouver le dimanche de la même semaine
    end_of_week = start_of_week + timedelta(days=6)

    # Format de la date "DD/MM/YYYY au DD/MM/YYYY"
    semaine_formatee = f"{start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}"

    context = {
        'form': marqueting_instance,
        'variant_formset': Variant.objects.filter(Marqueting=marqueting_instance),
        'semaine_formatee': semaine_formatee,  # Ajout de la plage de dates formatée
    }

    return render(request, 'marqueting/marqueting_detail.html', context)



@login_required
def export_marqueting_pdf(request, pk):
    # Récupérer l'instance Marqueting
    marqueting_instance = get_object_or_404(Marqueting, pk=pk)

    # Vérifier et formater la date
    date_obj = marqueting_instance.date
    if isinstance(date_obj, datetime):
        report_date = date_obj.date()
    else:
        report_date = date_obj  # Supposé être un champ DateField

    formatted_date = report_date.strftime('%d-%m-%Y')

    # Trouver le lundi et le dimanche de la semaine correspondante
    start_of_week = report_date - timedelta(days=report_date.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Format de la période : "DD/MM/YYYY au DD/MM/YYYY"
    semaine_formatee = f"{start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}"

    # Définir la locale en français pour les dates
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'fr')

    # Récupérer les Variants liés à cet enregistrement Marqueting
    variants = Variant.objects.filter(Marqueting=marqueting_instance)

    # Construire les données pour le template
    variants_data = [
        {
            'autre_un': variant.autre_un,
            'objectifs': variant.objectifs,
            'quantites': variant.quantites,
            'Total': variant.Total,
            'acteur': variant.acteur,
            'Activites': variant.Activites,
            'Entreprises': variant.Entreprises,
            'Particuliers': variant.Particuliers,
            'Services': variant.Services,
            'Consommables': variant.Consommables,
            'materiel_informatique': variant.materiel_informatique,
            'formation': variant.formation,
            'Statut': variant.Statut,
            'Difficultes_rencontrees': variant.Difficultes_rencontrees,
            'Raisons_e_l_echec_de_l_objectif': variant.Raisons_e_l_echec_de_l_objectif,
            'Actions_correctives': variant.Actions_correctives,
            'pourcentage': variant.pourcentage,  # Propriété calculée
        }
        for variant in variants
    ]

    # Contexte envoyé au template
    context = {
        'form': marqueting_instance,
        'semaine_formatee': semaine_formatee,  # 🔥 Clé correcte pour le template
        'variants_data': variants_data,
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin absolu pour CSS/Images
    }

    # Charger le template et le rendre avec le contexte
    template = get_template('marqueting/pdf_marqueting.html')
    html = template.render(context)

    # Options pour pdfkit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)

    # Nom du fichier basé sur la date
    filename = f"rapport_hebdomadaire_marqueting_{formatted_date}.pdf"

    # Créer la réponse HTTP avec le PDF en pièce jointe
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



#--------------------------------------------Technique--------------------------------------------------------/

# 📌 Création d'une technique avec formsets


@login_required
def listTechnique(request):
    rapports = Technique.objects.all().order_by('-date')
    # Créer un objet Paginator
    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'technique/technique_list.html', context)



class TechniqueDeleteView(LoginRequiredMixin, DeleteView):
    model = Technique
    template_name = "technique/technique_delete.html"
    success_url = reverse_lazy('technique_list')






class TechniqueCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Technique
    form_class = TechniqueForm
    template_name = 'technique/technique_form_create.html'

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        # Vérifier si l'utilisateur est un superutilisateur
        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "TECHNIQUE"

    def handle_no_permission(self):

        return render(self.request, "technique/permission_denied_ajout.html", {
        }, status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ext_formset'] = SubTechniqueExtFormSet(self.request.POST)
            context['int_formset'] = SubTechniqueIntFormSet(self.request.POST)
        else:
            context['ext_formset'] = SubTechniqueExtFormSet()
            context['int_formset'] = SubTechniqueIntFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ext_formset = context['ext_formset']
        int_formset = context['int_formset']
        self.object = form.save()  # Enregistrement de l'objet Technique

        if ext_formset.is_valid() and int_formset.is_valid():
            ext_formset.instance = self.object
            int_formset.instance = self.object
            ext_formset.save()
            int_formset.save()
            return redirect('listTechnique')
        else:
            return self.render_to_response(self.get_context_data(form=form))



class TechniqueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Technique
    template_name = 'technique/technique_confirm_delete.html'
    success_url = reverse_lazy('listTechnique')

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        # Vérifier si l'utilisateur est un superutilisateur
        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "TECHNIQUE"

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        technique_id = self.kwargs.get('pk')  # Récupérer l'ID de l'objet depuis l'URL
        technique = get_object_or_404(Technique, pk=technique_id)  # Récupérer l'objet

        return render(self.request, "technique/permission_denied_delete.html", {
            'technique': technique,  # 🔥 Ajout de l'objet complet
            'titre': technique.titre
        }, status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter l'objet technique dans le contexte directement
        context['rapport'] = context['object']
        return context




class TechniqueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Technique
    form_class = TechniqueForm
    template_name = 'technique/technique_form_update.html'
    success_url = reverse_lazy('listTechnique')

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "TECHNIQUE"

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        technique_id = self.kwargs.get('pk')  # Récupérer l'ID de l'objet depuis l'URL
        technique = get_object_or_404(Technique, pk=technique_id)  # Récupérer l'objet

        return render(self.request, "technique/permission_denied.html", {
            'technique': technique,  # 🔥 Ajout de l'objet complet
            'titre': technique.titre
        }, status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ajouter le titre de l'objet au contexte
        context['titre_objet'] = self.object.titre if self.object else "Nouvelle Technique"

        if self.request.POST:
            context['ext_formset'] = SubTechniqueExtFormSet(self.request.POST, instance=self.object)
            context['int_formset'] = SubTechniqueIntFormSet(self.request.POST, instance=self.object)
        else:
            context['ext_formset'] = SubTechniqueExtFormSet(instance=self.object)
            context['int_formset'] = SubTechniqueIntFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ext_formset = context['ext_formset']
        int_formset = context['int_formset']

        # Sauvegarder l'objet principal
        self.object = form.save()

        # Sauvegarder les formsets même s'ils ne sont pas valides
        ext_formset.instance = self.object
        int_formset.instance = self.object

        ext_formset.save()  # Sauvegarder le formset externe
        int_formset.save()  # Sauvegarder le formset interne

        # Redirection en cas de succès
        return super().form_valid(form)

    def form_invalid(self, form):
        # Pour afficher les erreurs dans le template, vous pouvez simplement rendre la réponse
        return self.render_to_response(self.get_context_data(form=form))






class TechniquesDetailView(DetailView):
    model = Technique
    template_name = 'technique/technique_detail.html'
    context_object_name = 'technique'  # Nom de l'objet dans le template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les activités externes liées
        activites_externes = self.object.activites_externes.all()
        activites_internes = self.object.activites_internes.all()  # S'il y a aussi un modèle interne

        # Compter le nombre d'objets ayant activite=None et ext_action=None
        none_externes_count = sum(
            1 for act in activites_externes
            if act.ext_clients is None and act.ext_action is None
        )

        # Compter le nombre d'objets ayant int_clients=None et int_action=None
        none_internes_count = sum(
            1 for act in activites_internes
            if act.int_clients is None and act.int_action is None
        )

        # Ajouter au contexte
        context.update({
            'activites_externes': activites_externes,
            'activites_internes': activites_internes,
            'rowspan_externe': max(1, activites_externes.count() + 2 + none_externes_count),
            'rowspan_interne': max(1, activites_internes.count() + 2 + none_internes_count),
            # Évite les erreurs si 0 activité externe
        })

        # Calcul et formatage de la date du rapport hebdomadaire
        date_du_rapport = self.object.date.date()  # Convertir en date
        debut_semaine = date_du_rapport - timedelta(days=date_du_rapport.weekday())  # Lundi
        fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

        # Formater le rapport hebdomadaire
        context['rapport_date'] = f"RAPPORT HEBDOMADAIRE DU {debut_semaine.strftime('%d/%m')} AU {fin_semaine.strftime('%d/%m/%Y')}"

        return context





@login_required
def export_Techniques_pdf(request, technique_id):
    # Récupérer le rapport spécifique
    technique = get_object_or_404(Technique, id=technique_id)

    # Vérifier et formater la date
    if not isinstance(technique.date, datetime):
        report_date = technique.date  # Suppose que technique.date est un champ DateTimeField
    else:
        report_date = technique.date.date()

    formatted_date = report_date.strftime('%d-%m-%Y')

    # Définir la locale en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'fr')

    # Calcul et formatage de la date du rapport hebdomadaire
    debut_semaine = report_date - timedelta(days=report_date.weekday())  # Lundi
    fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

    # Vérification des activités
    activites_externes = technique.activites_externes.all() if hasattr(technique, 'activites_externes') else []
    activites_internes = technique.activites_internes.all() if hasattr(technique, 'activites_internes') else []

    # Compter le nombre d'objets ayant activite=None et ext_action=None
    none_externes_count = sum(
        1 for act in activites_externes
        if act.ext_clients is None and act.ext_action is None
    )

    # Compter le nombre d'objets ayant int_clients=None et int_action=None
    none_internes_count = sum(
        1 for act in activites_internes
        if act.int_clients is None and act.int_action is None
    )
    # Contexte pour le template
    context = {
        'technique': technique,
        'activites_externes': activites_externes,
        'activites_internes': activites_internes,
        'rowspan_externe': max(1, len(activites_externes) + 2 + none_externes_count),
        'rowspan_interne': max(1, len(activites_internes) + 2 + none_internes_count),
        'rapport_date': f"RAPPORT HEBDOMADAIRE DU {debut_semaine.strftime('%d/%m')} AU {fin_semaine.strftime('%d/%m/%Y')}",
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin Absolu pour Bootstrap + Images
    }

    # Charger le template et rendre le contexte
    template = get_template('technique/technique_pdf.html')
    html = template.render(context)

    # Options pour pdfkit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)

    # Nom du fichier basé sur la date d'enregistrement
    filename = f"RAPPORT_HEBDOMADAIRE_DU_DEPARTEMEMENT_TECHNIQUE_DU_{formatted_date}.pdf"

    # Créer la réponse HTTP avec le PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


#--------------------------------------------fin Technique--------------------------------------------------------/




#--------------------------------------------generaux--------------------------------------------------------/
@login_required
def generaux_list(request):
    rapports = Generaux.objects.all().order_by('-date')

    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ajouter des dates de début et de fin de semaine à chaque rapport sur la page actuelle
    for rapport in page_obj:
        rapport.date_start_of_week = rapport.date - timedelta(days=rapport.date.weekday())
        rapport.date_end_of_week = rapport.date_start_of_week + timedelta(days=6)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'generaux/generaux_list.html', context)


@login_required
def generaux_create(request):
    # Vérifiez si l'utilisateur est l'auteur ou un administrateur
    if not request.user.is_authenticated:
        return render(request, 'generaux/permission_denied_ajout.html')

    # Vous pouvez vérifier si l'utilisateur a le droit de créer un marqueting
    if not request.user.is_superuser:
        # Ajoutez une logique ici pour vérifier si l'utilisateur a des droits spécifiques
        return render(request, 'generaux/permission_denied_ajout.html')

    if request.method == 'POST':
        form = GenerauxForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('generaux_list')
    else:
        form = GenerauxForm()
    return render(request, 'generaux/generaux_form.html', {'form': form})


@login_required
def generaux_update(request, pk):
    generaux = get_object_or_404(Generaux, pk=pk)

    # Vérification si l'utilisateur est un super utilisateur
    if request.user.is_superuser:
        if request.method == 'POST':
            generaux.delete()
            return redirect('generaux_list')

        return render(request, 'generaux/generaux_delete.html', {'rapport': generaux})

    # Vérification des permissions
    if not (request.user.is_admin and request.user.departement == "BON_COMPTOIR"):
        return render(request, "generaux/permission_denied.html", {
            'generaux': generaux,  # 🔥 On passe l'objet pour le lien de retour
            'titre': generaux.titre
        }, status=403)


    if request.method == 'POST':
        form = GenerauxForm(request.POST, instance=generaux)
        if form.is_valid():
            form.save()
            return redirect('generaux_list')
    else:
        form = GenerauxForm(instance=generaux)
    return render(request, 'generaux/generaux_update.html', {'form': form})


@login_required
def generaux_delete(request, pk):
    generaux = get_object_or_404(Generaux, pk=pk)

    # Vérification si l'utilisateur est un super utilisateur
    if request.user.is_superuser:
        if request.method == 'POST':
            generaux.delete()
            return redirect('generaux_list')

        return render(request, 'generaux/generaux_delete.html', {'rapport': generaux})

    # Vérification des permissions
    if not (request.user.is_admin and request.user.departement == "BON_COMPTOIR"):
        return render(request, "generaux/permission_denied_delete.html", {
            'generaux': generaux,  # 🔥 On passe l'objet pour le lien de retour
            'titre': generaux.titre
        }, status=403)

    if request.method == 'POST':
        generaux.delete()
        return redirect('generaux_list')
    return render(request, 'generaux/generaux_delete.html', {'generaux': generaux})





@login_required
def generaux_detail(request, pk):
    generaux = get_object_or_404(Generaux, pk=pk)
    maintenant = timezone.now()

    # Calculer le début et la fin de la semaine en cours
    debut_semaine = maintenant - timedelta(days=maintenant.weekday())  # Lundi
    fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

    # Format de la date en français
    hebdo = f"{debut_semaine.day} au {fin_semaine.day} {format_date(debut_semaine, 'MMMM yyyy', locale='fr')}"

    return render(request, 'generaux/detail.html', {'generaux': generaux, 'hebdo': hebdo,})



@login_required
def export_generaux_pdf(request, rapport_id):
    # Récupérer le rapport spécifique
    form = get_object_or_404(Generaux, id=rapport_id)

    maintenant = timezone.now()

    # Calculer le début et la fin de la semaine en cours
    debut_semaine = maintenant - timedelta(days=maintenant.weekday())  # Lundi
    fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

    # Format de la date en français
    hebdo = f"{debut_semaine.day} au {fin_semaine.day} {format_date(debut_semaine, 'MMMM yyyy', locale='fr')}"

    context = {
        'form': form,
        'hebdo': hebdo,
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin Absolu pour Bootstrap + Images
    }

    template = get_template('generaux/pdf_generaux.html')
    html = template.render(context)

    # Options PdfKit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',  # Ajuste la taille du contenu
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)
    filename = f"rapport_Hebdomadaire_SERVICE_GENERAUX_du_{debut_semaine.strftime('%Y-%m-%d')}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response





#--------------------------------------------fin generaux--------------------------------------------------------/


#--------------------------------------------hebdomadaire--------------------------------------------------------/


@login_required
def derniers_rapports(request):
        maintenant = timezone.now()

        # Calculer le début et la fin de la semaine en cours
        debut_semaine = maintenant - timedelta(days=maintenant.weekday())  # Lundi
        fin_semaine = debut_semaine + timedelta(days=6)  # Dimanche

        # Format de la date en français
        hebdo = f"{debut_semaine.day} au {fin_semaine.day} {format_date(debut_semaine, 'MMMM yyyy', locale='fr')}"

        # Filtrer les rapports
        comptabilites = Comptabilite.objects.filter(date__range=(debut_semaine, fin_semaine))
        bons_comptoir = Boncomtoir.objects.filter(date__range=(debut_semaine, fin_semaine))
        marqueting_reports = Marqueting.objects.filter(date__range=(debut_semaine, fin_semaine))
        technique_reports = Technique.objects.filter(date__range=(debut_semaine, fin_semaine))
        generaux_reports = Generaux.objects.all()

        # Récupérer le dernier rapport de chaque modèle
        dernier_comptabilite = comptabilites.latest('date') if comptabilites.exists() else None
        dernier_boncomtoir = bons_comptoir.latest('date') if bons_comptoir.exists() else None
        dernier_marqueting = marqueting_reports.latest('date') if marqueting_reports.exists() else None
        dernier_technique = technique_reports.latest('date') if technique_reports.exists() else None
        dernier_generaux = generaux_reports.latest('date') if generaux_reports.exists() else None

        return render(request, 'hebdomadaire/derniers_rapports.html', {
            'hebdo': hebdo,
            'dernier_comptabilite': dernier_comptabilite,
            'dernier_boncomtoir': dernier_boncomtoir,
            'dernier_marqueting': dernier_marqueting,
            'dernier_technique': dernier_technique,
            'dernier_generaux': dernier_generaux,
        })


#--------------------------------------------fin hebdomadaire-------------------------------------------------------/

#--------------------------------------------recherche-------------------------------------------------------/
@login_required
def search(request):
    query = request.GET.get('q', '')
    date_query = request.GET.get('date', '').strip()  # Nettoyer la date

    # Vérifier si la date est valide
    date_filter = Q()
    if date_query:
        try:
            # Convertir la chaîne au format DD/MM/YYYY en objet date
            valid_date = datetime.strptime(date_query, '%d/%m/%Y').date()
            date_filter = Q(date__exact=valid_date)  # Filtrer par date exacte
        except ValueError:
            date_filter = Q()  # Pas de filtrage par date en cas d'erreur

    # Récupération des résultats de chaque modèle
    boncomtoirs = Boncomtoir.objects.filter(
        Q(titre__icontains=query) | Q(objectif__icontains=query) | date_filter
    )
    marketing_results = Marqueting.objects.filter(
        Q(titre__icontains=query) | Q(Nombre_de_rendez_vous_objectifs__icontains=query) | date_filter
    )
    technique_results = Technique.objects.filter(
        Q(titre__icontains=query) | Q(clients_externe__icontains=query) | date_filter
    )
    rapport_individuel_results = RapportIndividuel.objects.filter(
        Q(titre__icontains=query) | Q(description__icontains=query) | date_filter
    )
    comptabilite_results = Comptabilite.objects.filter(
        Q(titre__icontains=query) | Q(objectif__icontains=query) | date_filter
    )
    generaux_results = Generaux.objects.filter(
        Q(titre__icontains=query) | Q(description__icontains=query) | date_filter
    )
    rapport_equipe_results = RapportEquippe.objects.filter(
        Q(titre__icontains=query) | Q(description__icontains=query) | date_filter
    )

    # Fusionner les résultats dans une liste unique avec les bons noms de routes Django
    rapports = [
                   {'rapport': r, 'type': 'BON COMPTOIR', 'url_name': 'boncomptoir_detail', 'id': r.id,
                    'pdf_url': 'export_boncomptoir_pdf'} for r in boncomtoirs
               ] + [
                   {'rapport': r, 'type': 'MARKETING', 'url_name': 'detail_marqueting', 'id': r.id, 'pdf_url': None} for
                   r in marketing_results
               ] + [
                   {'rapport': r, 'type': 'TECHNIQUE', 'url_name': 'detailTechnique', 'id': r.id,
                    'pdf_url': 'export_Techniques_pdf'} for r in technique_results
               ] + [
                   {'rapport': r, 'type': 'RAPPORT INDIVIDUEL', 'url_name': 'rapport_detail_individuel', 'id': r.id,
                    'pdf_url': 'export_individuel_pdf'} for r in rapport_individuel_results
               ] + [
                   {'rapport': r, 'type': 'COMPTABILITE', 'url_name': 'detail_rapport', 'id': r.id,
                    'pdf_url': 'export_to_pdf'} for r in comptabilite_results
               ] + [
                   {'rapport': r, 'type': 'SERVICES GENERAUX', 'url_name': 'generaux_detail', 'id': r.id,
                    'pdf_url': 'export_generaux_pdf'} for r in generaux_results
               ] + [
                   {'rapport': r, 'type': 'RAPPORT PAR EQUIPE', 'url_name': 'rapport_detail_equippe', 'id': r.id,
                    'pdf_url': 'export_equipe_pdf'} for r in rapport_equipe_results
               ]

    # Trier par date (du plus récent au plus ancien)
    rapports.sort(key=lambda x: x['rapport'].date, reverse=True)

    # Pagination
    paginator = Paginator(rapports, 10)  # 10 résultats par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'date_query': date_query,  # Ajouter la date à votre contexte
        'page_obj': page_obj,
        'rapports': page_obj,
    }
    return render(request, 'recherche/recherche.html', context)

#--------------------------------------------fin recherche-------------------------------------------------------/



#--------------------------------------------test--------------------------------------------------------/


# Création d'un Boncomtoir avec les SubComptoirs en inline
class MarketingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Marketing
    form_class = MarketingForm
    template_name = "marketing/marketing_form.html"
    success_url = reverse_lazy("marketing_list")  # Correction ici

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        # Vérifier si l'utilisateur est un superutilisateur
        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "MARKETING"

    def handle_no_permission(self):

        return render(self.request, "marketing/permission_denied_ajout.html", {
        }, status=403)



    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["submarketings"] = SubMarketingFormSet(self.request.POST)  # Correction ici
        else:
            data["submarketings"] = SubMarketingFormSet()  # Correction ici
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        submarketings = context["submarketings"]  # Correction ici
        self.object = form.save()
        if submarketings.is_valid():
            submarketings.instance = self.object
            submarketings.save()
        return super().form_valid(form)



@login_required
def marketing_list(request):
    rapports = Marketing.objects.all().order_by('-date')

    paginator = Paginator(rapports, 10)  # Affiche 10 rapports par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ajouter des dates de début et de fin de semaine à chaque rapport sur la page actuelle
    for rapport in page_obj:
        rapport.date_start_of_week = rapport.date - timedelta(days=rapport.date.weekday())
        rapport.date_end_of_week = rapport.date_start_of_week + timedelta(days=6)

    context = {
        'rapports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'marketing/marketing_list.html', context)




class MarketingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Marketing
    form_class = MarketingForm
    template_name = "marketing/update_marketing.html"
    success_url = reverse_lazy("marketing_list")

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "MARKETING"

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        marketing_id = self.kwargs.get('pk')  # Récupérer l'ID de l'objet depuis l'URL
        marketing = get_object_or_404(Marketing, pk=marketing_id)  # Récupérer l'objet

        return render(self.request, "marketing/permission_denied.html", {
            'marketing': marketing,  # 🔥 Ajout de l'objet complet
            'titre': marketing.titre
        }, status=403)



    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["titre"] = self.object.titre

        if self.request.POST:
            data["submarketings"] = SubMarketingFormSet(self.request.POST, instance=self.object)
        else:
            data["submarketings"] = SubMarketingFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        self.object = form.save()
        context = self.get_context_data()
        submarketings = context["submarketings"]

        if submarketings.is_valid():
            cleaned_forms = []
            for sub_form in submarketings:
                if any(sub_form.cleaned_data.get(field) not in [None, '', []] for field in sub_form.cleaned_data):
                    cleaned_forms.append(sub_form)

            if cleaned_forms:
                submarketings.instance = self.object
                submarketings.save()
        else:
            print("Erreurs du formset :")
            for form in submarketings:
                if form.errors:
                    print(form.errors)

        return super().form_valid(form)




class MarketingDetailView(DetailView):
    model = Marketing
    template_name = "marketing/marketing_detail.html"
    context_object_name = "marketing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marketing_instance = self.object

        # Fonction pour formater la liste des utilisateurs
        def format_user_list(user_queryset):
            return ", ".join([user.username for user in user_queryset if user.username]) or "Aucune personne assignée"

        # Récupérer les SubMarketing liés à ce Marketing
        submarketings = marketing_instance.submarketing_set.all()

        # Initialisation de la liste submarketings_data
        submarketings_data = []

        for submarketing in submarketings:
            submarketing_data = {
                "indicateur": submarketing.indicateur,
                "objectifs": submarketing.objectifs,
                "quantites": submarketing.quantites,
                "total": submarketing.Total,
                "acteur": submarketing.acteur,
                "activites": submarketing.Activites,
                "entreprises": submarketing.Entreprises,
                "Particuliers": submarketing.Particuliers,
                "Services": submarketing.Services,
                "Consommables": submarketing.Consommables,
                "materiel_informatique": submarketing.materiel_informatique,
                "formation": submarketing.formation,
                "Statut": submarketing.Statut,
                "Difficultes_rencontrees": submarketing.Difficultes_rencontrees,
                "Raisons_e_l_echec_de_l_objectif": submarketing.Raisons_e_l_echec_de_l_objectif,
                "Actions_correctives": submarketing.Actions_correctives,
            }
            submarketings_data.append(submarketing_data)

        context["submarketings_data"] = submarketings_data

        # Format Date
        if marketing_instance.date:
            date_obj = marketing_instance.date
            start_of_week = date_obj - timedelta(days=date_obj.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            context["semaine_formatee"] = f"{start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}"
        else:
            context["semaine_formatee"] = "Date non disponible"

        return context



def export_marketing_pdf(request, pk):
    # Récupérer l'instance Marketing
    marketing_instance = get_object_or_404(Marketing, pk=pk)

    # Vérifier et formater la date
    date_obj = marketing_instance.date
    if isinstance(date_obj, datetime):
        report_date = date_obj.date()
    else:
        report_date = date_obj  # Supposé être un champ DateField

    formatted_date = report_date.strftime('%d-%m-%Y')

    # Trouver le lundi et le dimanche de la semaine correspondante
    start_of_week = report_date - timedelta(days=report_date.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche

    # Format de la période : "DD/MM/YYYY au DD/MM/YYYY"
    semaine_formatee = f"{start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}"

    # Définir la locale en français pour les dates
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'fr')

    # Récupérer les SubMarketing associés à cet enregistrement Marketing
    sub_marketing_instances = SubMarketing.objects.filter(marketing=marketing_instance)

    # Construire les données pour le template
    sub_marketing_data = [
        {
            'indicateur': sub.indicateur,
            'objectifs': sub.objectifs,
            'quantites': sub.quantites,
            'Total': sub.Total,
            'acteur': sub.acteur,
            'Activites': sub.Activites,
            'Entreprises': sub.Entreprises,
            'Particuliers': sub.Particuliers,
            'Services': sub.Services,
            'Consommables': sub.Consommables,
            'materiel_informatique': sub.materiel_informatique,
            'formation': sub.formation,
            'Statut': sub.Statut,
            'Difficultes_rencontrees': sub.Difficultes_rencontrees,
            'Raisons_e_l_echec_de_l_objectif': sub.Raisons_e_l_echec_de_l_objectif,
            'Actions_correctives': sub.Actions_correctives,
        }
        for sub in sub_marketing_instances
    ]

    # Contexte envoyé au template
    context = {
        'marketing': marketing_instance,
        'semaine_formatee': semaine_formatee,  # 🔥 Clé correcte pour le template
        'sub_marketing_data': sub_marketing_data,
        'base_url': request.build_absolute_uri('/'),  # 🔥 Chemin absolu pour CSS/Images
    }

    # Charger le template et le rendre avec le contexte
    template = get_template('marketing/pdf_marketing.html')
    html = template.render(context)

    # Options pour pdfkit
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        'zoom': '0.75',
        'quiet': '',
        'load-error-handling': 'ignore'
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)

    # Nom du fichier basé sur la date
    filename = f"rapport_hebdomadaire_marketing_{formatted_date}.pdf"

    # Créer la réponse HTTP avec le PDF en pièce jointe
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response




class MarketingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Marketing
    template_name = 'marketing/marketing_confirm_delete.html'
    context_object_name = 'marketing'
    success_url = reverse_lazy('marketing_list')  # Redirige vers la liste après suppression

    def test_func(self):
        """Seuls les admins du département 'Bon Comptoir' peuvent modifier un Boncomtoir"""
        user = self.request.user

        if user.is_superuser:
            return True

        # Vérifier si l'utilisateur est admin ET appartient au département "Bon Comptoir"
        return user.is_admin and user.departement == "MARKETING"

    def handle_no_permission(self):
        """Affiche une page d'erreur personnalisée au lieu d'un 403"""
        marketing_id = self.kwargs.get('pk')  # Récupérer l'ID de l'objet depuis l'URL
        marketing = get_object_or_404(Marketing, pk=marketing_id)  # Récupérer l'objet

        return render(self.request, "marketing/permission_denied_delete.html", {
            'marketing': marketing,  # 🔥 Ajout de l'objet complet
            'titre': marketing.titre
        }, status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marketing = self.object
        # Récupérer les SubMarketing liés à cet objet Marketing
        context['submarketings'] = marketing.submarketing_set.all()
        return context

    def delete(self, request, *args, **kwargs):
        marketing = self.get_object()
        # Supprimer les SubMarketing associés
        marketing.submarketing_set.all().delete()
        return super().delete(request, *args, **kwargs)
