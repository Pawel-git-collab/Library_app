import uuid
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse



class Genre(models.Model):
    """Model reprezentujący gatunek książki."""
    name = models.CharField(max_length=200, help_text='Wprowadż gatunek ksiażki (np. Romans)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Book(models.Model):
    """Model reprezentujący Książke ale nie kopię książki"""

    title = models.CharField(max_length=200, verbose_name="Tytuł")

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True, verbose_name="Autor")

    summary = models.TextField(max_length=1000, help_text='Wprowadz krotki opis ksiazki', verbose_name="Opis książki")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 znakowy <a href="https://www.isbn-international.org/content/what-isbn">numer ISBN</a>')

    genre = models.ManyToManyField(Genre, help_text='Wybierz gatunek ksiazki.', verbose_name="Gatunek")

    language = models.ManyToManyField("Language", help_text='Wybierz język.', verbose_name="Język")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Gatunek'

    def display_language(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(language.name for language in self.language.all()[:3])

    display_language.short_description = 'Język'



class BookInstance(models.Model):
    """Model reprezentujący kopię książki która może być wypożyczona przeż użytkownika"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unikalne ID dla kazdej ksiazki w calej księgarni.')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, verbose_name="Tytuł książki")
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True, verbose_name="Wypożyczona do")
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Pożyczający")
    title = models.CharField(max_length=200, null=True, verbose_name="Tytuł") #dodałem tytuł do kopi ksiązki

    LOAN_STATUS = (
        ('m', 'W trakcie renowacji'), # m - maintenance
        ('o', 'Wypożyczona'), # o - on loan
        ('a', 'Dostępna'), # a - available
        ('r', 'Zarezerwowana'), # r - reserved
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Dostępność książki',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        # return f'{self.id} ({self.book.title})'

        return f'{self.id} ({self.title})' #zmiana na title

    # def get_absolute_url(self):
    #     return reverse('book-detail', args=[str(self.id)])

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True

        return False


class Language(models.Model):

    name = models.CharField(max_length=200, help_text='Wprowadż język (np. Polski)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Author(models.Model):

    first_name = models.CharField(max_length=100, help_text='Podaj imię autora książki')
    last_name = models.CharField(max_length=100, help_text='Podaj nazwisko autora książki')

    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Urodzony - ")
    date_of_death = models.DateField(null=True, blank=True, verbose_name="Zmarł - ")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])





