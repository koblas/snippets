import uuid
from datetime import datetime
from ..auth.models import User
from mongoengine import Document, EmbeddedDocument
from mongoengine import StringField, DateTimeField, ReferenceField, ListField, IntField, EmbeddedDocumentField
from markdown import markdown

class Tag(Document):
    lc_name        = StringField(unique=True, max_length=100)
    name           = StringField(unique=True, max_length=100)

    def get_absolute_url(self):
        return "/tags/%s" % self.name

class Comment(EmbeddedDocument):
    author            = ReferenceField(User)
    content           = StringField(required=True)
    pub_date          = DateTimeField(default=datetime.now)

class Snippet(Document):
    guid              = StringField(required=True, default=lambda:str(uuid.uuid4()))
    title             = StringField(max_length=255)
    author            = ReferenceField(User)
    description       = StringField()
    description_html  = StringField()
    code              = StringField()
    pub_date          = DateTimeField(default=datetime.now)
    updated_date      = DateTimeField(default=datetime.now)

    vote_count        = IntField(default=0) # denormalized count
    views             = IntField(default=0) # denormaliazed score
    
    tags              = ListField(ReferenceField(Tag))
    comments          = ListField(EmbeddedDocumentField(Comment))
    
    class Meta:
        ordering = ('-pub_date',)
        
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.description_html = markdown(self.description, safe_mode="escape")
        self.updated_date     = datetime.now()
        super(Snippet, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        return "/snippets/%s" % self.guid
        
    def get_tagstring(self):
        return ", ".join([t.name for t in self.tags])
    
    def update_rating(self):
        self.rating_score = self.ratings.cumulative_score() or 0
        self.save()
    
    def update_bookmark_count(self):
        self.bookmark_count = self.bookmarks.count() or 0
        self.save()

    def increment_views(self):
        Snippet.objects(id=self.id).update_one(inc__views=1);

    def update_vote_count(self):
        self.vote_count = sum([obj.value for obj in Vote.objects(snippet=self)])
        self.save()

SNIPPET_FLAG_SPAM = 1
SNIPPET_FLAG_INAPPROPRIATE = 2
SNIPPET_FLAG_CHOICES = (
    (SNIPPET_FLAG_SPAM, 'Spam'),
    (SNIPPET_FLAG_INAPPROPRIATE, 'Inappropriate'),
)

class SnippetFlag(Document):
    snippet = ReferenceField(Snippet)  # , related_name='flags')
    user    = ReferenceField(User)
    flag    = IntField(choices=SNIPPET_FLAG_CHOICES)
    
    def __unicode__(self):
        return '%s flagged as %s by %s' % (
            self.snippet.title,
            self.get_flag_display(),
            self.user.username,
        )
    
    def remove_and_ban(self):
        user = self.snippet.author
        user.set_unusable_password()
        user.is_active = False
        user.save()
        self.snippet.delete()

class Vote(Document):
    user              = ReferenceField(User)
    snippet           = ReferenceField(Snippet)
    value             = IntField(default=1)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.snippet.update_vote_count()

    def delete(self, *args, **kwargs):
        super(Vote, self).delete(*args, **kwargs)
        self.snippet.update_vote_count()


class Bookmark(Document):
    snippet = ReferenceField(Snippet) #, related_name='bookmarks')
    user    = ReferenceField(User) # , related_name='cab_bookmarks')
    date    = DateTimeField(default=datetime.now)
    
    # TODO -
    class Meta:
        ordering = ('-date',)
    
    def __unicode__(self):
        return "%s bookmarked by %s" % (self.snippet, self.user)
    
    def save(self, *args, **kwargs):
        super(Bookmark, self).save(*args, **kwargs)
        self.snippet.update_bookmark_count()
    
    def delete(self, *args, **kwargs):
        super(Bookmark, self).delete(*args, **kwargs)
        self.snippet.update_bookmark_count()
