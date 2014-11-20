import traceback
from django.http import HttpResponse

class PlainExceptionsMiddleware(object):
    def process_exception(self, request, exception):
        if "HTTP_USER_AGENT" in request.META and "chrome" in request.META["HTTP_USER_AGENT"].lower():
            return
        return HttpResponse(traceback.format_exc(exception), content_type="text/plain", status=500)

