from django.contrib import admin
from  .models import *


class UserLikeInline(admin.StackedInline):
    model = UserLike
    extra = 0
    fk_name = 'like_to'


class ProjectLikeInline(admin.StackedInline):
    model = ProjectLike
    extra = 0


class ProjectCommentInline(admin.StackedInline):
    model = ProjectComment
    extra = 0


class ProjectNewInline(admin.StackedInline):
    model = ProjectNew
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'investments', 'profit')
    list_display_links = ('id', 'title')
    list_filter = ('user__country', 'categories__name')


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserLikeInline, ProjectLikeInline, ProjectCommentInline, ProjectNewInline)
    list_display = ('id', 'email', 'last_name', 'first_name', 'country')
    list_display_links = ('id', 'email')
    exclude = ('password', 'last_login', 'groups', 'user_permissions',
                'is_superuser', 'is_active', 'is_staff', 'date_joined')


@admin.register(Callback)
class CallbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'last_name', 'first_name')
    list_display_links = ('id', 'email')


admin.site.register(Category)
admin.site.register(UserLike)
admin.site.register(ProjectLike)
admin.site.register(ProjectComment)
admin.site.register(ProjectNew)
admin.site.register(UserSubscribe)
admin.site.register(ProjectOffer)