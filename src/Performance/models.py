from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from tinymce import models as tinymce_models



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password):
        if not email:
            raise ValueError("Vous devez entrer une adresse email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, username=None, first_name=None, last_name=None):
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save()
        return user


class CustomerUser(AbstractBaseUser):
    poste = models.CharField(max_length=100, null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    DEPARTEMENT_CHOICES = [
        ('BON_COMPTOIR', 'Bon Comptoir'),
        ('MARKETING', 'Marketing'),
        ('SERVICE_GENERAUX', 'Service Généraux'),
        ('TECHNIQUE', 'Technique'),
        ('SOFT', 'Soft'),
        ('COMPTABLE', 'Comptable'),
    ]

    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    genre = models.CharField(max_length=8, choices=GENDER_CHOICES, null=True, blank=True)
    pays = CountryField(blank_label='(select country)', blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    departement = models.CharField(max_length=50, choices=DEPARTEMENT_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True, blank=False)

    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return self.is_superuser or super().has_module_perms(app_label)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

    class Meta:
        ordering = ['first_name', ]



class Departement(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    chef = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name='departement_chef')
    utilisateur = models.ManyToManyField(CustomerUser, related_name='departements')

    def __str__(self):
        return self.nom if self.nom else "Nom non défini"




class RapportEquippe(models.Model):
    titre = models.CharField(max_length=255, blank=True, null=True)
    objectif = tinymce_models.HTMLField()

    STATUT_CHOICES = [
        ('Terminé', 'Terminé'),
        ('En Cours', 'En Cours'),
        ('En Pause', 'En Pause'),
        ('Risqué', 'Risqué'),
        ('Planifié', 'Planifié'),
    ]
    statut = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)
    chef = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name='chef_project')
    date = models.DateTimeField()
    description = tinymce_models.HTMLField()
    travailleur = models.ManyToManyField(CustomerUser, related_name='rapports_travailleur')
    superviseur = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name='rapports_superviseur')
    departement = models.ManyToManyField(Departement, related_name='rapport_departement')

    def __str__(self):
        return self.titre




class RapportIndividuel(models.Model):
    titre = models.CharField(max_length=255, blank=True, null=True, unique=True)
    STATUT_CHOICES = [
        ('Terminé', 'Terminé'),
        ('En Cours', 'En Cours'),
        ('En Pause', 'En Pause'),
        ('Risqué', 'Risqué'),
    ]
    TYPE_CHOICES = [
        ("JOURNALIER", "JOURNALIER"),
        ("HEBDOMADAIRE", "HEBDOMADAIRE"),
        ("D'ACTIVITE", "D'ACTIVITE"),
    ]
    rapport = models.CharField(max_length=255, choices=TYPE_CHOICES, blank=True, null=True)
    statut = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)
    date = models.DateTimeField()
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    auteur = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name='auteur')
    description = tinymce_models.HTMLField(blank=True, null=True)


    def __str__(self):
        return self.titre


class TitreDescription(models.Model):
    titre = models.CharField(max_length=255)
    sous_titre = models.CharField(max_length=255)
    description = models.TextField()
    rapport = models.ForeignKey(RapportIndividuel, on_delete=models.CASCADE, related_name='titres_descriptions')

    def __str__(self):
        return self.titre



# section comptabilite



