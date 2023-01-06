from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('all_borrowed_books/', views.AllBooksBorrowed.as_view(), name='all-borrowed'),
    path('books_renew_librarian/<uuid:pk>', views.renew_book_librarian, name='book-renew-librarian'),
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/update/<int:pk>', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/update/<int:pk>', views.BookUpdate.as_view(), name='book_form'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
    path('all_borrowed_extend/', views.AllBooksBorrowedExtend.as_view(), name='all-borrowed-extend'),
    path('update_book/', views.AllBooksUpdateExtend.as_view(), name='all-books-update'),
    path('update_author/', views.AllAuthorsUpdateExtend.as_view(), name='all-authors-update'),
    path('confirm_get_book/', views.ConfirmBookListView.as_view(), name='confirm-get-book'),
    path('get_book_form/<uuid:pk>', views.confirm_get_book, name='get-book-form'),
    path('bookinstance/update/<int:pk>', views.BookInstanceCopy.as_view(), name='book_instance_form'),
    path('bookinstance/delete/<uuid:pk>&<int:book_pk>', views.BookInstanceDelete.as_view(), name='book_instance_delete'),
    path('reservation_book/<uuid:pk>', views.reservation_book, name='reservation-book'),
    path('rental_book/<uuid:pk>', views.rental_book, name='rental-book'),
    path(
        "activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="django_registration_activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        views.ActivationView.as_view(),
        name="django_registration_activate",
    ),
    path(
        "register/",
        views.RegistrationView.as_view(),
        name="django_registration_register",
    ),
    path(
        "register/complete/",
        TemplateView.as_view(
            template_name="django_registration/registration_complete.html"
        ),
        name="django_registration_complete",
    ),
    path(
        "register/closed/",
        TemplateView.as_view(
            template_name="django_registration/registration_closed.html"
        ),
        name="django_registration_disallowed",
    ),
    # path('registration_form', views.register_user, name='registration-form'),
]
