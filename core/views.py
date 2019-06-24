from django.http import HttpResponse
from rest_framework.views import APIView

from core.services import GoogleService



class RecieveEmailListView(APIView):
  def get(self, request):
    emails = GoogleService.get_emails(request)
    return HttpResponse(emails)