class Comptabilite(models.Model):
    titre = models.CharField(max_length=255, blank=True, null=True, unique=True)
    STATUT_CHOICES = [
        ('Terminé', 'Terminé'),
        ('En Cours', 'En Cours'),
        ('En Pause', 'En Pause'),
        ('Risqué', 'Risqué'),
        ('Planifié', 'Planifié'),
    ]
    statut = models.CharField(max_length=255, choices=STATUT_CHOICES)
    date = models.DateTimeField(verbose_name="Date", help_text="Entrez la date.")
    objectif = tinymce_models.HTMLField()
    description_autre = tinymce_models.HTMLField(blank=True, null=True)

    statut_Facture_etablies = models.CharField(max_length=255)
    quantite_Facture_etablies = models.PositiveIntegerField(
        verbose_name="Factures établies",
        blank=True,
        null=True,
    )

    total_Facture_etablies = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Factures établies",
        blank=True,
        null=True,
    )

    statut_Devis = models.CharField(max_length=10000)
    quantite_Devis = models.PositiveIntegerField(
        verbose_name="Devis",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Devis = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Devis",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Demande_de_cotation = models.CharField(max_length=10000)
    quantite_Demande_de_cotation = models.PositiveIntegerField(
        verbose_name="Demande de cotation par mail",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Demande_de_cotation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Demande de cotation par mail",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Livraison_Expedition = models.CharField(max_length=10000)
    quantite_Livraison_Expedition = models.PositiveIntegerField(
        verbose_name="Livraison / Expedition",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Livraison_Expedition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Livraison / Expedition",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Cheques_recus = models.CharField(max_length=10000)
    quantite_Cheques_recus = models.PositiveIntegerField(
        verbose_name="Chèques reçus",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,

    )
    total_Cheques_recus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Chèques reçus",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Depots_cheques = models.CharField(max_length=10000)
    quantite_Depots_cheques = models.PositiveIntegerField(
        verbose_name="Dépôts chèques",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Depots_cheques = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Dépôts chèques",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Bon_de_Commande = models.CharField(max_length=10000)
    quantite_Bon_de_Commande = models.PositiveIntegerField(
        verbose_name="Bon de Commande",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Bon_de_Commande = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Bon de Commande",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Recouvrements_creances = models.CharField(max_length=10000)
    quantite_Recouvrements_creances = models.PositiveIntegerField(
        verbose_name="Recouvrements créances",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )
    total_Recouvrements_creances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Recouvrements créances",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    statut_Recharge_carte_UBA = models.CharField(max_length=10000)
    quantite_Recharge_carte_UBA = models.CharField(max_length=255)
    total_Recharge_carte_UBA = models.DecimalField(max_digits=10, decimal_places=2)

    statut_Recharge_carte_ACCESS = models.CharField(max_length=10000)
    quantite_Recharge_carte_ACCESS = models.CharField(
        max_length=10000,
        verbose_name="Recharge carte ACCESS",
        blank=True,
        null=True,

    )
    total_Recharge_carte_ACCESS = models.IntegerField()

    statut_Receptions_mails = models.CharField(max_length=10000)
    quantite_Receptions_mails = models.PositiveIntegerField(
        verbose_name="Réceptions mails",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,

    )
    total_Receptions_mails = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Réceptions mails",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,

    )

    statut_Mails_envoyes = models.CharField(max_length=10000)
    quantite_Mails_envoyes = models.PositiveIntegerField(
        verbose_name="Mails envoyés",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,

    )
    total_Mails_envoyes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Mails envoyés",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,

    )

    statut_Saisir_ecritures_logiciel_Sage = models.CharField(max_length=10000)
    quantite_Saisir_ecritures_logiciel_Sage = models.CharField(max_length=255)
    total_Saisir_ecritures_logiciel_Sage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total des saisies des écritures dans le logiciel Sage I7.",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,

    )

    statut_Teledeclaration_impot = models.CharField(max_length=1000000)
    quantite_Teledeclaration_impot = models.CharField(max_length=255)

    total_Teledeclaration_impot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total de la télé Télédeclarationmpôt",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,

    )


    statut_Paiement_impot = models.CharField(max_length=10000)
    quantite_Paiement_impot = models.CharField(
        max_length=10000,
        verbose_name="Paiement impôt",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )

    total_Paiement_impot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Paiement impôt",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )


    statut_Depot_de_facture_en_presentiels = models.CharField(max_length=10000)
    quantite_Depot_de_facture_en_presentiels = models.PositiveIntegerField(
        verbose_name="Dépôt de facture en présentiel",
        help_text="Entrez une quantité positive.",
        blank=True,
        null=True,
    )


    total_Depot_de_facture_en_presentiels = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total des dépôts de factures en présentiel",
        help_text="Entrez un montant total valide.",
        blank=True,
        null=True,
    )

    @property
    def pourcentage_Facture_etablies(self):
        # Convertir quantite_Facture_etablies en entier
        quantite = int(self.quantite_Facture_etablies) if isinstance(self.quantite_Facture_etablies, str) else int(
            self.quantite_Facture_etablies)

        # Convertir total_Facture_etablies en entier, en utilisant 0 si None
        total = int(self.total_Facture_etablies) if self.total_Facture_etablies is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Devis(self):
        # Convertir quantite_Devis en entier
        quantite = int(self.quantite_Devis) if isinstance(self.quantite_Devis, str) else self.quantite_Devis

        # Convertir total_Devis en float, en utilisant 0 si None
        total = float(self.total_Devis) if self.total_Devis is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Demande_de_cotation(self):
        # Convertir quantite_Demande_de_cotation en entier
        quantite = int(self.quantite_Demande_de_cotation) if isinstance(self.quantite_Demande_de_cotation,
                                                                        str) else self.quantite_Demande_de_cotation

        # Convertir total_Demande_de_cotation en float, en utilisant 0 si None
        total = float(self.total_Demande_de_cotation) if self.total_Demande_de_cotation is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Livraison_Expedition(self):
        # Convertir quantite_Livraison_Expedition en entier
        quantite = int(self.quantite_Livraison_Expedition) if isinstance(self.quantite_Livraison_Expedition,
                                                                         str) else self.quantite_Livraison_Expedition

        # Convertir total_Livraison_Expedition en float, en utilisant 0 si None
        total = float(self.total_Livraison_Expedition) if self.total_Livraison_Expedition is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Cheques_recus(self):
        # Convertir quantite_Cheques_recus en entier
        quantite = int(self.quantite_Cheques_recus) if isinstance(self.quantite_Cheques_recus,
                                                                  str) else self.quantite_Cheques_recus

        # Convertir total_Cheques_recus en float, en utilisant 0 si None
        total = float(self.total_Cheques_recus) if self.total_Cheques_recus is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None


    @property
    def pourcentage_Depots_cheques(self):
        # Convertir quantite_Depots_cheques en entier
        quantite = int(self.quantite_Depots_cheques) if isinstance(self.quantite_Depots_cheques,
                                                                   str) else self.quantite_Depots_cheques

        # Convertir total_Depots_cheques en float, en utilisant 0 si None
        total = float(self.total_Depots_cheques) if self.total_Depots_cheques is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Bon_de_Commande(self):
        # Convertir quantite_Bon_de_Commande en entier
        quantite = int(self.quantite_Bon_de_Commande) if isinstance(self.quantite_Bon_de_Commande,
                                                                    str) else self.quantite_Bon_de_Commande

        # Convertir total_Bon_de_Commande en float, en utilisant 0 si None
        total = float(self.total_Bon_de_Commande) if self.total_Bon_de_Commande is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Recouvrements_creances(self):
        # Convertir quantite_Recouvrements_creances en entier
        quantite = int(self.quantite_Recouvrements_creances) if isinstance(self.quantite_Recouvrements_creances,
                                                                           str) else self.quantite_Recouvrements_creances

        # Convertir total_Recouvrements_creances en float, en utilisant 0 si None
        total = float(self.total_Recouvrements_creances) if self.total_Recouvrements_creances is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Recharge_carte_UBA(self):
        # Convertir quantite_Recharge_carte_UBA en entier
        quantite = int(self.quantite_Recharge_carte_UBA) if isinstance(self.quantite_Recharge_carte_UBA,
                                                                       str) else self.quantite_Recharge_carte_UBA

        # Convertir total_Recharge_carte_UBA en float, en utilisant 0 si None
        total = float(self.total_Recharge_carte_UBA) if self.total_Recharge_carte_UBA is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Recharge_carte_ACCESS(self):
        # Convertir quantite_Recharge_carte_ACCESS en entier
        quantite = int(self.quantite_Recharge_carte_ACCESS) if isinstance(self.quantite_Recharge_carte_ACCESS,
                                                                          str) else self.quantite_Recharge_carte_ACCESS

        # Convertir total_Recharge_carte_ACCESS en float, en utilisant 0 si None
        total = float(self.total_Recharge_carte_ACCESS) if self.total_Recharge_carte_ACCESS is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Receptions_mails(self):
        # Convertir quantite_Receptions_mails en entier
        quantite = int(self.quantite_Receptions_mails) if isinstance(self.quantite_Receptions_mails,
                                                                     str) else self.quantite_Receptions_mails

        # Convertir total_Receptions_mails en float, en utilisant 0 si None
        total = float(self.total_Receptions_mails) if self.total_Receptions_mails is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Mails_envoyes(self):
        # Convertir quantite_Mails_envoyes en entier
        quantite = int(self.quantite_Mails_envoyes) if isinstance(self.quantite_Mails_envoyes,
                                                                  str) else self.quantite_Mails_envoyes

        # Convertir total_Mails_envoyes en float, en utilisant 0 si None
        total = float(self.total_Mails_envoyes) if self.total_Mails_envoyes is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Saisir_ecritures_logiciel_Sage(self):
        # Convertir quantite_Saisir_ecritures_logiciel_Sage en entier
        quantite = int(self.quantite_Saisir_ecritures_logiciel_Sage) if isinstance(
            self.quantite_Saisir_ecritures_logiciel_Sage, str) else self.quantite_Saisir_ecritures_logiciel_Sage

        # Convertir total_Saisir_ecritures_logiciel_Sage en float, en utilisant 0 si None
        total = float(
            self.total_Saisir_ecritures_logiciel_Sage) if self.total_Saisir_ecritures_logiciel_Sage is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Paiement_impot(self):
        # Convertir quantite_Paiement_impot en entier
        quantite = int(self.quantite_Paiement_impot) if isinstance(self.quantite_Paiement_impot,
                                                                   str) else self.quantite_Paiement_impot

        # Convertir total_Paiement_impot en float, en utilisant 0 si None
        total = float(self.total_Paiement_impot) if self.total_Paiement_impot is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None


    @property
    def pourcentage_Depot_de_facture_en_presentiels(self):
        # Convertir quantite_Depot_de_facture_en_presentiels en entier
        quantite = int(self.quantite_Depot_de_facture_en_presentiels) if isinstance(
            self.quantite_Depot_de_facture_en_presentiels, str) else self.quantite_Depot_de_facture_en_presentiels

        # Convertir total_Depot_de_facture_en_presentiels en float, en utilisant 0 si None
        total = float(
            self.total_Depot_de_facture_en_presentiels) if self.total_Depot_de_facture_en_presentiels is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None

    @property
    def pourcentage_Teledeclaration_impot(self):
        # Convertir quantite_Teledeclaration_impot en entier
        quantite = int(self.quantite_Teledeclaration_impot) if isinstance(
            self.quantite_Teledeclaration_impot, str) else self.quantite_Teledeclaration_impot

        # Convertir total_Teledeclaration_impot en float, en utilisant 0 si None
        total = float(self.total_Teledeclaration_impot) if self.total_Teledeclaration_impot is not None else 0

        # Calculer le pourcentage
        pourcentage = (quantite * 100) / total if total != 0 else 0

        # Vérifier si le pourcentage est supérieur à 100
        return int(pourcentage) if pourcentage <= 100 else None


    @property
    def pourcentage_global(self):
        pourcentages = [
            self.pourcentage_Facture_etablies,
            self.pourcentage_Devis,
            self.pourcentage_Demande_de_cotation,
            self.pourcentage_Livraison_Expedition,
            self.pourcentage_Cheques_recus,
            self.pourcentage_Depots_cheques,
            self.pourcentage_Bon_de_Commande,
            self.pourcentage_Recouvrements_creances,
            self.pourcentage_Recharge_carte_UBA,
            self.pourcentage_Recharge_carte_ACCESS,
            self.pourcentage_Receptions_mails,
            self.pourcentage_Mails_envoyes,
            self.pourcentage_Saisir_ecritures_logiciel_Sage,
            self.pourcentage_Paiement_impot,
            self.pourcentage_Depot_de_facture_en_presentiels,
            self.pourcentage_Teledeclaration_impot
        ]

        # Filtrer les pourcentages valides (non None et supérieurs à 0)
        pourcentages_valides = [p for p in pourcentages if p is not None and p > 0]

        if not pourcentages_valides:
            return 0

        # Calculer la moyenne
        total = sum(pourcentages_valides) / len(pourcentages_valides)
        return int(total) if total <= 100 else None  # Vérifie que le total ne dépasse pas 100

    def __str__(self):
        return self.titre




