import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
django.setup()

from test_app.models import Product

def run():
    print("Running migrations...")
    from django.core.management import call_command
    call_command('migrate', verbosity=0)

    print("Creating test product...")
    # Clean up
    Product.objects.all().delete()
    
    p = Product()
    p.name = {'en': 'Apple', 'it': 'Mela'}
    p.description = {'en': 'A fruit', 'it': 'Un frutto'}
    p.save()

    print(f"Product created: {p.name}")
    print(f"Product.objects type: {type(Product.objects)}")
    print(f"Product.objects manager class: {Product.objects.__class__}")
    print(f"Product MRO: {Product.mro()}")

    print("\nAttempting Product.objects.values('name')...")
    try:
        qs = Product.objects.values('name')
        print(f"Result: {list(qs)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nAttempting Product.objects.values('name_en', 'name_it')...")
    try:
        qs = Product.objects.values('name_en', 'name_it')
        print(f"Result: {list(qs)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
