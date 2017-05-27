from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_safe

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import *

import bs4


@require_safe
def query(request):
    context = {'paid': request.GET.get('paid', False),
               'contests': sorted(list(Contest.objects.all()), key=lambda c: c.order)}
    return render(request, 'contest/query.html', context)


@require_safe
def checklist(request):
    context = {'contests': sorted(list(Contest.objects.all()), key=lambda c: c.order)}
    return render(request, 'contest/checklist.html', context)


@require_safe
def scoretable(request):
    context = {'contests': sorted(list(Contest.objects.all()), key=lambda c: c.order)}
    return render(request, 'contest/scoretable.html', context)


def get_number(s):
    return ''.join(filter(str.isdigit, s))


def subscribe(request, msg):
    context = {'msg': msg,
               'current': Current.objects.get().contest,
               'result': False,
               'reason': 0}
    return render(request, 'contest/login.xml', context)


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
        user = User(group=Group.objects.get(id=2),
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
    content = get_number(msg['content'])
    if content == 0:
        context = {'msg': msg,
                   'current': Current.objects.get().contest}
        return render(request, 'contest/base.xml', context)
    current = Current.objects.get().contest
    if len(content) != 4 or len(content) + 10 < len(msg['content']):
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': False,
                   'reason': 0}
        return render(request, 'contest/vote.xml', context)
    participate = None
    try:
        participate = current.participate_set.get(contestant1__number=content)
    except ObjectDoesNotExist:
        pass
    try:
        participate = current.participate_set.get(contestant2__number=content)
    except ObjectDoesNotExist:
        pass
    if participate:
        vote = None
        try:
            vote = Vote.objects.get(participate__contest=participate.contest)
        except ObjectDoesNotExist:
            pass
        if vote:
            context = {'msg': msg,
                       'current': Current.objects.get().contest,
                       'result': False,
                       'reason': 1}
            return render(request, 'contest/vote.xml', context)
        Vote(user=user, participate=participate).save()
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': True}
        return render(request, 'contest/vote.xml', context)
    try:
        participate = current.prev().participate_set.get(contestant1__number=content)
    except ObjectDoesNotExist:
        pass
    try:
        participate = current.prev().participate_set.get(contestant2__number=content)
    except ObjectDoesNotExist:
        pass
    if participate:
        vote = None
        try:
            vote = Vote.objects.get(participate__contest=participate.contest)
        except ObjectDoesNotExist:
            pass
        if vote:
            context = {'msg': msg,
                       'current': Current.objects.get().contest,
                       'result': False,
                       'reason': 1}
            return render(request, 'contest/vote.xml', context)
        Vote(user=user, participate=participate).save()
        context = {'msg': msg,
                   'current': Current.objects.get().contest,
                   'result': True}
        return render(request, 'contest/vote.xml', context)
    context = {'msg': msg,
               'current': Current.objects.get().contest,
               'result': False,
               'reason': 2}
    return render(request, 'contest/vote.xml', context)


def admin(request, msg, _):
    context = {'msg': msg,
               'current': Current.objects.get().contest}
    return render(request, 'contest/base.xml', context)


@csrf_exempt
@require_http_methods(['HEAD', 'GET', 'POST'])
def webhook(request):
    if request.method == 'POST':
        data = bs4.BeautifulSoup(request.body, 'html.parser').xml
        if data.msgtype.text == 'event':
            if data.event.text == 'subscribe':
                msg = {'from': data.fromusername.text,
                       'to': data.tousername.text}
                return subscribe(request, msg)
        elif data.msgtype.text == 'text':
            msg = {'from': data.fromusername.text,
                   'to': data.tousername.text,
                   'time': data.createtime.text,
                   'content': data.content.text}
            try:
                return admin(request, msg, User.objects.get(wechat=msg['from'], group_id=4))
            except ObjectDoesNotExist:
                try:
                    return text(request, msg, User.objects.get(wechat=msg['from']))
                except ObjectDoesNotExist:
                    return login(request, msg)
        else:
            return HttpResponse()
    else:
        return HttpResponse(request.GET['echostr'])