# fin comptabilté

#--------------------------------------------------rubrique boncompoir----------------------------------------------------------/



class Boncomtoir(models.Model):
    STATUT_CHOICES = [
        ('Terminé', 'Terminé'),
        ('En Cours', 'En Cours'),
        ('En Pause', 'En Pause'),
        ('Risqué', 'Risqué'),
        ('Planifié', 'Planifié'),
    ]

    titre = models.CharField(max_length=255, blank=True, null=True)
    objectif = tinymce_models.HTMLField()
    date = models.DateTimeField(verbose_name="Date", help_text="Entrez la date.")
    # chargement des produits sheet

    quantite_produit = models.PositiveIntegerField(verbose_name="Quantite_produit_dans_le_sheet", help_text="Entrez une quantité positive.", blank=True,null=True)
    quantite_total_produit = models.PositiveIntegerField(verbose_name="Quantite_total_produit_dans_le_sheet", help_text="Entrez une quantité positive.", blank=True,null=True)
    nombre_personne = models.ManyToManyField(CustomerUser, related_name='personne_en_charge_pour_le_sheet')
    personne_en_charge_le_sheet = models.ManyToManyField(CustomerUser, related_name='Nombre_presonne_pour_le_sheet')
    pourcentage_individuel_quantite_produit = models.CharField(max_length=255, blank=True, null=True)
    statut_qte_produit_sheet = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)

    # chargement des produits sur le site

    quantite_importer = models.PositiveIntegerField(verbose_name="Quantite_produit_site", help_text="Entrez_une_quantité_positive.", blank=True, null=True)
    quantite_total_importer = models.PositiveIntegerField(verbose_name="Quantite_total_site", help_text="Entrez_une_quantité_positive.", blank=True, null=True)
    Nombre_presonne_importer = models.ManyToManyField(CustomerUser, related_name='Nombre_presonne_importer')
    personne_en_charge_importer = models.ManyToManyField(CustomerUser, related_name='personne_en_charge_pour_importer')
    pourcentage_individuel_quantite_importer_importer = models.CharField(max_length=255, blank=True, null=True)
    statut_qte_importer_importer = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)

    # chargement des produits flyer
    quantite_flyers = models.PositiveIntegerField(verbose_name="Quantite_de_flyers ", help_text="Entrez une quantité positive.", blank=True, null=True)
    quantite_total_flyers = models.PositiveIntegerField(verbose_name="Quantite_total_de_flyers", help_text="Entrez une quantité positive.", blank=True, null=True)
    Nombre_presonne_flyers = models.ManyToManyField(CustomerUser, related_name='Nombre_presonne_flyers')
    personne_en_charge_flyers = models.ManyToManyField(CustomerUser, related_name='personne_en_charge_pour_flyers')
    pourcentage_individuel_quantite_importer_flyers = models.CharField(max_length=255, blank=True, null=True)
    statut_qte_importer_flyers = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)

    autre = tinymce_models.HTMLField(blank=True, null=True)

    @property
    def pourcentage_charge_sheet(self):
        if self.quantite_total_produit is not None and self.quantite_total_produit > 0:
            pourcentage = (self.quantite_produit or 0) * 100 / self.quantite_total_produit
            return int(pourcentage) if pourcentage <= 100 else None
        return None

    @property
    def pourcentage_quantite_importer(self):
        if self.quantite_total_importer is not None and self.quantite_total_importer > 0:
            pourcentage = (self.quantite_importer or 0) * 100 / self.quantite_total_importer
            return int(pourcentage) if pourcentage <= 100 else None
        return None

    @property
    def pourcentage_quantite_flyers(self):
        if self.quantite_flyers is not None and self.quantite_total_flyers is not None:
            if self.quantite_total_flyers > 0:
                pourcentage = (self.quantite_flyers or 0) * 100 / self.quantite_total_flyers
                return int(pourcentage) if pourcentage <= 100 else None
        return None

    @property
    def pourcentage_global1(self):
        pourcentages = [
            self.pourcentage_charge_sheet,
            self.pourcentage_quantite_importer,
            self.pourcentage_quantite_flyers,
        ]

        # Filtrer les pourcentages valides (non None et supérieurs à 0)
        valid_pourcentages = [p for p in pourcentages if p is not None and p > 0]

        total_pourcentages = sum(valid_pourcentages)
        count_valid = len(valid_pourcentages)

        if count_valid > 0:
            moyenne = total_pourcentages / count_valid
            return int(moyenne) if moyenne <= 100 else None  # Vérifie que la moyenne ne dépasse pas 100

        return None  # Retourner None si aucun pourcentage n'est valide



    @property
    def pourcentage_global_activite(self):
        subcomptoirs = self.subcomptoir_set.all()
        total_pourcentages = 0
        count_valid = 0

        for subcomptoir in subcomptoirs:
            pourcentage = subcomptoir.pourcentage_activite
            if pourcentage is not None and pourcentage > 0:  # Vérification de None
                total_pourcentages += pourcentage
                count_valid += 1

        if count_valid > 0:
            global_pourcentage = total_pourcentages / count_valid  # Utiliser la division flottante
            return int(
                global_pourcentage) if global_pourcentage <= 100 else None  # Vérifie que le pourcentage global ne dépasse pas 100

        return None  # Retourner None si aucun pourcentage n'est valide

    @property
    def pourcentage_total(self):
        pourcentage1 = self.pourcentage_global1
        pourcentage2 = self.pourcentage_global_activite

        # Filtrer les pourcentages valides (non None et supérieurs à 0)
        pourcentages = [p for p in [pourcentage1, pourcentage2] if p is not None and p > 0]

        if pourcentages:
            total_pourcentages = sum(pourcentages)
            count_valid = len(pourcentages)

            # Calculer la moyenne
            global_pourcentage = total_pourcentages / count_valid
            return int(
                global_pourcentage) if global_pourcentage <= 100 else None  # Vérifie que le total ne dépasse pas 100

        return None  # Retourner None si aucun pourcentage n'est valide






