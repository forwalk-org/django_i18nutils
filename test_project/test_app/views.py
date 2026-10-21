from django.shortcuts import render
from .forms import ProductForm

def product_form_view(request):
    """
    Vista di debug per testare il rendering e l'invio del ProductForm.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ProductForm()
    
    return render(request, 'test_app/product_form.html', {'form': form})
