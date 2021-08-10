from django.conf.urls import url
from . import views

urlpatterns = [
	#Authenticate to be taken out after testing /autneticate which has the custom claims
	url(r'^authenticate/',views.get_token, name='authenticate'),
	url(r'^register/$', views.register, name='register'),
	url(r'^forgotpassword/$', views.forgot_password, name='forgotpassword'),
	url(r'^changepassword/$', views.change_password, name='changepassword'),
	url(r'^cats/$', views.get_cats, name='cats'),
	url(r'^makebooking/$', views.make_booking, name='makebooking'),
	url(r'^getslots$', views.get_slots, name='getslots'),
	url(r'^getslotsformonth$', views.get_month, name='getslotsformonth'),
	url(r'^mybookings/$', views.my_slots, name='mybookings'),
	url(r'^deletebooking/$', views.delete_slot, name='deletebooking'),
	url(r'^getmenu$', views.get_menu, name='getmenu'),
	url(r'^contact$', views.contact, name='contact'),
]
