from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from .models import Category, Product, SizeAttribute
from django.db.models import Q
from django.http import HttpResponse


class IndexView(TemplateView):
    template_name = "products/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "products/home_content.html", context)
        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    template_name = 'products/base.html'

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        'min_size': lambda queryset, value: queryset.filter(product_sizes__value__gte=value),
        'max_size': lambda queryset, value: queryset.filter(product_sizes__value__lte=value),
        'size_type': lambda queryset, value: queryset,
        'glaze_type': lambda queryset, value: queryset.filter(glaze_type=value)

    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        products = Product.objects.all().order_by("-created_at")
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        query = self.request.GET.get("q")
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query))

        filter_params = {}

        # Сохраняем все параметры фильтрации
        filter_params['color'] = self.request.GET.get('color', '')
        filter_params['glaze_type'] = self.request.GET.get('glaze_type', '')
        filter_params['size_type'] = self.request.GET.get('size_type', '')  # ЭТО КЛЮЧЕВОЕ
        filter_params['q'] = query or ''

        # Цена
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            try:
                filter_params['min_price'] = float(min_price)
                products = products.filter(price__gte=filter_params['min_price'])
            except ValueError:
                filter_params['min_price'] = ''
        else:
            filter_params['min_price'] = ''

        if max_price:
            try:
                filter_params['max_price'] = float(max_price)
                products = products.filter(price__lte=filter_params['max_price'])
            except ValueError:
                filter_params['max_price'] = ''
        else:
            filter_params['max_price'] = ''

        # Цвет
        if filter_params['color']:
            products = products.filter(color__iexact=filter_params['color'])

        # Глазурь
        if filter_params['glaze_type']:
            products = products.filter(glaze_type=filter_params['glaze_type'])

        # Размер: сохраняем значения, фильтруем только если есть size_type
        min_size = self.request.GET.get('min_size')
        max_size = self.request.GET.get('max_size')

        filter_params['min_size'] = min_size if min_size else ''
        filter_params['max_size'] = max_size if max_size else ''

        # ВАЖНО: проверяем наличие size_type перед фильтрацией
        if filter_params['size_type'] and (filter_params['min_size'] or filter_params['max_size']):
            size_filters = Q(product_sizes__size__attribute_type=filter_params['size_type'])
            if filter_params['min_size']:
                try:
                    size_filters &= Q(product_sizes__value__gte=float(filter_params['min_size']))
                except ValueError:
                    pass
            if filter_params['max_size']:
                try:
                    size_filters &= Q(product_sizes__value__lte=float(filter_params['max_size']))
                except ValueError:
                    pass
            products = products.filter(size_filters).distinct()

        # Убираем дублирование типов размеров
        unique_sizes = {}
        for size in SizeAttribute.objects.all():
            if size.attribute_type not in unique_sizes:
                unique_sizes[size.attribute_type] = size
        sizes = list(unique_sizes.values())

        context.update({
            'categories': categories,
            'products': products,
            'current_category': current_category,
            'filter_params': filter_params,  # Теперь здесь есть size_type
            'sizes': sizes,
            'glaze_choices': Product.GLAZE_CHOICES,
            'search_query': query or ''
        })

        if self.request.GET.get('show_search') == 'true':
            context["show_search"] = True
        elif self.request.GET.get('reset_search') == 'true':
            context["reset_search"] = True

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            if context.get('show_search'):
                if request.GET.get('mobile') == 'true':
                    return TemplateResponse(request, 'products/search_input_mobile.html', context)
                return TemplateResponse(request, 'products/search_input.html', context)
            elif context.get('reset_search'):
                # Возвращаем разные кнопки в зависимости от того, откуда пришёл запрос
                if request.GET.get('mobile') == 'true':
                    return TemplateResponse(request, 'products/mobile_search_button.html', {})
                return TemplateResponse(request, 'products/desktop_search_button.html', {})
            template = 'products/filter_modal.html' if request.GET.get('show_filters') == 'true' else 'products/catalog.html'
            return TemplateResponse(request, template, context)
        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/base.html'
    slug_field = "slug"
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        context['current_category'] = product.category
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'products/product_detail.html', context)
        return TemplateResponse(request, self.template_name, context)
