
def categories(request):
    from auctions.models import Category
    return {'categories': Category.objects.all().order_by('category')}