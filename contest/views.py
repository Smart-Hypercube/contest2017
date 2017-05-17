from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import User, Ticket, Group, Current, Contest

import bs4


def query(request):
    return render(request, 'contest/query.html', {'contests': Contest.objects.all()})


def get_number(s):
    return ''.join(filter(str.isdigit, s))


def subscribe(request, data):
    return render(request, 'contest/reply.xml', {'from': 'from', 'to': 'to', 'content': 'content'})


def login(request, msg):
    ticket = get_number(msg['content'])
    if ticket == 0:
        context = {'msg': msg,
                   'current': Current.objects.get().contest}
        return render(request, 'contest/base.xml', context)
    if len(ticket) != 6 or len(ticket) + 10 < len(msg['content']):
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': False,
                   'reason': 0}
        return render(request, 'contest/login.xml', context)
    try:
        user = User(group=Group.objects.get(name='audience'),
                    ticket=Ticket.objects.get(number=ticket),
                    wechat=msg['from'])
        user.save()
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': True}
        return render(request, 'contest/login.xml', context)
    except ObjectDoesNotExist:
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': False,
                   'reason': 1}
        return render(request, 'contest/login.xml', context)
    except ValidationError:
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': False,
                   'reason': 2}
        return render(request, 'contest/login.xml', context)


def text(request, msg, user):
    input = get_number(msg['content'])
    if input == 0:
        context = {'msg': msg,
                   'current': Current.objects.get().contest}
        return render(request, 'contest/base.xml', context)
    current = Current.objects.get().contest
    if len(ticket) != 4 or len(ticket) + 10 < len(msg['content']):
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': False,
                   'reason': 0}
        return render(request, 'contest/vote.xml', context)
    try:
        current.participate_set.get(contestant1__number=input)
    except ObjectDoesNotExist:
        pass


def admin(request, msg, user):
    pass


@csrf_exempt
@require_http_methods(['HEAD', 'GET', 'POST'])
def webhook(request):
    if request.method == 'POST':
        data = bs4.BeautifulSoup(request.body, 'html.parser').xml
        if data.msgtype.text == 'event':
            if data.event.text == 'subscribe':
                return subscribe(request, data)
        elif data.msgtype.text == 'text':
            msg = {'from': data.fromusername.text,
                   'to': data.tousername.text,
                   'time': data.createtime.text,
                   'content': data.content.text}
            try:
                return admin(request, msg, User.objects.get(wechat=msg['from'], group__name='admin'))
            except ObjectDoesNotExist:
                try:
                    return text(request, msg, User.objects.get(wechat=msg['from']))
                except ObjectDoesNotExist:
                    return login(request, msg)
        else:
            return HttpResponse()
    else:
        return HttpResponse(request.GET['echostr'])
