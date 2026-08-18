from django.contrib import admin
from .models import BlogPost, BlogImage, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 0

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content', 'hashtags']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BlogImageInline]
