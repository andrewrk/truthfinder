from google.appengine.api import users

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

from main.models import TruthNode, NodeRelationship, ChangeNotification
from main.forms import CreateNodeForm, NodeRelationshipForm

from django.conf import settings

import simplejson as json

ok_emails = set([
    'superjoe30@gmail.com',
    'tyler.heald@gmail.com',
])



def login_required(function):
    def decorated(*args, **kwargs):
        user = users.get_current_user() 
        if user and user.email() in ok_emails:
            return function(*args, **kwargs)
        else:
            request = args[0]
            return HttpResponseRedirect(users.create_login_url(request.path))
    return decorated

def orphans(request):
    nodes = [n for n in TruthNode.objects.all() if NodeRelationship.objects.filter(child_node__pk=n.pk).count() == 0]
    return render_to_response('orphans.html', {'nodes': nodes}, 
        context_instance=RequestContext(request))

def changelist(request):
    changes = ChangeNotification.objects.order_by('-date')[:40]
    pin_type_names = dict(NodeRelationship.RELATIONSHIP_CHOICES)
    return render_to_response('changelist.html', locals(), 
        context_instance=RequestContext(request))

def home(request):
    nodes = [rel.child_node for rel in NodeRelationship.objects.filter(parent_node__pk=settings.HOME_PAGE_ID)]
    return render_to_response('home.html', {'nodes': nodes}, 
        context_instance=RequestContext(request))

def common_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))

    parent_rels = NodeRelationship.objects.filter(child_node__pk=node.pk)
    parents = [rel.parent_node for rel in parent_rels]

    children_rels = NodeRelationship.objects.filter(parent_node__pk=node.pk)
    pro_rels = children_rels.filter(relationship=NodeRelationship.PRO)
    con_rels = children_rels.filter(relationship=NodeRelationship.CON)
    premise_rels = children_rels.filter(relationship=NodeRelationship.PREMISE)
    pros = [rel.child_node for rel in pro_rels]
    cons = [rel.child_node for rel in con_rels]
    premises = [rel.child_node for rel in premise_rels]

    return {
        'node': node,
        'parents': parents,
        'parent_rels': parent_rels,
        'relationship_choices': dict(NodeRelationship.RELATIONSHIP_CHOICES),
        'pros': pros,
        'cons': cons,
        'premises': premises,
    }

def json_response(data):
    return HttpResponse(json.dumps(data), mimetype="text/plain")

def ajax_node(request, node_id):
    context = common_node(request, node_id)
    return render_to_response('node_content.html', context, 
        context_instance=RequestContext(request))

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
            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            change = ChangeNotification()
            change.change_type = ChangeNotification.EDIT
            change.user = users.get_current_user().nickname()
            change.node = node
            change.node_title = node.title
            change.save()


            return HttpResponseRedirect(reverse('node', args=[node.id]))
    else:
        form = CreateNodeForm(initial={
            'title': node.title,
            'content': node.content,
        })

    return render_to_response('add.html', {'form': form}, 
        context_instance=RequestContext(request))

@login_required
def unpin_node(request, child_node_id, parent_node_id, relationship_type):
    child_node = get_object_or_404(TruthNode, pk=int(child_node_id))
    parent_node = get_object_or_404(TruthNode, pk=int(parent_node_id))
    relationship = NodeRelationship.objects.get(parent_node=parent_node, child_node=child_node, relationship=int(relationship_type))
    relationship_choices = dict(NodeRelationship.RELATIONSHIP_CHOICES)
    
    if request.method == 'POST':
        change = ChangeNotification()
        change.change_type = ChangeNotification.UNPIN
        change.user = users.get_current_user().nickname()
        change.node = child_node
        change.node_title = child_node.title
        change.pin_type = relationship.relationship
        change.parent_node = parent_node
        change.parent_node_title = parent_node.title
        change.save()

        relationship.delete()

        return HttpResponseRedirect(reverse('home'))
    else:
        return render_to_response('unpin.html', locals(),
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
    if request.method == 'POST':
        change = ChangeNotification()
        change.change_type = ChangeNotification.DELETE
        change.user = users.get_current_user().nickname()
        change.node_title = node.title
        change.save()

        NodeRelationship.objects.filter(parent_node__pk=node.pk).delete()
        NodeRelationship.objects.filter(child_node__pk=node.pk).delete()
        node.delete()

        return HttpResponseRedirect(reverse('home'))
    else:
        return render_to_response('delete.html', {'node': node}, 
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
