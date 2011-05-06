from django.shortcuts import render_to_response

def choose_photo(request):
    try:
       from photologue.models import PhotoSize, Photo
    except ImportError:
        raise Exception('You must install Photologue to use this feature')
    context = {}
    #get choices of photo sizes
    photo_sizes = PhotoSize.objects.all()
    #get choices of photos
    photos = Photo.objects.all()
    #set the context
    context['photo_sizes'] = photo_sizes
    context['photos'] = photos
    #display
    return render_to_response("richtext/choose_photo.html", context)

def testRichText(request):
    from richtext.forms import TestingForm
    form = TestingForm()
    return render_to_response('richtext/testrichtext.html', {'form':form})


   
