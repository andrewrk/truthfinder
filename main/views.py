from google.appengine.api import users

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from main.models import TruthNode, NodeRelationship
from main.forms import CreateNodeForm

def home(request):
    nodes = [n for n in TruthNode.objects.all() if NodeRelationship.objects.filter(child_node__pk=n.pk).count() == 0]
    return render_to_response('home.html', {'nodes': nodes}, 
        context_instance=RequestContext(request))

def common_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    children_rels = NodeRelationship.objects.filter(parent_node__pk=node.pk)
    pro_rels = children_rels.filter(relationship=NodeRelationship.PRO)
    con_rels = children_rels.filter(relationship=NodeRelationship.CON)
    pros = [rel.child_node for rel in pro_rels]
    cons = [rel.child_node for rel in con_rels]

    return {
        'node': node,
        'pros': pros,
        'cons': cons,
    }
    

def ajax_node(request, node_id):
    context = common_node(request, node_id)
    return render_to_response('node_content.html', context, 
        context_instance=RequestContext(request))

def node(request, node_id):
    context = common_node(request, node_id)
    return render_to_response('node.html', context, 
        context_instance=RequestContext(request))

def add_node(request):
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            node = TruthNode()
            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            return HttpResponseRedirect(reverse('node', args=[node.id]))
    else:
        form = CreateNodeForm()

    return render_to_response('add.html', {'form': form}, 
        context_instance=RequestContext(request))

def edit_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
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

def delete_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
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

            return HttpResponseRedirect(reverse('node', args=[parent.id]))
    else:
        form = CreateNodeForm()

    context = {
        'parent': parent,
        'arg_type': arg_type,
        'form': form,
    }
    return render_to_response('arg.html', context,
        context_instance=RequestContext(request))

def add_pro(request, node_id):
    return add_arg(request, node_id, NodeRelationship.PRO)

def add_con(request, node_id):
    return add_arg(request, node_id, NodeRelationship.CON)
