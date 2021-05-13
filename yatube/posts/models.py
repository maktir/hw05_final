from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_not_empty


User = get_user_model()


class Post(models.Model):
    text = models.TextField(validators=[validate_not_empty])
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey('Group', on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(max_length=200,
                            validators=[validate_not_empty])
    created = models.DateTimeField('Дата публикации',
                                   auto_now_add=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')
