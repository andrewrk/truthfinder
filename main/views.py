from google.appengine.api import users

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from main.models import TruthNode, NodeRelationship, ChangeNotification
from main.forms import CreateNodeForm, NodeRelationshipForm, NodeRelationshipFormMissingChild

import simplejson as json
from datetime import datetime

ok_emails = set([
    'superjoe30@gmail.com',
    'tyler.heald@gmail.com',
    'thejoshwolfe@gmail.com',
    'suraphael@gmail.com',
])

def admin_required(function):
    def decorated(*args, **kwargs):
        if users.is_current_user_admin():
            return function(*args, **kwargs)
        else:
            request = args[0]
            return HttpResponseRedirect(users.create_login_url(request.path))
    return decorated

def login_required(function):
    def decorated(*args, **kwargs):
        user = users.get_current_user() 
        if user and user.email() in ok_emails:
            return function(*args, **kwargs)
        else:
            request = args[0]
            return HttpResponseRedirect(users.create_login_url(request.path))
    return decorated

def node_children(request, template, node_id):
    node_rels = NodeRelationship.objects.filter(parent_node__pk=node_id)
    return render_to_response(template, {'node_rels': node_rels}, 
        context_instance=RequestContext(request))

def orphans(request):
    return node_children(request, 'orphans.html', settings.ORPHANS_ID)

def home(request):
    return node_children(request, 'home.html', settings.HOME_PAGE_ID)

def flagged(request):
    return node_children(request, 'flagged.html', settings.FLAG_ID)

def changelist(request):
    paginator = Paginator(ChangeNotification.objects.order_by('-date'), 40)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        changes = paginator.page(page)
    except (EmptyPage, InvalidPage):
        changes = paginator.page(paginator.num_pages)
    
    context = {
        'pin_type_names': dict(NodeRelationship.RELATIONSHIP_CHOICES),
        'changes': changes,
    }
    return render_to_response('changelist.html', context, 
        context_instance=RequestContext(request))

def common_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))

    parent_rels = NodeRelationship.objects.filter(child_node__pk=node.pk)

    children_rels = NodeRelationship.objects.filter(parent_node__pk=node.pk)
    pro_rels = children_rels.filter(relationship=NodeRelationship.PRO)
    con_rels = children_rels.filter(relationship=NodeRelationship.CON)
    premise_rels = children_rels.filter(relationship=NodeRelationship.PREMISE)

    return {
        'node': node,
        'relationship_choices': dict(NodeRelationship.RELATIONSHIP_CHOICES),
        'parent_rels': parent_rels,
        'pro_rels': pro_rels,
        'con_rels': con_rels,
        'premise_rels': premise_rels,
    }

@admin_required
def cron_orphans(request):
    for node in TruthNode.objects.all():
        if NodeRelationship.objects.filter(child_node__pk=node.pk).count() == 0:
            # this is an orphan. pin it to orphans.
            rel = NodeRelationship()
            rel.child_node = node
            rel.parent_node = TruthNode.objects.get(pk=settings.ORPHANS_ID)
            rel.relationship = NodeRelationship.PRO
            rel.createDiscussionNode()
            rel.save()

    return json_response({"success": True})

