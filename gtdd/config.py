import datetime

class TimeRange(object):
    pass

class OneDay(TimeRange):
    start = datetime.datetime.today()
    end = datetime.datetime.today() + datetime.timedelta(days=1, seconds=-1)
    @classmethod
    def default_range(cls):
        return [cls.start, cls.end]


class OneWeek(TimeRange):
    pass


class OneMonth(TimeRange):
    pass

class Tab(dict):
    def __init__(self, title, *views):
        kwargs={}
        kwargs["title"] = title
        kwargs["url"] = title.replace(" ", "_").lower()
        kwargs["views"] = views
        super(Tab, self).__init__(**kwargs)

    def html(self, base_url, active_tab_name):
        if self["url"] == active_tab_name:
            li_class = ' class="active"'
        else:
            li_class = ''
        title = self["title"]
        tab_url = self["url"]
        return '<li%(li_class)s><a href="%(base_url)s%(tab_url)s/" title="%(title)s">%(title)s</a></li>' % locals()

    def view_menu_html(self, base_url, active_view_name):
        return [view.html(base_url, self["url"], active_view_name) for view in self["views"]]


class View(dict):
    def __init__(self, title, **kwargs):
        kwargs["title"] = title
        kwargs["url"] = title.replace(" ", "_").lower()
        defaultkeys = "inbox,task,memo,someday_task,finished_card,calender"
        for key in defaultkeys.split(","):
            kwargs.setdefault("show_"+key, False)
        kwargs.setdefault("range", OneDay)
        super(View, self).__init__(**kwargs)

    def html(self, base_url, tab_url, active_view_name):
        title = self["title"]
        view_url = self["url"]
        if view_url == active_view_name:
            li_class = ' class="active"'
        else:
            li_class = ""
        return '<li%(li_class)s><a href="%(base_url)s%(tab_url)s/%(view_url)s/" title="%(title)s">%(title)s</a></li>' % locals()



tabs = [
  Tab("Action List",
    View("Action List",
         show_task=True),
    View("Memo",
         show_memo=True)
    ),
  Tab("Inbox",
    View("Inbox",
         show_inbox=True),
    View("Daily Review",
         show_inbox=True,
         range=OneWeek),
    View("Weekly Review",
         show_inbox=True,
         range=OneMonth),
    View("Someday",
         show_someday_task=True)
  ),
  Tab("Retrospect",
    View("Finished Task",
         show_memo=True,
         show_finished_card=True),
  )
]


def get_active_view(tab_name, view_name):
    if tab_name == "":
        return tabs[0], tabs[0]["views"][0]
    for tab in tabs:
        if tab["url"] == tab_name:
            if view_name == "":
                return tab, tab["views"][0]
            for view in tab["views"]:
                if view["url"] == view_name:
                    return tab, view


def get_tab_html(base_url, active_tab_name=None):
    return [tab.html(base_url, active_tab_name) for tab in tabs]

