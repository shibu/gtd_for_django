from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.utils import simplejson

import re, cgi
import time, datetime
from gtd_site.gtdd import date


_type_list_keys = (
  "inbox", "memo", "calender", "deadline", "someday",
  "nextaction", "nextaction_week", "everyday", "sunday", "monday",
  "tuesday", "wednesday", "thursday", "friday", "saturday"
)

type_list = {}

for index, key in enumerate(_type_list_keys):
    type_list[key] = index
    type_list[index] = key

def get_user(request_or_str):
    if isinstance(request_or_str, basestring):
        try:
            return User.objects.get(username=request_or_str)
        except models.DoesNotExist:
            pass
    elif request_or_str is None:
        pass
    else:
        user = request_or_str.user
        if user.is_authenticated():
            return user
    user = authenticate(username='anonymous', password='anonymous')
    if user is None:
        user = User.objects.create_user('anonymous', 'x', 'anonymous')
        user.save()
    return user


class Tag(models.Model):
    title = models.CharField(max_length=200, blank=True)
    style = models.CharField(max_length=200, null=True)
    is_system = models.BooleanField()
    system_tags = {"book":"book.gif", "idea":"flair.gif", "home":"house.gif",
                   "company":"building.gif", "study":"pencil.gif",
                   "mail":"mail.gif", "tel":"mobilephone.gif",
                   "party":"wine.gif", "item":"bag.gif"}

    def __unicode__(self):
        if self.is_system:
            return '[*%s*]' % self.title
        return '[%s]' % self.title

    @classmethod
    def get_tag(cls, tag_title):
        if not tag_title:
            tag_title = ""
        try:
            return Tag.objects.get(title=tag_title)
        except ObjectDoesNotExist:
            if tag_title in cls.system_tags:
                cls.generate_system_tags()
                return Tag.objects.get(title=tag_title)
            tag = cls(title=tag_title, is_system=False, style="")
            tag.save()
            return tag

    def html(self):
        if self.is_system:
            title = '<img src="/static/icons/%s"/>' % self.style
            return '<span class="img_tag" tag_id="%d" tag_name="[%s]">%s</span>' % (
                self.id, self.title, title)
        else:
            title = '[%s]' % self.title
            return '<span class="text_tag" tag_id="%d" tag_name="[%s]">%s</span>' % (
                self.id, self.title, title)

    @classmethod
    def generate_system_tags(cls):
        for tag_title, icon in cls.system_tags.items():
            tag = cls(title=tag_title, is_system=True, style=icon)
            tag.save()


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_system']


# remove ()
_url_pattern = re.compile(r"(https?:\/\/[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)")
_mail_pattern = re.compile(r"([-\w\.+]+@(?:(?:[-a-zA-Z0-9]+\.)*[a-zA-Z]+|\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]))")

