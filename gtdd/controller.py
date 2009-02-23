# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import django.utils
import django.utils.simplejson as json
import gtd_site.gtdd.models as models
from django.template import RequestContext
import views
from django.conf import settings


_base_url = settings.BASE_URL
_app_url = settings.APP_URL


def view_tasks(request, tab_name="", view_name=""):
    message = None
    if request.method == "POST":
        method = request.POST["method"]
        if method == "login":
            message = login(request)
        elif method == "logout":
            message = logout(request)
        elif method == "regist_task":
            return HttpResponse(add_task(request))
        elif method == "check":
            task_id = int(request.POST["id"][3:])
            is_checked = request.POST["is_check"] == "true"
            is_doing = request.POST["is_doing"] == "true"
            return HttpResponse(models.TaskCard.check(task_id, is_checked, is_doing))
        elif method == "edit":
            if not request.POST["target_items"]:
                return HttpResponse("No Target")
            command = request.POST["command"]
            items = [int(rowid[3:]) for rowid in request.POST["target_items"].split(",")]
            return HttpResponse(models.TaskCard.edit(command, items))
    base_url = _base_url
    app_url = _app_url

    tab, view = views.get_active_view(tab_name, view_name)
    tabs = views.get_tab_html(_base_url, tab.url)
    variables = views.get_variables(tab_name, view_name)
    view_menu_list = tab.view_menu_html(_base_url, view.url)
    tasks = []
    return render_to_response('index.html', locals(),
                              context_instance=RequestContext(request))


def ajax_task_table(request, tab_name="", view_name=""):
    date_query = request.POST.get("query", "")
    user = models.get_user(request)
    tasks = views.get_tasks(tab_name, view_name, user, date_query)
    json_obj = views.task_table(tasks, request)
    return HttpResponse(json.dumps(json_obj))


def ajax_tag_table(request, tag_id=None):
    if not tag_id:
        tag_id = int(request.POST.get("query"))
    tag = models.Tag.objects.get(id=tag_id)
    tasks = models.TaskCard.objects.filter(tags__pk=tag_id)
    page = int(request.POST.get("page", 1))
    total = tasks.count()
    rows = [task.json(with_tag=False) for task in tasks]
    result = {"page":page, "total":total, "rows":rows}
    return HttpResponse(json.dumps(result))


def ajax_datetime(request, task_id):
    if not task_id:
        task_id = request.POST.get("id")
    taskcard = models.TaskCard.objects.get(id=int(task_id))
    result = {}
    if taskcard.target_date is not None:
        result["target_date_flag"] = "checked"
        result["target_date"] = taskcard.target_date.strftime("%m/%d")
        result["target_time"] = taskcard.target_date.strftime("%H:%M")
    if taskcard.start_date is not None:
        result["start_date_flag"] = "checked"
        result["start_date"] = taskcard.start_date.strftime("%m/%d")
        result["start_time"] = taskcard.start_date.strftime("%H:%M")
    if taskcard.finished_date is not None:
        result["finished_date_flag"] = "checked"
        result["finished_date"] = taskcard.finished_date.strftime("%m/%d")
        result["finished_time"] = taskcard.finished_date.strftime("%H:%M")
    return HttpResponse(json.dumps(result))


def view_author(request):
    base_url = _base_url
    app_url = _app_url
    tabs = views.get_tab_html(_base_url)
    return render_to_response('author.html', locals(),
                              context_instance=RequestContext(request))


def view_import(request):
    base_url = _base_url
    app_url = _app_url
    tabs = views.get_tab_html(_base_url)
    message = None
    if not request.user.is_authenticated():
        export_data = ""
        return render_to_response('import.html', locals(),
                          context_instance=RequestContext(request))
    user = models.get_user(request)
    if request.method == "POST":
        method = request.POST["method"]
        if method == "login":
            message = login(request)
            user = models.get_user(request)
        elif method == "logout":
            message = logout(request)
            user = models.get_user("anonymous")
        elif method == "import":
            mode = request.POST["mode"]
            import_data = request.POST["import_data"]
            models.import_data(import_data, mode, user)
            return HttpResponse("Import successfully")
        elif method == "export":
            mode = request.POST["mode"]
            export_data = models.export_data(mode, user)
            return HttpResponse(export_data)
    export_data = models.export_data("json", user)
    return render_to_response('import.html', locals(),
                              context_instance=RequestContext(request))


def login(request):
    username = request.POST['user_id']
    password = request.POST['password']
    user = models.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            models.login(request, user)
            return "Welcome %s! Login successful." % username
        else:
            return "Disabled account"
    else:
        return "Invalid Login"


def logout(request):
    models.logout(request)
    return "Logout"


def add_task(request):
    task_string = request.POST["new_task"]
    user = models.get_user(request)
    taskcard = models.TaskCard.create(user, task_string)
    return "create ok: (%s) %s" % (taskcard.data_type_as_string(), taskcard.title)
