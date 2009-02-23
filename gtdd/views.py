import copy
import gtd_site.gtdd.models as models
import django.utils.simplejson as json
from gtd_site.gtdd.date import OneDay, OneWeek, OneMonth
import gtd_site.gtdd.date as date

class Tab(object):
    def __init__(self, title, *views):
        self.title = title
        self.url = title.replace(" ", "_").lower()
        self.views = views

    def html(self, base_url, active_tab_name):
        if self.url == active_tab_name:
            li_class = ' class="active"'
        else:
            li_class = ''
        title = self.title
        tab_url = self.url
        return '<li%(li_class)s><a href="%(base_url)s%(tab_url)s/" title="%(title)s">%(title)s</a></li>' % locals()

    def view_menu_html(self, base_url, active_view_name):
        return [view.html(base_url, self.url, active_view_name) for view in self.views]


class View(object):
    def __init__(self, title, options, *query_sets):
        self.title = title
        self.url = title.replace(" ", "_").lower()
        self.query_sets = query_sets
        self.options = options

    def html(self, base_url, tab_url, active_view_name):
        title = self.title
        view_url = self.url
        if view_url == active_view_name:
            li_class = ' class="active"'
        else:
            li_class = ""
        return '<li%(li_class)s><a href="%(base_url)s%(tab_url)s/%(view_url)s/" title="%(title)s">%(title)s</a></li>' % locals()

    def query_task(self, user, date_query):
        user_cards = models.TaskCard.objects.filter(user=user)
        query = None
        for query_set in self.query_sets:
            if query is None:
                query = query_set.do(date_query)
            else:
                query = query | query_set.do(date_query)
        if query is not None:
            return user_cards.filter(query)
        else:
            return user_cards

class QuerySet(object):
    def __init__(self, **options):
        defaultkeys = "inbox,task,memo,someday_task,finished_card,unfinished_card,calender,nextaction,doing"
        for key in defaultkeys.split(","):
            options.setdefault("show_"+key, False)
        self.options = options

    def do_next_action(self, date_query):
        day_kwargs = {"data_type__in":[5, 7, 8, 9, 10, 11, 12, 13, 14]}
        week_kwargs = {"data_type":models.type_list["nextaction_week"]}
        Q = models.models.Q
        view_range = self.options.get("view_range")
        show_finished = self.options["show_finished_card"]
        show_unfinished = self.options["show_unfinished_card"]
        if not view_range:
            if show_unfinished:
                day_kwargs.setdefault("target_date__lt", date.today())
                day_kwargs.setdefault("finished_date__isnull", True)
                week_kwargs.setdefault("target_date__lt", date.next_week())
                week_kwargs.setdefault("finished_date__isnull", True)
            elif not show_finished:
                day_kwargs.setdefault("finished_date__isnull", True)
                week_kwargs.setdefault("finished_date__isnull", True)
            return Q(**day_kwargs) | Q(**week_kwargs)

        view_start, view_end = view_range.get(date_query)
        week_view_start, week_view_end = view_range.get_week(date_query)
        if show_unfinished:
            day_kwargs["target_date__lt"] = view_start
            day_kwargs["finished_date__isnull"] = True
            week_kwargs["target_date__lt"] = week_view_end
            week_kwargs["finished_date__isnull"] = True
            return Q(**day_kwargs) | Q(**week_kwargs)
        else:
            day_kwargs["target_date__range"] = [view_start, view_end]
            week_kwargs["target_date__range"] = [week_view_start, week_view_end]
            if not show_finished:
                day_kwargs["finished_date__isnull"] = True
                week_kwargs["finished_date__isnull"] = True
            return Q(**day_kwargs) | Q(**week_kwargs)


    def do(self, date_query):
        kwargs = {}
        Q = models.models.Q
        if self.options["show_nextaction"]:
            return self.do_next_action(date_query)
        elif self.options["show_inbox"]:
            kwargs["data_type"] = models.type_list["inbox"]
        elif self.options["show_task"]:
            kwargs["data_type"] = models.type_list["calender"]
        elif self.options["show_memo"]:
            kwargs["data_type"] = models.type_list["memo"]
            kwargs["finished_date__isnull"] = False
        elif self.options["show_someday_task"]:
            kwargs["data_type"] = models.type_list["someday"]
        view_range = self.options.get("view_range")
        show_finished = self.options["show_finished_card"]
        show_unfinished = self.options["show_unfinished_card"]
        show_doing = self.options["show_doing"]
        if not view_range:
            if show_doing:
                    kwargs.setdefault("finished_date__isnull", True)
                    kwargs.setdefault("start_date__isnull", False)
            else:
                if show_unfinished:
                    kwargs.setdefault("target_date__lt", date.today())
                    kwargs.setdefault("finished_date__isnull", True)
                elif not show_finished:
                    kwargs.setdefault("finished_date__isnull", True)
            return Q(**kwargs)

        view_start, view_end = view_range.get(date_query)
        if show_unfinished:
            kwargs["target_date__lt"] = view_start
            kwargs["finished_date__isnull"] = True
            return Q(**kwargs)
        else:
            kwargs["target_date__range"] = [view_start, view_end]
            if not show_finished:
                kwargs["finished_date__isnull"] = True
            return Q(**kwargs)


