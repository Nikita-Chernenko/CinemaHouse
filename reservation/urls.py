from django.conf.urls import url

from reservation import views

urlpatterns=[
    url(r'get_reservation_by_session_id/(?P<session_id>[0-9]+)$', views.get_reservation_by_session_id, name ='get-reservation-by-session-id'),
    url(r'continue_reservation/(?P<reservation_seat_ids>([0-9,]*))/(?P<session_id>([0-9]+))$', views.continue_reservation, name='continue-reservation'),
]