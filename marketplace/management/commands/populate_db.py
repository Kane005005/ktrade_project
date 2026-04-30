from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from marketplace.models import Category, Product, Request
from faker import Faker
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de test'
    
    def handle(self, *args, **kwargs):
        fake = Faker()
        Faker.seed(0)
        random.seed(0)
        
        self.stdout.write('Création des catégories...')
        
        categories_data = [
            {'name': 'Électronique', 'icon': 'fa-laptop'},
            {'name': 'Textile & Mode', 'icon': 'fa-tshirt'},
            {'name': 'Alimentaire', 'icon': 'fa-apple-alt'},
            {'name': 'Agriculture', 'icon': 'fa-tractor'},
            {'name': 'Construction', 'icon': 'fa-hard-hat'},
            {'name': 'Médical', 'icon': 'fa-heartbeat'},
            {'name': 'Automobile', 'icon': 'fa-car'},
            {'name': 'Énergie', 'icon': 'fa-bolt'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': cat_data['name'].lower().replace(' ', '-'), 'icon': cat_data['icon']}
            )
            categories.append(category)
            self.stdout.write(f'  - {category.name} créée')
        
        self.stdout.write('Création des utilisateurs de test...')
        
        # Créer des fournisseurs
        suppliers = []
        for i in range(1, 6):
            username = f"fournisseur{i}"
            email = f"fournisseur{i}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                profile = user.profile
                profile.user_type = 'fournisseur'
                profile.phone = fake.phone_number()
                profile.country = fake.country()
                profile.city = fake.city()
                profile.company_name = fake.company()
                profile.bio = fake.text(max_nb_chars=200)
                profile.save()
                
                suppliers.append(user)
                self.stdout.write(f'  - Fournisseur {username} créé')
        
        # Créer des acheteurs
        buyers = []
        for i in range(1, 6):
            username = f"acheteur{i}"
            email = f"acheteur{i}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                profile = user.profile
                profile.user_type = 'vendeur'
                profile.phone = fake.phone_number()
                profile.country = fake.country()
                profile.city = fake.city()
                profile.bio = fake.text(max_nb_chars=200)
                profile.save()
                
                buyers.append(user)
                self.stdout.write(f'  - Acheteur {username} créé')
        
        self.stdout.write('Création des produits...')
        
        # Créer des produits
        for supplier in suppliers:
            for i in range(random.randint(3, 8)):
                product = Product.objects.create(
                    supplier=supplier,
                    name=fake.catch_phrase(),
                    category=random.choice(categories),
                    estimated_price=Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01')),
                    price_currency=random.choice(['USD', 'EUR', 'XOF']),
                    description=fake.text(max_nb_chars=500),
                    quantity_available=random.randint(10, 1000),
                    country_of_origin=fake.country(),
                )
                self.stdout.write(f'  - Produit {product.name} créé')
        
        self.stdout.write('Création des demandes...')
        
        # Créer des demandes
        for buyer in buyers:
            for i in range(random.randint(2, 5)):
                request_obj = Request.objects.create(
                    buyer=buyer,
                    product_name=fake.catch_phrase(),
                    category=random.choice(categories),
                    desired_quantity=random.randint(50, 5000),
                    desired_country=fake.country(),
                    description=fake.text(max_nb_chars=300),
                    max_budget=Decimal(random.uniform(100, 50000)).quantize(Decimal('0.01')),
                    budget_currency=random.choice(['USD', 'EUR', 'XOF']),
                )
                self.stdout.write(f'  - Demande {request_obj.product_name} créée')
        
        self.stdout.write(self.style.SUCCESS('Base de données peuplée avec succès!'))