class SubComptoir(models.Model):
    STATUT_CHOICES = [
        ('Terminé', 'Terminé'),
        ('En Cours', 'En Cours'),
        ('En Pause', 'En Pause'),
        ('Risqué', 'Risqué'),
        ('Planifié', 'Planifié'),
    ]
    boncomptoir = models.ForeignKey(Boncomtoir, on_delete=models.CASCADE)
    activite = models.CharField(max_length=255, blank=True, null=True, verbose_name="Activité")
    quantite = models.PositiveIntegerField(verbose_name="Quantité", blank=True, null=True)
    quantite_total = models.PositiveIntegerField(verbose_name="Quantité_total", blank=True, null=True)
    personne_en_charge = models.ManyToManyField(CustomerUser, related_name='subcomptoir_personne_en_charge', blank=True, null=True)
    Nombre_de_personne = models.ManyToManyField(CustomerUser, related_name='subcomptoir_nombre_de_personne', blank=True, null=True)
    pourcentage_de_charge_individuel = models.CharField(max_length=255, blank=True, null=True)
    statut = models.CharField(max_length=255, choices=STATUT_CHOICES, blank=True, null=True)



    @property
    def pourcentage_activite(self):
        # Vérifier si quantite et quantite_total ne sont pas None
        if self.quantite is not None and self.quantite_total is not None:
            if self.quantite_total != 0:
                pourcentage = (self.quantite * 100) / self.quantite_total
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si quantite_total est 0


