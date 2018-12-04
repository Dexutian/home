from django.contrib import admin
from .models import Book, Author, Friendship, Person, Group, Membership


# Register your models here.
class BookInline(admin.TabularInline):
    model = Book


class AuthorAdmin(admin.ModelAdmin):
    inlines = [
        BookInline,
    ]

    list_display = ['id', 'name']


class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author']


class FriendshipInline(admin.TabularInline):
    model = Friendship
    fk_name = "to_person"


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


class PersonAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)

    list_display = ['first_name', 'last_name']


class GroupAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)

    filter_horizontal = ['members']


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdmin)