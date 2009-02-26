from django.test import TestCase

import re
import urls
import gtdd.models as models


class RegexNotMatch(Exception):
    pass


class RegexMatch(Exception):
    pass


class URLTestCase(TestCase):
    def assert_match_url(self, url, patterns):
        for pattern in patterns:
            if pattern.regex.match(url):
                return
        raise RegexNotMatch(url)

    def assert_not_match_url(self, url, patterns):
        for i, pattern in enumerate(patterns):
            if pattern.regex.match(url):
                raise RegexMatch("%d: %s" % (i, url))


class PageUrlTest(URLTestCase):
    def test_page_url(self):
        self.assert_match_url("author", urls.pagepatterns)
        self.assert_match_url("import", urls.pagepatterns)
        self.assert_match_url("", urls.pagepatterns)
        self.assert_match_url("view/test/", urls.pagepatterns)
        self.assert_match_url("view/test_tab/test_page/", urls.pagepatterns)

    def test_page_url2(self):
        self.assert_not_match_url("author", urls.ajaxpatterns)
        self.assert_not_match_url("import", urls.ajaxpatterns)
        self.assert_not_match_url("", urls.ajaxpatterns)
        self.assert_not_match_url("view/test/", urls.ajaxpatterns)
        self.assert_not_match_url("view/test_tab/test_page/", urls.ajaxpatterns)


class AjaxUrlTest(URLTestCase):
    def test_ajax_url(self):
        self.assert_match_url("_tag_table/", urls.ajaxpatterns)
        self.assert_match_url("_table/", urls.ajaxpatterns)
        self.assert_match_url("view/test/_table/", urls.ajaxpatterns)
        self.assert_match_url("view/test_tab/test_page/_table/", urls.ajaxpatterns)
        self.assert_match_url("_datetime/", urls.ajaxpatterns)
        self.assert_match_url("view/test/_datetime/", urls.ajaxpatterns)
        self.assert_match_url("view/test_tab/test_page/_datetime/", urls.ajaxpatterns)

    def test_ajax_url2(self):
        self.assert_not_match_url("_tag_table", urls.pagepatterns)
        self.assert_not_match_url("_table", urls.pagepatterns)
        self.assert_not_match_url("view/test/_table/", urls.pagepatterns)
        self.assert_not_match_url("view/test_tab/test_page/_table/", urls.pagepatterns)
        self.assert_not_match_url("_datetime", urls.pagepatterns)
        self.assert_not_match_url("view/test/_datetime/", urls.pagepatterns)
        self.assert_not_match_url("view/test_tab/test_page/_datetime/", urls.pagepatterns)


class TaskCardTest(TestCase):
    def test_format_title(self):
        format_title = models.TaskCard._format_title
        self.assertEquals('abc', format_title("abc"))
        self.assertEquals('<a class="mail_link" href="mailto:abc@def.com">abc@def.com</a>',
            format_title("abc@def.com"))
        self.assertEquals('<a class="external_link" target="_blank" href="http://djangoproject.com">http://djangoproject.com</a>',
            format_title("http://djangoproject.com"))
        self.assertEquals('&lt;test&gt;', format_title('<test>'))