class TaskCard(models.Model):
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True)
    title = models.CharField(max_length=200, blank=True)
    data_type = models.IntegerField()
    start_date = models.DateTimeField(null=True, blank=True)
    target_date = models.DateTimeField(null=True, blank=True)
    finished_date = models.DateTimeField(null=True, blank=True)
    options = models.TextField(blank=True)

    class Meta:
        ordering = ["finished_date", "target_date"]

    def data_type_as_string(self):
        return type_list[self.data_type]

    def __unicode__(self):
        results = ["%s: " % type_list[self.data_type]]
        for tag in self.tags.all():
            results.append("[%s]" % unicode(tag))
        results.append(self.title)
        return "".join(results)

    @classmethod
    def create(cls, user, task_string):
        tasktypes = [Memo, SomedayTask, TaskOnCalender,
                    TaskWithDeadline, RepeatTask, InboxTask]
        for tasktype in tasktypes:
            task = tasktype.parse_from_input_str(user, task_string)
            if task:
                return task

    def is_repeat_task(self):
        return self.data_type > 6

    def change_to(self, dest):
        if not isinstance(dest, int):
            dest = type_list[dest]
        self.data_type = dest

    @classmethod
    def check(cls, task_id, is_check, is_doing):
        taskcard = cls.objects.get(id=task_id)
        if is_doing:
            taskcard.start_date = datetime.datetime.now()
            taskcard.finished_date = None
        elif is_check:
            if taskcard.is_repeat_task():
                record = TaskCard(title=taskcard.title, user=taskcard.user,
                    options=taskcard.options, start_date=taskcard.start_date,
                    target_date=taskcard.target_date,
                    data_type=type_list["nextaction"],
                    finished_date = datetime.datetime.now())
                record.save()
                for tag in taskcard.tags.all():
                    record.tags.add(tag)
                taskcard.start_date = None
                taskcard.target_date = date.next_dayofweek(
                    taskcard.data_type_as_string(),
                    taskcard.target_date)
            else:
                taskcard.finished_date = datetime.datetime.now()
        else:
            taskcard.finished_date = None
            taskcard.start_date = None
        taskcard.save()
        return "OK"

    @classmethod
    def edit(cls, command, items):
        if command == "Delete":
            cls.objects.filter(id__in=items).delete()
            return "Delete OK"
        elif command == "Memo":
            for task in cls.objects.filter(id__in=items):
                task.change_to("memo")
                task.finished_date = date.now()
                task.save()
            return "Memo OK"
        elif command == "Someday":
            for task in cls.objects.filter(id__in=items):
                task.change_to("someday")
                task.save()
            return "Someday OK"
        elif command in ("Today", "Tomorrow", "Next Week"):
            functions = {"Today":(date.today, "nextaction"),
                         "Tomorrow":(date.tomorrow, "nextaction"),
                         "Next Week":(date.next_week, "nextaction_week")}
            for task in cls.objects.filter(id__in=items):
                function, type = functions[command]
                task.change_to(type)
                task.target_date = function()
                task.save()
            return "%s OK" % command

    def image(self):
        if self.data_type == 0:
            return "cloud.gif"
        elif self.data_type == 1:
            return "clip.gif"
        elif self.data_type == 2:
            return "bell.gif"
        elif self.data_type == 3:
            return "clock.gif"
        elif self.data_type == 4:
            return "yacht.gif"
        elif self.data_type in [5, 6]:
            return "memo.gif"
        return "repeat_memo.gif"

    def check_box(self):
        if self.data_type not in [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            return ""
        if self.finished_date is not None:
            return '<img class="check_box checked" src="/static/icons/null.gif" />'
        elif self.start_date is not None:
            return '<img class="check_box doing" src="/static/icons/null.gif" />'
        return '<img class="check_box" src="/static/icons/null.gif" />'

    def format_date(self):
        if self.finished_date:
            if type_list[self.data_type] == "memo":
                return self.finished_date.strftime("%m/%d")
            return self.finished_date.strftime("%m/%d %H:%M")
        if self.target_date is None:
            return ""
        if self.target_date:
            unfinished = self.target_date < date.today()
        else:
            unfinished = False
        if type_list[self.data_type] == "nextaction_week":
            start, end = date.OneWeek.get(self.target_date)
            datestr = "%s - %s" % (start.strftime("%m/%d"), end.strftime("%m/%d"))
            unfinished = end < date.today()

        elif self.target_date.hour == 0 and self.target_date.minute == 0:
            datestr = self.target_date.strftime("%m/%d")
        else:
            datestr = self.target_date.strftime("%m/%d %H:%M")
        if unfinished:
            return '<span class="date unfinished">%s</span>' % datestr
        return '<span class="date">%s</span>' % datestr

    @classmethod
    def _format_title(self, title):
        import cgi
        title = _url_pattern.sub(
            r'<a class="external_link" target="_blank" href="\1"*>*\1</a>',
            title)
        title = _mail_pattern.sub(
            r'<a class="mail_link" href="mailto:\1"*>*\1</a>',
            title)
        title = cgi.escape(title)
        title = title.replace("&lt;a class=", "<a class=")
        title = title.replace("*&gt;*", ">")
        title = title.replace("&lt;/a&gt;", "</a>")
        return title

    def get_title(self):
        return self._format_title(self.title)

    def json(self, with_tag=True):
        from cgi import escape
        imagetag = '<img src="/static/icons/%s"/>' % self.image()
        tags = []
        if with_tag:
            tags = [tag.html() for tag in self.tags.all()]
        if tags:
            title = "%s %s" % (" ".join(tags), self.get_title())
        else:
            title = self.get_title()
        cell = [self.check_box(), imagetag, self.format_date(), title]
        return {"id":self.id, "cell":cell}


class TaskCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'show_user', 'show_tag', 'title', 'show_data_type', 'target_date', 'start_date', 'finished_date']
    list_filter = ['user', 'data_type']

    def show_tag(self, obj):
        return "[%s]" % obj.tag.title
    show_tag.short_description = 'Tag'

    def show_data_type(self, obj):
        return type_list[obj.data_type]
    show_data_type.short_description = 'Type'

    def show_user(self, obj):
        return obj.user.username
    show_user.short_description = 'User'


try:
    admin.site.register(Tag, TagAdmin)
    admin.site.register(TaskCard, TaskCardAdmin)
except AlreadyRegistered:
    pass # for test


class Entity(object):
    json_type = None
    title_pattern = re.compile("((?:\\[.+?\\])*)(.+)")
    @classmethod
    def create_taskcard(cls, user, title_str, target_date=None, finished_date=None, task_type=None):
        if not task_type:
            task_type = cls.json_type
        if task_type is None:
            raise NotImplementedError()
        title_match = cls.title_pattern.match(title_str)
        tag_list, title = title_match.groups()
        params = {"title":title, "data_type":type_list[task_type], "user":user}
        if target_date:
            params["target_date"] = target_date
        if finished_date:
            params["finished_date"] = finished_date
        task_card = TaskCard(**params)
        task_card.save()
        if len(tag_list) > 1:
            for tag_name in tag_list[1:-1].split("]["):
                task_card.tags.add(Tag.get_tag(tag_name))
        return task_card

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        raise NotImplementedError()

    @classmethod
    def create_date(cls, input_str, hour=0, minute=0):
        month = int(input_str[:2])
        day = int(input_str[2:])
        today = cls.create_today()
        result = datetime.datetime(today.year, month, day, hour, minute)
        if result < today:
            return datetime.datetime(today.year+1, month, day, hour, minute)
        return result

    @classmethod
    def create_time(cls, input_str):
        hour = int(input_str[:2])
        minute = int(input_str[2:])
        hour = min(23, hour)
        minute = min(59, minute)
        return hour, minute

    @classmethod
    def create_today(cls, hour=0, minute=0):
        today = datetime.date.today()
        return datetime.datetime(today.year, today.month, today.day, hour, minute)


class Memo(Entity):
    input_pattern = re.compile(">(.*)")
    json_type = "memo"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        if match:
            return cls.create_taskcard(user, match.group(1),
                                       finished_date=datetime.datetime.now())


class TaskOnCalender(Entity):
    input_pattern = re.compile("(?:(\\d{4})|@)(\\d{4}){0,1}(.*)")
    json_type = "calender"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        if not match:
            return
        if match.group(2) is None:
            hour, minute = 0, 0
        else:
            hour, minute = cls.create_time(match.group(2))
        if match.group(1) is None:
            date = cls.create_today(hour, minute)
        else:
            date = cls.create_date(match.group(1), hour, minute)
        return cls.create_taskcard(user, match.group(3), target_date = date)


class TaskWithDeadline(Entity):
    input_pattern = re.compile("\\.+(\\d{4})(.*)")
    json_type = "deadline"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        if not match:
            return
        date = cls.create_date(match.group(1))
        return cls.create_taskcard(user, match.group(2), target_date = date)


class SomedayTask(Entity):
    input_pattern = re.compile("#(.*)")
    json_type = "someday"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        if match:
            return cls.create_taskcard(user, match.group(1))


class InboxTask(Entity):
    input_pattern = re.compile("(.*)")
    json_type = "inbox"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        return cls.create_taskcard(user, match.group(1))


class NextActionTask(Entity):
    input_pattern = re.compile("<(.*)")
    json_type = "nextaction"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        date = cls.create_today()
        return cls.create_taskcard(user, match.group(1), target_date = date)


class RepeatTask(Entity):
    input_pattern = re.compile("\\*(su|mo|tu|we|th|fr|sa|):(.*)")
    json_type = "repeat"

    @classmethod
    def parse_from_input_str(cls, user, input_str):
        match = cls.input_pattern.match(input_str)
        if not match:
            return
        task_types = {"su":"sunday", "mo":"monday",
            "tu":"tuesday", "we":"wednesday", "th":"thursday",
            "fr":"friday", "sa":"saturday", "":"everyday"}
        task_type = task_types[match.group(1)]
        target_date = date.next_dayofweek(task_type)
        return cls.create_taskcard(user, match.group(2),
            target_date = target_date, task_type = task_type)


def _parse_date(date_str):
    import time
    if not date_str:
        return None
    date_str = date_str.split(".")[0]
    try:
        times = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")[0:6]
    except ValueError:
        return None
    return datetime.datetime(*times)


def import_data(import_data, mode, user):
    if mode == "all":
        TaskCard.objects.all().delete()
    elif mode == "user":
        TaskCard.objects.filter(user=user).delete()
    for entry in simplejson.loads(import_data):
        project = entry.get("project")
        if project:
            tags = [project]
        else:
            tags = entry.get("tag", [])
        title = entry.get("title")
        data_type = entry.get("type")
        start_date = _parse_date(entry.get("start_date"))
        target_date = _parse_date(entry.get("target_date"))
        finished_date = _parse_date(entry.get("finished_date"))
        user_name = entry.get("user")
        if user_name:
            entry_user = get_user(user_name)
        else:
            entry_user = user
        task = TaskCard(title=title, data_type=type_list[data_type],
                        target_date=target_date, start_date=start_date,
                        finished_date=finished_date, user=entry_user)
        task.save()
        for tag_title in tags:
            tag = Tag.get_tag(tag_title)
            task.tags.add(tag)


def export_data(mode, user):
    if mode == "all":
        query_set = TaskCard.objects.all()
    else:
        query_set = TaskCard.objects.filter(user=user)
    result = []
    for task in query_set:
        result.append({"title":task.title,
                       "tag":[tag.title for tag in task.tags.all()],
                       "target_date":str(task.target_date),
                       "start_date":str(task.start_date),
                       "finished_date":str(task.finished_date),
                       "type":type_list[task.data_type]})
    return simplejson.dumps(result, ensure_ascii=False, indent=2)
