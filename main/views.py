from google.appengine.api import users

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from main.models import TruthNode, NodeRelationship
from main.forms import CreateNodeForm

def home(request):
    nodes = TruthNode.objects.all()
    return render_to_response('home.html', {'nodes': nodes}, 
        context_instance=RequestContext(request))

def node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    return render_to_response('node.html', {'node': node}, 
        context_instance=RequestContext(request))

def add_node(request):
    if request.method == 'POST':
        form = CreateNodeForm(request.POST)
        if form.is_valid():
            node = TruthNode()
            node.title = form.cleaned_data.get('title')
            node.content = form.cleaned_data.get('content')
            node.save()

            return HttpResponseRedirect(reverse('home'))
    else:
        form = CreateNodeForm()

    return render_to_response('add.html', {'form': form}, 
        context_instance=RequestContext(request))

def edit_node(request, node_id):
    pass

def delete_node(request, node_id):
    node = get_object_or_404(TruthNode, pk=int(node_id))
    if request.method == 'POST':
        node.delete()
        return HttpResponseRedirect(reverse('home'))
    else:
        return render_to_response('delete.html', {'node': node}, 
            context_instance=RequestContext(request))

def add_pro(request, node_id):
    pass

def add_con(request, node_id):
    pass
