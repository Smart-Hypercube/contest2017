from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=200)
    weight = models.FloatField()

    def __str__(self):
        return self.name


class Ticket(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.number)


class User(models.Model):
    group = models.ForeignKey(Group, models.PROTECT)
    ticket = models.ForeignKey(Ticket, models.CASCADE, unique=True)
    wechat = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.group) + '.' + str(self.ticket)


class Contest(models.Model):
    order = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.order) + '-' + self.name

    def prev(self):
        return Contest.objects.get(order=self.order-1)

    def next(self):
        return Contest.objects.get(order=self.order+1)


class Current(models.Model):
    contest = models.ForeignKey(Contest, models.PROTECT)


class School(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.number) + '-' + self.name


class Contestant(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    school = models.ForeignKey(School, models.CASCADE)

    def __str__(self):
        return str(self.number) + '-' + self.name


class Participate(models.Model):
    contestant1 = models.ForeignKey(Contestant, models.CASCADE, related_name='participate1_set', blank=True, null=True)
    contestant2 = models.ForeignKey(Contestant, models.CASCADE, related_name='participate2_set', blank=True, null=True)
    contest = models.ForeignKey(Contest, models.CASCADE)
    paid = models.BooleanField()
    result = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s, %s in %s' % (self.contestant1, self.contestant2, self.contest)

    def contestants(self):
        if self.contestant1 and self.contestant2:
            return '%s %s' % (self.contestant1, self.contestant2)
        elif self.contestant1:
            return str(self.contestant1)
        else:
            return str(self.contestant2)


class Vote(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    participate = models.ForeignKey(Participate, models.CASCADE)

    def __str__(self):
        return '%s for %s, %s in %s' % (self.user, self.participate.contestant1, self.participate.contestant2,
                                        self.participate.contest)
