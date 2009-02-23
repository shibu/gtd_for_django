# -*- encoding: utf-8 -*-

from django.conf import settings

analog = """<div style="position:absolute;top:0;right:0;color:#fff;filter:alpha(opacity=50);opacity:0.5;font-size:1.5em;font-weight:900;">アナログ</div></body>"""

class AnalogMiddleware(object):
   def __init__(self):
       self.is_show = settings.DEBUG

   def process_response(self, request, response):
       if not self.is_show:
           return response
       if "text/html" in response["Content-Type"]:
           response.content = response.content.replace("</body>", analog)
       return response
