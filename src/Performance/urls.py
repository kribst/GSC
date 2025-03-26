from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .views import export_to_pdf, home, \
    liste_comptabilite, supprimer_comptabilite, ajouter_comptabilite, boncomtoir_list, detail_rapport, \
    export_to_word, \
    boncomtoir_delete, export_boncomptoir_pdf, marqueting_list, create_marqueting, \
    derniers_rapports, search, rapport_create_equippe, signup, login_view, dashboard, rapport_listindividuel, \
    rapport_createindividuel, rapport_updateindividuel, rapport_deleteindividuel, \
    rapport_detail_individuel, rapport_list_equippe, rapport_update_equippe, rapport_detail_equippe, \
    rapport_delete_equippe, download_rapporte_equippe, BoncomtoirCreateView, BoncomtoirUpdateView, BoncomtoirDetailView, \
    modifier_comptabilite, generaux_detail, export_generaux_pdf, listTechnique, \
    TechniqueCreateView, TechniqueUpdateView, TechniquesDetailView, export_Techniques_pdf, export_individuel_pdf, \
    export_equipe_pdf, TechniqueDeleteView, detail_marqueting, export_marqueting_pdf, \
    MarquetingUpdateView, MarketingCreateView, marketing_list, MarketingUpdateView, MarketingDetailView, \
    MarketingDeleteView

urlpatterns = [
    path('', home, name='home'),
    path('inscription/', signup, name='signup'),
    path('connexion/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
#----------------- rapport individuel-----------------------------------------------------------------/
    path('rapport_listindividuel/', rapport_listindividuel, name='rapport_listindividuel'),
    path('rapport/<int:pk>/', rapport_detail_individuel, name='rapport_detail_individuel'),
    path('rapport_createindividuel', rapport_createindividuel, name='rapport_createindividuel'),
    path('rapport/update-individuel/<int:pk>/', rapport_updateindividuel, name='rapport_updateindividuel'),
    path('rapport/delete/<int:pk>/', rapport_deleteindividuel, name='rapport_deleteindividuel'),
    path('rapport/<int:rapport_id>/pdf/', export_individuel_pdf, name='export_individuel_pdf'),
 #---------------------------fin rapport individuel----------------------------------------------------------/
 # ---------------------------comptablite----------------------------------------------------------/
    path('rapports/liste_comptabilite', liste_comptabilite, name='liste_comptabilite'),
    path('comptabilite/<int:rapport_id>/', detail_rapport, name='detail_rapport'),
    path('rapports/supprimer/<int:pk>/', supprimer_comptabilite, name='supprimer_comptabilite'),
    path('rapports/ajouter/', ajouter_comptabilite, name='ajouter_comptabilite'),
    path('download_comptabilite/<int:rapport_id>/export/', export_to_word, name='export_to_word'),
    path('download_comptabilite_pdf/<int:rapport_id>/export_pdf/', export_to_pdf, name='export_to_pdf'),
    path('rapports/comptabilite/modifier/<int:pk>/', modifier_comptabilite, name='modifier_comptabilite'),
# ---------------------------fin comptabilite----------------------------------------------------------/
    path('download_boncomptoir_pdf/<int:rapport_id>/', export_boncomptoir_pdf, name='export_boncomptoir_pdf'),
    path('rapports/boncomtoir_list', boncomtoir_list, name='boncomtoir_list'),
    path('rapports/boncomtoir_create', BoncomtoirCreateView.as_view(), name='boncomptoir_create'),
    path('boncomptoir/update/<int:pk>/', BoncomtoirUpdateView.as_view(), name='boncomtoir_update'),
    path('boncomtoir/<int:pk>/', BoncomtoirDetailView.as_view(), name='boncomptoir_detail'),
    path('rapports/boncomtoir_delete/<int:pk>', boncomtoir_delete, name='boncomtoir_delete'),

# ---------------------------fin boncomptoir----------------------------------------------------------/
    path("rapports/marqueting_list", marqueting_list, name="marqueting_list"),
    path('rapports/marqueting/nouveau/', create_marqueting, name='create_marqueting'),
    path('rapports/marqueting/detail/<int:pk>/', detail_marqueting, name='detail_marqueting'),
    path('marqueting/update/<int:pk>/', MarquetingUpdateView.as_view(), name='marqueting_update'),
    path('export/marqueting/<int:pk>/pdf/', export_marqueting_pdf, name='export_marqueting_pdf'),
    # --------------------------- rapport technique----------------------------------------------------------/
    path('rapports/technique/<int:pk>/', TechniquesDetailView.as_view(), name='detailTechnique'),
    path('rapports/Technique_list', listTechnique, name='listTechnique'),
    path('rapports/technique/create/', TechniqueCreateView.as_view(), name='technique_create'),
    path('rapports/technique/update/<int:pk>/', TechniqueUpdateView.as_view(), name='technique_update'),
    path('rapports/technique/pdf/<int:technique_id>/', export_Techniques_pdf, name='export_Techniques_pdf'),
    path('technique/<int:pk>/delete/', TechniqueDeleteView.as_view(), name='deleteTechnique'),

# --------------------------- rapport technique----------------------------------------------------------/

# --------------------------- generaux----------------------------------------------------------/
    path('rapports/generaux_list', views.generaux_list, name='generaux_list'),
    path('rapports/generaux_create/', views.generaux_create, name='generaux_create'),
    path('rapports/generaux/update/<int:pk>/', views.generaux_update, name='generaux_update'),
    path('rapports/generaux/delete/<int:pk>/', views.generaux_delete, name='generaux_delete'),
    path('rapports/generaux/<int:pk>/', generaux_detail, name='generaux_detail'),
    path('rapports/generaux/export-generaux-pdf/<int:rapport_id>/', export_generaux_pdf, name='export_generaux_pdf'),
# ---------------------------fin generaux----------------------------------------------------------/
#--------------------------------------------hebdomadaire--------------------------------------------------------/
    path('rapports/derniers/', derniers_rapports, name='derniers_rapports'),
#--------------------------------------------hebdomadaire--------------------------------------------------------/
    path('search/', search, name='search'),

    # ---------------------------fin rapport equippe----------------------------------------------------------/
    path('rapports_equippe/equippe', rapport_list_equippe, name='rapport_list_equippe'),
    path('rapport/equippe/nouveau/', rapport_create_equippe, name='rapport_create_equippe'),
    path('rapports_equippe/update_equippe/<int:pk>/', rapport_update_equippe, name='rapport_update_equippe'),
    path('rapports_equippe/equippe/<int:pk>/', rapport_detail_equippe, name='rapport_detail_equippe'),
    path('rapports_equippe/delete/<int:pk>/', rapport_delete_equippe, name='rapport_delete_equippe'),
    path('rapports_equippe/download/<int:pk>/', download_rapporte_equippe, name='download_rapporte_equippe'),
    path('<int:rapport_id>/export_pdf/', export_equipe_pdf, name='export_equipe_pdf'),
 # ---------------------------fin rapport equippe----------------------------------------------------------/
    path('marketing/create/', MarketingCreateView.as_view(), name='marketing_create'),
    path("rapports/marketing_list", marketing_list, name="marketing_list"),
    path('marketing/update/<int:pk>/', MarketingUpdateView.as_view(), name='marketing_update'),
    path("marketing/detail/<int:pk>/", MarketingDetailView.as_view(), name="marketing_detail"),
    path('marketing/<int:pk>/export_pdf/', views.export_marketing_pdf, name='export_marketing_pdf'),
    path('marketing/<int:pk>/delete/', MarketingDeleteView.as_view(), name='marketing-delete'),
]