#--------------------------------------------------fin rubrique boncompoir----------------------------------------------------------/



#-------------------------------------service généraux------------------------------------------/

class Generaux(models.Model):
    titre = models.CharField(max_length=255)
    date = models.DateTimeField()
    description = tinymce_models.HTMLField()

#-------------------------------------service généraux------------------------------------------/

# fin rubrique technique

class Marqueting(models.Model):
    titre = models.CharField(max_length=255)
    date = models.DateTimeField(verbose_name="Date", help_text="Entrez la date.")
    # Nombre de rendez-vous
    Nombre_de_rendez_vous_objectifs = models.CharField(max_length=255)
    Nombre_de_rendez_vous_quantite_Objectifs = models.PositiveIntegerField( verbose_name="quantite_Objectifs",)
    Nombre_de_rendez_vous_Total_Objectifs = models.PositiveIntegerField( verbose_name="quantite_Objectifs",)
    Nombre_de_rendez_vous_acteur = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Activites = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Entreprises = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Particuliers = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Services = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Consommables = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Matériel_informatique = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Formation = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Statut = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Difficultés_rencontrees = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Nombre_de_rendez_vous_Actions_correctives = models.CharField(max_length=255)

    # Nombre de proposition commerciale
    Nombre_de_proposition_commerciale_objectifs = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_quantite_Objectifs = models.PositiveIntegerField(verbose_name="quantite_Objectifs_Nombre_de_proposition_commerciale", )
    Nombre_de_proposition_commercialele_Total_Objectifs = models.PositiveIntegerField(verbose_name="quantite_Objectifs_Nombre_de_proposition_commerciale", )
    Nombre_de_proposition_commercialele_acteur = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Activités = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Entreprises = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Particuliers = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Services = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Consommables = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Materiel_informatique = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Formation = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Statut = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Difficultes_rencontrees = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Nombre_de_proposition_commerciale_Actions_correctives = models.CharField(max_length=255)

    # Nombre de prospections
    Nombre_de_prospections_objectifs = models.CharField(max_length=255)
    Nombre_de_prospections_quantite_Objectifs = models.PositiveIntegerField( verbose_name="quantite_Objectifs_Nombre_de_prospections", )
    Nombre_de_prospectionsle_Total_Objectifs = models.PositiveIntegerField(verbose_name="total_Objectifs_Nombre_de_prospections", )
    Nombre_de_prospections_acteur = models.CharField(max_length=255)
    Nombre_de_prospections_Activites = models.CharField(max_length=255)
    Nombre_de_prospections_Entreprises = models.CharField(max_length=255)
    Nombre_de_prospections_Particuliers = models.CharField(max_length=255)
    Nombre_de_prospections_Services = models.CharField(max_length=255)
    Nombre_de_prospections_Consommables = models.CharField(max_length=255)
    Nombre_de_prospections_Materiel_informatique = models.CharField(max_length=255)
    Nombre_de_prospections_Formation = models.CharField(max_length=255)
    Nombre_de_prospections_Statut = models.CharField(max_length=255)
    Nombre_de_prospections_Difficultés_rencontrees = models.CharField(max_length=255)
    Nombre_de_prospections_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Nombre_de_prospections_Actions_correctives = models.CharField(max_length=255)

    # Relance
    Relance_objectifs = models.CharField(max_length=255)
    Relance_quantité_Objectifs = models.PositiveIntegerField(verbose_name="quantité_Objectifs_Relance", )
    Relancele_Total_Objectifs = models.PositiveIntegerField(verbose_name="total_Objectifs_Relance", blank=True,null=True, )
    Relance_acteur = models.CharField(max_length=255)
    Relance_Activités = models.CharField(max_length=255)
    Relance_Entreprises = models.CharField(max_length=255)
    Relance_Particuliers = models.CharField(max_length=255)
    Relance_Services = models.CharField(max_length=255)
    Relance_Consommables = models.CharField(max_length=255)
    Relance_Materiel_informatique = models.CharField(max_length=255)
    Relance_Formation = models.CharField(max_length=255)
    Relance_Statut = models.CharField(max_length=255)
    Relance_Difficultés_rencontrees = models.CharField(max_length=255)
    Relance_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Relance_Actions_correctives = models.CharField(max_length=255)

    # Nombre de devis élaborés
    Nombre_de_devis_elabores_objectifs = models.CharField(max_length=255)
    Nombre_de_devis_elabores_quantité_Objectifs = models.PositiveIntegerField(verbose_name="quantité_Objectifs_Nombre_de_devis_elabores", )
    Nombre_de_devis_elaboresle_Total_Objectifs = models.PositiveIntegerField(verbose_name="total_Objectifs_Nombre_de_devis_elabores", )
    Nombre_de_devis_elabores_acteur = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Activités = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Entreprises = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Particuliers = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Services = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Consommables = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Materiel_informatique = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Formation = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Statut = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Difficultés_rencontrees = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Nombre_de_devis_elabores_Actions_correctives = models.CharField(max_length=255)

    # Devis en attente
    Devis_en_attente_objectifs = models.CharField(max_length=255)
    Devis_en_attente_elabores_quantité_Objectifs = models.PositiveIntegerField(verbose_name="quantité_Objectifs_Devis_en_attente_elabores", )
    Devis_en_attente_elaboresle_Total_Objectifs = models.PositiveIntegerField(verbose_name="total_Objectifs_Devis_en_attente_elabores", )
    Devis_en_attente_elaboresle_acteur = models.CharField(max_length=255)
    Devis_en_attente_elabores_Activités = models.CharField(max_length=255)
    Devis_en_attente_elabores_Entreprises = models.CharField(max_length=255)
    Devis_en_attente_elabores_Particuliers = models.CharField(max_length=255)
    Devis_en_attente_elabores_Services = models.CharField(max_length=255)
    Devis_en_attente_elabores_Consommables = models.CharField(max_length=255)
    Devis_en_attente_elabores_Matériel_informatique = models.CharField(max_length=255)
    Devis_en_attente_elabores_Formation = models.CharField(max_length=255)
    Devis_en_attente_elabores_Statut = models.CharField(max_length=255)
    Devis_en_attente_elabores_Difficultés_rencontrees = models.CharField(max_length=255)
    Devis_en_attente_elabores_Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255)
    Devis_en_attente_elabores_Actions_correctives = models.CharField(max_length=255)

    autre = tinymce_models.HTMLField(blank=True, null=True)

    @property
    def pourcentage_Devis_en_attente_elabores(self):
        if self.Devis_en_attente_elabores_quantité_Objectifs is not None and self.Devis_en_attente_elaboresle_Total_Objectifs is not None:
            if self.Devis_en_attente_elaboresle_Total_Objectifs != 0:
                pourcentage = (self.Devis_en_attente_elabores_quantité_Objectifs * 100) / self.Devis_en_attente_elaboresle_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des quantités est None ou si le total est 0

    @property
    def pourcentage_Nombre_de_devis_elabores(self):
        # Vérifier si les quantités ne sont pas None
        if self.Nombre_de_devis_elabores_quantité_Objectifs is not None and self.Nombre_de_devis_elaboresle_Total_Objectifs is not None:
            if self.Nombre_de_devis_elaboresle_Total_Objectifs != 0:
                pourcentage = (self.Nombre_de_devis_elabores_quantité_Objectifs * 100) / self.Nombre_de_devis_elaboresle_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0

    @property
    def pourcentage_Relance(self):
        # Vérifier si les quantités ne sont pas None
        if self.Relance_quantité_Objectifs is not None and self.Relancele_Total_Objectifs is not None:
            if self.Relancele_Total_Objectifs != 0:
                pourcentage = (self.Relance_quantité_Objectifs * 100) / self.Relancele_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0


    @property
    def pourcentage_Nombre_de_rendez_vous(self):
        # Vérifier si les quantités ne sont pas None
        if self.Nombre_de_rendez_vous_quantite_Objectifs is not None and self.Nombre_de_rendez_vous_Total_Objectifs is not None:
            if self.Nombre_de_rendez_vous_Total_Objectifs != 0:
                pourcentage = (self.Nombre_de_rendez_vous_quantite_Objectifs * 100) / self.Nombre_de_rendez_vous_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0

    @property
    def pourcentage_Nombre_de_proposition_commerciale(self):
        # Vérifier si les quantités ne sont pas None
        if self.Nombre_de_proposition_commerciale_quantite_Objectifs is not None and self.Nombre_de_proposition_commercialele_Total_Objectifs is not None:
            if self.Nombre_de_proposition_commercialele_Total_Objectifs != 0:
                pourcentage = (self.Nombre_de_proposition_commerciale_quantite_Objectifs * 100) / self.Nombre_de_proposition_commercialele_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0

    @property
    def pourcentage_Nombre_de_prospections(self):
        # Vérifier si les quantités ne sont pas None
        if self.Nombre_de_prospections_quantite_Objectifs is not None and self.Nombre_de_prospectionsle_Total_Objectifs is not None:
            if self.Nombre_de_prospectionsle_Total_Objectifs != 0:
                pourcentage = (self.Nombre_de_prospections_quantite_Objectifs * 100) / self.Nombre_de_prospectionsle_Total_Objectifs
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0

    @property
    def pourcentage_global(self):
        pourcentages = [
            self.pourcentage_Devis_en_attente_elabores,
            self.pourcentage_Nombre_de_devis_elabores,
            self.pourcentage_Relance,
            self.pourcentage_Nombre_de_rendez_vous,
            self.pourcentage_Nombre_de_proposition_commerciale,
            self.pourcentage_Nombre_de_prospections
        ]

        # Récupérer les pourcentages des Variants liés
        variants_pourcentages = [variant.pourcentage for variant in self.variant_set.all() if
                                 variant.pourcentage is not None]

        # Ajouter les pourcentages des variantes à la liste
        pourcentages.extend(variants_pourcentages)

        # Filtrer les pourcentages valides (non nuls et non None)
        pourcentages_valides = [p for p in pourcentages if isinstance(p, int) and p > 0 and p <= 100]

        if pourcentages_valides:
            # Calculer la moyenne des pourcentages valides
            return int(sum(pourcentages_valides) / len(pourcentages_valides))  # Convertir en entier

        return 0  # Retourner 0 si aucune valeur valide




