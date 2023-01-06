from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from .models import Book, BookInstance, Author, Genre
from django.views import generic, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import ConfirmGetBook, RenewBookForm, ReversationBookForm, BookInstanceForm

import datetime

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_registration import signals
from django_registration.exceptions import ActivationError
from django_registration.views import ActivationView as BaseActivationView
from django_registration.views import RegistrationView as BaseRegistrationView

REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Dostępne książki (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # # Funkcja 'all()' jest wykonywana domyślnie nawet jak nie jest stricte wywoływana.
    num_authors = Author.objects.count()  # to samo co -> Author.objects.all().count()

    num_genre = Genre.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre
    }

    # Przekazywanie do wzorca html danych przy pomocy zmiennej context
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = 'book_list.html'

    def get_context_data(self, **kwargs):
        # Wywołanie funkcji super poznanej juz wcześniej
        context = super(BookListView, self).get_context_data(**kwargs)
        # Stworzenie danych i zapisanie ich do contextu
        context['some_data'] = 'Pozdrawiamy wszystkich nauczycieli języka python:)'  # przykladowa wartosc
        return context

    def get_queryset(self):
        return Book.objects.all()
        # return Book.objects.all()[:5] pokazuje tylko 5 ksiazek


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'author_list.html'
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    template_name = 'book_detail.html'


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class MyView(PermissionRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')


class AllBooksBorrowed(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    template_name = 'bookinstance_list_borrowed.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class AllBooksBorrowedExtend(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'all_borrowed_extend.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        # return BookInstance.objects.filter(status__exact='o').order_by('due_back') - wszystkie wypozyczone


# @permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    # zwraca obiekt z modelu o zadanych parametrów lub zgłasza błąd typu 404 not found
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Jeśli typ zapytania to POST
    if request.method == 'POST':

        # Stworzenie instancji formularza i wstrzykniecie jej danych z zapytania POST
        form = RenewBookForm(request.POST)

        # Sprawdzenie czy dane w formularzu są poprawne
        if form.is_valid():
            # pobranie renewal_date z wyczyszczonych danych z formualrza i zapisanie ich do modelu do
            # atrybutu due_back
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # przekierowanie do URL wszystkich moich wypozyczonych książek co oczywiscie zawsze można zmienic
            return HttpResponseRedirect(reverse('my-borrowed'))

    # Jeśli to zapytanie GET lub każde inne to uzyc domyślnego formularza
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    # Stworzenie contextu w formie słownika który zostanie przekazany do pliku HTML
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    # Przekazanie danych, i zapytania do pliku HTML
    return render(request, 'book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': ''}
    template_name = 'author_form.html'


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'author_form.html'


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'author_confirm_delete.html'


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    template_name = 'book_form.html'


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    template_name = 'book_form.html'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'book_confirm_delete.html'


class AllBooksUpdateExtend(generic.ListView):
    model = Book
    template_name = 'update_book.html'


class AllAuthorsUpdateExtend(generic.ListView):
    model = Author
    template_name = 'update_author.html'


def confirm_get_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = ConfirmGetBook(request.POST)

        if form.is_valid():
            book_instance.status = form.cleaned_data['status']
            book_instance.save()

            return HttpResponseRedirect(reverse('my-borrowed'))

    else:
        form = ConfirmGetBook()

    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'get_book_form.html', context)


class ConfirmBookListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'confirm_get_book.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class RegistrationView(BaseRegistrationView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """

    email_body_template = "django_registration/activation_email_body.txt"
    email_subject_template = "django_registration/activation_email_subject.txt"
    success_url = reverse_lazy("django_registration_complete")

    def register(self, form):
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=self.request
        )
        return new_user

    def create_inactive_user(self, form):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(obj=user.get_username(), salt=REGISTRATION_SALT)

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        scheme = "https" if self.request.is_secure() else "http"
        return {
            "scheme": scheme,
            "activation_key": activation_key,
            "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
            "site": get_current_site(self.request),
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is the username,
        signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context["user"] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request,
        )
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = "".join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request,
        )
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class ActivationView(BaseActivationView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """

    ALREADY_ACTIVATED_MESSAGE = (
        "The account you tried to activate has already been activated."
    )
    BAD_USERNAME_MESSAGE = "The account you attempted to activate is invalid."
    EXPIRED_MESSAGE = "This account has expired."
    INVALID_KEY_MESSAGE = "The activation key you provided is invalid."
    success_url = reverse_lazy("django_registration_activation_complete")

    def activate(self, *args, **kwargs):
        username = self.validate_key(kwargs.get("activation_key"))
        user = self.get_user(username)
        user.is_active = True
        user.save()
        return user

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or raising ``ActivationError`` if not.
        """
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400,
            )
            return username
        except signing.SignatureExpired:
            raise ActivationError(self.EXPIRED_MESSAGE, code="expired")
        except signing.BadSignature:
            raise ActivationError(
                self.INVALID_KEY_MESSAGE,
                code="invalid_key",
                params={"activation_key": activation_key},
            )

    def get_user(self, username):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or raising
        ``ActivationError`` if it doesn't.
        """
        User = get_user_model()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
            if user.is_active:
                raise ActivationError(
                    self.ALREADY_ACTIVATED_MESSAGE, code="already_activated"
                )
            return user
        except User.DoesNotExist:
            raise ActivationError(self.BAD_USERNAME_MESSAGE, code="bad_username")


class BookInstanceCopy(CreateView, PermissionRequiredMixin):
    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    fields = ["id", 'book', 'imprint', 'status']
    success_url = reverse_lazy('books')
    template_name = 'book_instance_form.html'

    def get_initial(self):
        self.book = Book.objects.get(pk=self.kwargs.get('pk'))
        return {'book': self.book}


# class BookInstanceListView(generic.DetailView):
#     model = Book
#     template_name = 'book_instance_create.html'

class BookInstanceDelete(DeleteView, PermissionRequiredMixin):
    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    template_name = 'book_instance_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('book-detail', kwargs={'pk': self.kwargs.get('book_pk')})


def reservation_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = ReversationBookForm(request.POST)

        if form.is_valid():
            book_instance.status = form.cleaned_data['status']
            book_instance.save()

            return HttpResponseRedirect(reverse('books'))

    else:
        form = ReversationBookForm()

    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'reservation_book_form.html', context)


def rental_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = BookInstanceForm(request.POST,
                                initial={'wypożyczona_do': proposed_renewal_date, 'borrower': request.user})

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['wypożyczona_do']
            book_instance.status = form.cleaned_data['status']
            book_instance.borrower = form.cleaned_data['borrower']
            book_instance.save()

            return HttpResponseRedirect(reverse('my-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = BookInstanceForm(initial={'wypożyczona_do': proposed_renewal_date, 'borrower': request.user})

    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'rental_book_form.html', context)