def json_response(data):
    def json_dthandler(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%B %d, %Y %H:%M:%S')
        else:
            return None

    return HttpResponse(json.dumps(data, default=json_dthandler), mimetype="text/plain")

def ajax_search(request):
    query = request.GET.get('term')

    # perform search
    nodes = TruthNode.objects.filter(title__startswith=query)

    # limit to 15 results
    nodes = nodes[:15]

    data = []
    for node in nodes:
        data.append({
            'id': node.id,
            'label': node.title,
            'value': node.title,
        })

    return json_response(data)

def ajax_rel(request, rel_id):
    node_rel = get_object_or_404(NodeRelationship, pk=int(rel_id))

    context = common_node(request, node_rel.child_node.id)
    context['node_rel'] = node_rel

    if node_rel.invert_child:
        context['pro_rels'], context['con_rels'] = context['con_rels'], context['pro_rels']

    return render_to_response('node_content.html', context,
        context_instance=RequestContext(request))

def ajax_node(request, node_id):
    context = common_node(request, node_id)
    return render_to_response('node_content.html', context, 
        context_instance=RequestContext(request))

def ajax_node_json(request, node_id):
    data = common_node(request, node_id)
    del data['relationship_choices']
    node = data['node']
    data['node'] = {
        'title': node.title,
        'content': node.content,
        'create_date': node.create_date,
        'edit_date': node.edit_date,
    }
    rid = lambda rels: [r.pk for r in rels]
    data['parent_rels'] = rid(data['parent_rels'])
    data['pro_rels'] = rid(data['pro_rels'])
    data['con_rels'] = rid(data['con_rels'])
    data['premise_rels'] = rid(data['premise_rels'])
    return json_response(data)

def ajax_rel_json(request, rel_id):
    node_rel = get_object_or_404(NodeRelationship, pk=int(rel_id))
    data = {
        'parent': node_rel.parent_node.pk,
        'child': node_rel.child_node.pk,
        'relationship': node_rel.relationship,
        'invert_child': node_rel.invert_child,
        'discussion_node': node_rel.discussion_node.pk,
    }
    return json_response(data)
    

def node(request, node_id):
    # redirect to home page if home page is requested
    if int(node_id) == settings.HOME_PAGE_ID:
        return HttpResponseRedirect('/')

    context = common_node(request, node_id)
    return render_to_response('node.html', context, 
        context_instance=RequestContext(request))

@login_required
def add_node(request):
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            node = TruthNode()
            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            rel = NodeRelationship()
            rel.parent_node = TruthNode.objects.get(pk=settings.HOME_PAGE_ID)
            rel.child_node = node
            rel.relationship = NodeRelationship.PRO
            rel.createDiscussionNode()
            rel.save()

            change = ChangeNotification()
            change.change_type = ChangeNotification.CREATE
            change.user = users.get_current_user().nickname()
            change.node = node
            change.node_title = node.title
            change.save()

            return HttpResponseRedirect(reverse('node', args=[node.id]))
    else:
        form = CreateNodeForm()

    return render_to_response('add.html', {'form': form}, 
        context_instance=RequestContext(request))

@login_required
def edit_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            change = ChangeNotification()
            change.change_type = ChangeNotification.EDIT
            change.user = users.get_current_user().nickname()
            change.node = node
            change.node_title = node.title
            change.save()

            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            return HttpResponseRedirect(reverse('node', args=[node.id]))
    else:
        form = CreateNodeForm(initial={
            'title': node.title,
            'content': node.content,
        })

    return render_to_response('add.html', {'form': form}, 
        context_instance=RequestContext(request))

@login_required
def invert(request, rel_id):
    rel = get_object_or_404(NodeRelationship, pk=int(rel_id))
    rel_choices = dict(NodeRelationship.RELATIONSHIP_CHOICES)

    if request.method == 'POST':
        rel.invert_child = not rel.invert_child
        rel.save()

        return HttpResponseRedirect(reverse('node', args=[rel.parent_node.id]))
    else:
        return render_to_response('invert.html', locals(), 
            context_instance=RequestContext(request))

@login_required
def unpin_node(request, node_rel_id):
    relationship = get_object_or_404(NodeRelationship, pk=int(node_rel_id))
    relationship_choices = dict(NodeRelationship.RELATIONSHIP_CHOICES)

    if request.method == 'POST':
        change = ChangeNotification()
        change.change_type = ChangeNotification.UNPIN
        change.user = users.get_current_user().nickname()
        change.node = relationship.child_node
        change.node_title = relationship.child_node.title
        change.pin_type = relationship.relationship
        change.parent_node = relationship.parent_node
        change.parent_node_title = relationship.parent_node.title
        change.save()

        relationship.delete()

        return HttpResponseRedirect(reverse('node', args=[relationship.parent_node.id]))
    else:
        return render_to_response('unpin.html', locals(),
            context_instance=RequestContext(request))
    
@login_required
def pin_existing(request, node_id, relationship_type):
    parent_node = get_object_or_404(TruthNode, pk=int(node_id))
    relationship_type = int(relationship_type)

    if request.method == 'POST':
        form = NodeRelationshipFormMissingChild(request.POST)
        if form.is_valid():
            relate = NodeRelationship()
            relate.parent_node = form.cleaned_data.get('parent_node')
            relate.child_node = form.cleaned_data.get('child_node')
            relate.relationship = form.cleaned_data.get('relationship')
            relate.invert_child = form.cleaned_data.get('invert_child')
            relate.createDiscussionNode()
            relate.save()

            change = ChangeNotification()
            change.change_type = ChangeNotification.PIN
            change.user = users.get_current_user().nickname()
            change.node = relate.child_node
            change.node_title = relate.child_node.title
            change.pin_type = relate.relationship
            change.parent_node = relate.parent_node
            change.parent_node_title = relate.parent_node.title
            change.save()

            return HttpResponseRedirect(reverse("node", args=[relate.parent_node.id]))
    else:
        initial = {
            'relationship': relationship_type,
        }
        form = NodeRelationshipForm(initial=initial)
    return render_to_response('pin_existing.html', locals(),
        context_instance=RequestContext(request))

@login_required
def pin_node(request, node_id):
    child_node = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
        form = NodeRelationshipForm(request.POST)
        if form.is_valid():
            relate = NodeRelationship()
            relate.parent_node = form.cleaned_data.get('parent_node')
            relate.child_node = form.cleaned_data.get('child_node')
            relate.relationship = form.cleaned_data.get('relationship')
            relate.invert_child = form.cleaned_data.get('invert_child')
            relate.createDiscussionNode()
            relate.save()

            change = ChangeNotification()
            change.change_type = ChangeNotification.PIN
            change.user = users.get_current_user().nickname()
            change.node = relate.child_node
            change.node_title = relate.child_node.title
            change.pin_type = relate.relationship
            change.parent_node = relate.parent_node
            change.parent_node_title = relate.parent_node.title
            change.save()

            return HttpResponseRedirect(reverse("node", args=[relate.parent_node.id]))
    else:
        form = NodeRelationshipForm()
    return render_to_response('pin.html', locals(),
        context_instance=RequestContext(request))

@login_required
def delete_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    parent_rels = NodeRelationship.objects.filter(child_node__pk=node.pk)
    child_rels = NodeRelationship.objects.filter(parent_node__pk=node.pk)
    rel_types = dict(NodeRelationship.RELATIONSHIP_CHOICES)

    if request.method == 'POST':
        change = ChangeNotification()
        change.change_type = ChangeNotification.DELETE
        change.user = users.get_current_user().nickname()
        change.node_title = node.title
        change.save()

        parent_rels.delete()
        child_rels.delete()
        node.delete()

        return HttpResponseRedirect(reverse('home'))
    else:
        return render_to_response('delete.html', locals(), 
            context_instance=RequestContext(request))

def add_arg(request, node_id, arg_type):
    parent = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            node = TruthNode()
            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            relate = NodeRelationship()
            relate.parent_node = parent
            relate.child_node = node
            relate.relationship = arg_type
            relate.createDiscussionNode()
            relate.save()

            change = ChangeNotification()
            change.change_type = ChangeNotification.ADD
            change.user = users.get_current_user().nickname()
            change.node = relate.child_node
            change.node_title = relate.child_node.title
            change.pin_type = relate.relationship
            change.parent_node = relate.parent_node
            change.parent_node_title = relate.parent_node.title
            change.save()


            return HttpResponseRedirect(reverse('node', args=[parent.id]))
    else:
        form = CreateNodeForm()

    context = {
        'parent': parent,
        'arg_type': arg_type,
        'arg_type_text': dict(NodeRelationship.RELATIONSHIP_CHOICES)[arg_type],
        'form': form,
    }
    return render_to_response('arg.html', context,
        context_instance=RequestContext(request))

@login_required
def add_pro(request, node_id):
    return add_arg(request, node_id, NodeRelationship.PRO)

@login_required
def add_con(request, node_id):
    return add_arg(request, node_id, NodeRelationship.CON)

@login_required
def add_premise(request, node_id):
    return add_arg(request, node_id, NodeRelationship.PREMISE)