class Variant(models.Model):
    autre_un = models.CharField(max_length=255, blank=True, null=True)
    Marqueting = models.ForeignKey(Marqueting, on_delete=models.CASCADE)
    objectifs = models.CharField(max_length=255, blank=True, null=True)
    quantites = models.PositiveIntegerField(verbose_name="quantités", blank=True, null=True)
    Total = models.PositiveIntegerField(verbose_name="total", blank=True, null=True)
    acteur = models.CharField(max_length=255, blank=True, null=True)
    Activites = models.CharField(max_length=255, blank=True, null=True)
    Entreprises = models.CharField(max_length=255, blank=True, null=True)
    Particuliers = models.CharField(max_length=255, blank=True, null=True)
    Services = models.CharField(max_length=255, blank=True, null=True)
    Consommables = models.CharField(max_length=255, blank=True, null=True)
    materiel_informatique = models.CharField(max_length=255, blank=True, null=True)
    formation = models.CharField(max_length=255, blank=True, null=True)
    Statut = models.CharField(max_length=255, blank=True, null=True)
    Difficultes_rencontrees = models.CharField(max_length=255, blank=True, null=True)
    Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255, blank=True, null=True)
    Actions_correctives = models.CharField(max_length=255, blank=True, null=True)

    @property
    def pourcentage(self):
        if self.quantites is not None and self.Total is not None:
            if self.Total != 0:
                pourcentage = (self.quantites * 100) / self.Total
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0



