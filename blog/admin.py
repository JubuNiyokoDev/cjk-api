from django.contrib import admin
from .models import BlogPost, BlogImage, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 0

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'hashtags', 'external_link', 'author__username', 'category__name']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['author', 'category']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 25
    inlines = [BlogImageInline]

@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'post', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['caption', 'post__title']
    list_editable = ['order']
    autocomplete_fields = ['post']
    list_per_page = 25
