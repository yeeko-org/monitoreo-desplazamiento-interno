from django.db import models

from pygooglenews import GoogleNews
import requests


class SearchQuery(models.Model):
    query = models.TextField()
    when = models.CharField(max_length=10, default='1d')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

    def save(self, *args, **kwargs):

        _save = super().save(*args, **kwargs)
        gn = GoogleNews("es", "MX")
        news = gn.search(self.query, helper=True, when=self.when)
        entries = news['entries']
        for entry in entries:
            source = entry.get("source", {}).get("href")

            link = Link.objects.create(
                query=self,
                gnews_url=entry.get("link"),
                title=entry.get("title"),
                description=entry.get("summary"),
                source=source
            )
            link.save()
        return _save


class Link(models.Model):
    query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='links')
    gnews_url = models.URLField(max_length=800)
    real_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.gnews_url[:30]

    def get_content(self):
        response = requests.get(self.gnews_url)
        if response.status_code == 200:
            if not self.real_url:
                self.real_url = response.url
                self.save()
            return response.content
        return None


class SourceMethod(models.Model):
    domain = models.CharField(max_length=200)
    title_tag = models.CharField(max_length=200)
    subtitle_tag = models.CharField(max_length=200)
    content_tag = models.TextField()

    def __str__(self):
        return self.domain

    def news_by_link(self, link: Link):
        from bs4 import BeautifulSoup
        link_content = link.get_content()
        if not link_content:
            return None
        soup = BeautifulSoup(link_content, 'html.parser')

        def get_text(tag, soup):
            tag_type = "class"
            if "=" in tag:
                tag_type = tag.split(":")[0]
                tag = tag.split(":")[1]
                tag = tag.replace('"', '').replace("'", "")

            if "id" in tag_type:
                find_kwargs = {"id": tag}
            else:
                find_kwargs = {"class_": tag}
            tags = soup.find_all(**find_kwargs)

            return " ".join([t.get_text(strip=True) for t in tags])

        title = get_text(self.title_tag, soup)
        subtitle = get_text(self.subtitle_tag, soup)
        content = get_text(self.content_tag, soup)

        news = News.objects.create(
            link=link,
            title=title,
            subtitle=subtitle,
            content=content,
            source_method=self
        )


class News(models.Model):
    link = models.ForeignKey(
        Link, on_delete=models.CASCADE, related_name='news')
    source_method = models.ForeignKey(
        SourceMethod, on_delete=models.CASCADE, related_name='news',
        null=True, blank=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