#-------------------------------------rubrique technique----------------------------------------------------------/


class Technique(models.Model):
    titre = models.CharField(max_length=255)
    date = models.DateTimeField()
#------------activite externe---------------------------------------/
    clients_externe = models.CharField(max_length=255)
    action_externe = models.CharField(max_length=255)
    resultats_externe = models.CharField(max_length=255)
    remarque_externe = models.CharField(max_length=255)
    statuts_externe = models.CharField(max_length=255)
    paiement_externe = models.CharField(max_length=255)
    intervenant_externe = models.ManyToManyField(CustomerUser,  related_name='intervenant')
    # ------------interventions---------------------------------------/
    nombres_interventions_externe = models.PositiveIntegerField(verbose_name="nombres_interventions_externe")
    Intervention_en_attente_externe = models.PositiveIntegerField(verbose_name="Intervention_en_attente_externe")
    liste =models.CharField(max_length=255)
    Facturation_Paiement_externe = models.CharField(max_length=255, verbose_name="Facturation_Paiement", blank=True,null=True,)
    # ------------fin interventions---------------------------------------/
    champ_un = models.CharField(max_length=255, blank=True, null=True)
    champ_deux = models.CharField(max_length=255, blank=True, null=True)
    champ_trois = models.CharField(max_length=255, blank=True, null=True)
    champ_quatre = models.CharField(max_length=255, blank=True, null=True)
#------------activite interne---------------------------------------/
    clients_interne = models.CharField(max_length=255)
    action_interne = models.CharField(max_length=255)
    resultats_interne = models.CharField(max_length=255)
    remarque_interne = models.CharField(max_length=255)
    statuts_interne = models.CharField(max_length=255)
    paiement_interne = models.CharField(max_length=255)
    intervenant_interne = models.ManyToManyField(CustomerUser, related_name='intervenants')
# ------------activité---------------------------------------/
    Laptops_Entree = models.PositiveIntegerField(verbose_name="Laptops_Entrées")
    Laptop_en_Attente = models.PositiveIntegerField(verbose_name="Laptop_en_Attente")
    Facturation_Paiement = models.CharField(max_length=255, verbose_name="Facturation_Paiement", blank=True,null=True,)
    autre = tinymce_models.HTMLField(blank=True, null=True)

    #------------activite interne---------------------------------------/

    def Pourcentage_de_Realisation_interne(self):
        if self.nombres_interventions_externe > 0:
            pourcentage = (self.Intervention_en_attente_externe / self.nombres_interventions_externe) * 100
            return int(pourcentage) if pourcentage <= 100 else None  # Vérifie que le pourcentage ne dépasse pas 100
        return None  # Retourner None si le nombre d'interventions est 0 ou inférieur

    def Pourcentage_de_Realisation_externe(self):
        if self.Laptops_Entree > 0:
            pourcentage = (self.Laptop_en_Attente / self.Laptops_Entree) * 100
            return int(pourcentage) if pourcentage <= 100 else None  # Vérifie que le pourcentage ne dépasse pas 100
        return None  # Retourner None si le nombre de Laptops est 0 ou inférieur

    def Pourcentage_Total(self):
        pourcentage_interne = self.Pourcentage_de_Realisation_interne()
        pourcentage_externe = self.Pourcentage_de_Realisation_externe()

        # Filtrer les valeurs None et ne garder que celles qui sont valides
        valid_pourcentages = [p for p in [pourcentage_interne, pourcentage_externe] if p is not None]

        if valid_pourcentages:
            # Calculer le pourcentage total (moyenne simple)
            total = sum(valid_pourcentages) / len(valid_pourcentages)
            return int(total) if total <= 100 else None  # Vérifie que le total ne dépasse pas 100

        return None  # Retourner None si aucun pourcentage n'est valide





