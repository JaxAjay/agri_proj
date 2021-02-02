from django.db import models
from django.contrib.auth.models import User
# Create your models here.
import base64
from django.utils import timezone

class UserPost(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    text = models.TextField()
    image = models.FileField()
    date_created = models.DateTimeField(default=timezone.now , null=True)

    def __str__(self):
        return "%s - %s"%(self.user.username , self.text[:10])

    @property
    def serialize(self):
        image_str = ""
        if self.image:
            try:
                image_str =  base64.b64encode(self.image.read()).decode('utf-8')
            except:
                image_str = ""
        dic = {}
        dic['id'] = self.id
        dic['text'] = self.text
        dic['image'] = image_str
        dic['date_created'] = self.date_created.strftime("%m/%d/%Y, %H:%M:%S")
        dic['comments'] = [ comment.serialize for comment in self.comment_set.all()]
        dic['like_unlike'] = self.count_like_unlike()
        return dic

    def count_like_unlike(self):
        total = self.likeunlike_set.all()
        dic = {}
        dic['like'] = 0
        dic['unlike'] = 0
        dic['liked_by'] = []
        dic['unliked_by'] = []
        for i in total:
            if i.like_unlike:
                dic['like']+=1
                dic['liked_by'].append(i.user.username)
            if i.like_unlike == False:
                dic['unlike'] += 1
                dic['unliked_by'].append(i.user.username)
        
        return dic


class Comment(models.Model):
    post = models.ForeignKey(UserPost , on_delete=models.CASCADE)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(default=timezone.now , null=True)


    def __str__(self):
        return "%s - %s"%(self.user.username , self.text[:10])

    @property
    def serialize(self):
        dic = {}
        dic['id'] = self.id
        dic['comment'] = self.text
        dic['commented_by'] = self.user.username
        return dic

class LikeUnlike(models.Model):
    post = models.ForeignKey(UserPost , on_delete=models.CASCADE)
    like_unlike = models.BooleanField(null=True , blank=True)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['post' , 'user']
        
    def __str__(self):
        return "%s - %s"%(self.user.username , self.like_unlike)