tabs = [
  Tab("Action List",
    View("Next Action",
         dict(defer_tomorrow=True, change_to_memo=True,
              do_today=True, defer_next_week=True),
         QuerySet(show_task=True, view_range=OneDay),
         QuerySet(show_task=True, view_range=OneDay, show_unfinished_card=True),
         QuerySet(show_nextaction=True, view_range=OneDay),
         QuerySet(show_nextaction=True, view_range=OneDay, show_unfinished_card=True)),
    View("Doing", dict(),
         QuerySet(show_doing=True)),
    View("Memo", dict(),
         QuerySet(show_memo=True))
  ),
  Tab("Inbox",
    View("Inbox",
         dict(do_today=True, defer_tomorrow=True, defer_next_week=True,
              change_to_memo=True, do_someday=True),
         QuerySet(show_inbox=True)),
    View("Daily Review",
         dict(do_today=True, defer_tomorrow=True, defer_next_week=True),
         QuerySet(show_task=True, view_range=OneWeek),
         QuerySet(show_task=True, show_unfinished_card=True),
         QuerySet(show_nextaction=True, view_range=OneWeek),
         QuerySet(show_nextaction=True, view_range=OneWeek, show_unfinished_card=True)),
    View("Weekly Review",
         dict(do_today=True, do_someday=True, defer_next_week=True),
         QuerySet(show_task=True, view_range=OneMonth),
         QuerySet(show_task=True, show_unfinished_card=True),
         QuerySet(show_nextaction=True),
         QuerySet(show_nextaction=True, show_unfinished_card=True)),
    View("Someday",
         dict(do_today=True, change_to_memo=True),
         QuerySet(show_someday_task=True)),
  ),
  Tab("Retrospect",
    View("Finished Task", dict(show_calender=True),
         QuerySet(show_memo=True, view_range=OneDay),
         QuerySet(show_task=True, view_range=OneDay, show_finished_card=True))
  )
]

def sort_and_paging(items, request, sortkey):
    page = int(request.POST.get("page", 1))
    rp = int(request.POST.get("rp", 10))
    total = items.count()
    start = (page-1)*rp
    end = min(page*rp, total)
    if request.POST.get("sortorder", "desc") == "desc":
        sortkey = "-%s" % sortkey
    return items.order_by(sortkey)[start:end]


def sort_and_paging_tasks(tasks, request):
    sortkeys = {"title":"title", "date":"target_date", "icon":"data_type"}
    sortkey = sortkeys.get(request.POST.get("sortname", "date"), "target_date")
    return sort_and_paging(tasks, request, sortkey)


def task_table(tasks, request):
    page = int(request.POST.get("page", 1))
    total = tasks.count()
    tasks = sort_and_paging_tasks(tasks, request)
    rows = [task.json() for task in tasks]
    return {"page":page, "total":total, "rows":rows}


def get_active_view(tab_name, view_name):
    if tab_name == "":
        return tabs[0], tabs[0].views[0]
    for tab in tabs:
        if tab.url == tab_name:
            if view_name == "":
                return tab, tab.views[0]
            for view in tab.views:
                if view.url == view_name:
                    return tab, view
    raise ValueError("Not Found %s/%s" % (tab_name, view_name))


def get_tab_html(base_url, active_tab_name=None):
    return [tab.html(base_url, active_tab_name) for tab in tabs]


def get_tasks(tab_name, view_name, user, date_query):
    view = get_active_view(tab_name, view_name)[1]
    return view.query_task(user, date_query)


def get_variables(active_tab_name=None, view_name=None):
    variables = []
    tab, view = get_active_view(active_tab_name, view_name)
    variables = json.dumps(view.options)
    return 'var options = %s;' % variables