class Technique_ext(models.Model):
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE, related_name='activites_externes')
    ext_clients = models.CharField(max_length=255, blank=True, null=True)
    ext_action = models.CharField(max_length=255, blank=True, null=True)
    ext_resultats = models.CharField(max_length=255, blank=True, null=True)
    ext_remarque = models.CharField(max_length=255, blank=True, null=True)
    ext_statuts = models.CharField(max_length=255, blank=True, null=True)
    ext_paiement = models.CharField(max_length=255, blank=True, null=True)
    ext_intervenant = models.ManyToManyField(CustomerUser, blank=True, null=True, related_name='techniques_externes')


class Technique_int(models.Model):
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE, related_name='activites_internes')
    int_clients = models.CharField(max_length=255, blank=True, null=True)
    int_action = models.CharField(max_length=255, blank=True, null=True)
    int_resultats = models.CharField(max_length=255, blank=True, null=True)
    int_remarque = models.CharField(max_length=255, blank=True, null=True)
    int_statuts = models.CharField(max_length=255, blank=True, null=True)
    int_paiement = models.CharField(max_length=255, blank=True, null=True)
    int_intervenant = models.ManyToManyField(CustomerUser, blank=True, null=True, related_name='techniques_internes')



#-------------------------------------rubrique technique----------------------------------------------------------/



class Marketing(models.Model):
    titre = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(verbose_name="Date", help_text="Entrez la date.")
    autre = tinymce_models.HTMLField(blank=True, null=True)

    indicateur = models.CharField(max_length=255, blank=True, null=True)
    objectifs = models.CharField(max_length=255, blank=True, null=True)
    quantites = models.PositiveIntegerField(verbose_name="quantités", blank=True, null=True)
    Total = models.PositiveIntegerField(verbose_name="total", blank=True, null=True)
    acteur = models.CharField(max_length=255, blank=True, null=True)
    Activites = models.CharField(max_length=255, blank=True, null=True)
    Entreprises = models.CharField(max_length=255, blank=True, null=True)
    Particuliers = models.CharField(max_length=255, blank=True, null=True)
    Services = models.CharField(max_length=255, blank=True, null=True)
    Consommables = models.CharField(max_length=255, blank=True, null=True)
    materiel_informatique = models.CharField(max_length=255, blank=True, null=True)
    formation = models.CharField(max_length=255, blank=True, null=True)
    Statut = models.CharField(max_length=255, blank=True, null=True)
    Difficultes_rencontrees = models.CharField(max_length=255, blank=True, null=True)
    Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255, blank=True, null=True)
    Actions_correctives = models.CharField(max_length=255, blank=True, null=True)

    @property
    def pourcentage_1(self):
        if self.quantites is not None and self.Total is not None:
            if self.Total != 0:
                pourcentage = (self.quantites * 100) / self.Total
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des quantités est None ou si le total est 0

    @property
    def pourcentage_global(self):
        # Calculer les totaux et quantités des SubMarketing associés
        total_quantites_submarketing = sum(submarketing.quantites or 0 for submarketing in self.submarketing_set.all())
        total_total_submarketing = sum(submarketing.Total or 0 for submarketing in self.submarketing_set.all())

        # Total global de quantités et totaux
        total_quantites_global = (self.quantites or 0) + total_quantites_submarketing
        total_total_global = (self.Total or 0) + total_total_submarketing

        if total_total_global != 0:
            pourcentage_global = (total_quantites_global * 100) / total_total_global
            return int(
                pourcentage_global) if pourcentage_global <= 100 else 100  # Retourner un pourcentage global max de 100%
        return 0  # Retourner 0 si le total global est 0



class SubMarketing(models.Model):
    marketing = models.ForeignKey(Marketing, on_delete=models.CASCADE)
    indicateur = models.CharField(max_length=255, blank=True, null=True)
    objectifs = models.CharField(max_length=255, blank=True, null=True)
    quantites = models.PositiveIntegerField(verbose_name="quantités", blank=True, null=True)
    Total = models.PositiveIntegerField(verbose_name="total", blank=True, null=True)
    acteur = models.CharField(max_length=255, blank=True, null=True)
    Activites = models.CharField(max_length=255, blank=True, null=True)
    Entreprises = models.CharField(max_length=255, blank=True, null=True)
    Particuliers = models.CharField(max_length=255, blank=True, null=True)
    Services = models.CharField(max_length=255, blank=True, null=True)
    Consommables = models.CharField(max_length=255, blank=True, null=True)
    materiel_informatique = models.CharField(max_length=255, blank=True, null=True)
    formation = models.CharField(max_length=255, blank=True, null=True)
    Statut = models.CharField(max_length=255, blank=True, null=True)
    Difficultes_rencontrees = models.CharField(max_length=255, blank=True, null=True)
    Raisons_e_l_echec_de_l_objectif = models.CharField(max_length=255, blank=True, null=True)
    Actions_correctives = models.CharField(max_length=255, blank=True, null=True)

    @property
    def pourcentage_2(self):
        if self.quantites is not None and self.Total is not None:
            if self.Total != 0:
                pourcentage = (self.quantites * 100) / self.Total
                return int(pourcentage) if pourcentage <= 100 else None
        return None  # Retourner None si l'une des deux quantités est None ou si le total est 0



