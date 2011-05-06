from django.utils.safestring import mark_safe
from django import forms
import settings
from string import Template

class RichTextWidget(forms.TextInput):
   def __init__(self, attrs=None):
      final_attrs = {'class': 'richtext vLargeTextField', 'photologue': False}
      if attrs is not None:
         final_attrs.update(attrs)
      super(RichTextWidget, self).__init__(attrs=final_attrs)
            
   def render(self, name, value, attrs=None):
        output = []
        template = Template(u"""
            <script type="text/javascript">
                setupRichTextEditor("$id", "$photologue");
            </script>
            <textarea id="$id" class="$class" name="$name">$value</textarea>
            """)
        subs = {}
        subs['id'] = "id_" + name
        subs['name'] = name
        if value is not None:
            subs['value'] = value
        else:
            subs['value'] = ""
        subs['class'] = self.attrs['class']
        subs['photologue'] = self.attrs['photologue'] #MUST use self.attrs, not just attrs.
        
        output.append(template.substitute(subs))
        return mark_safe(u''.join(output))
    
   class Media:
        css = {
            'all': ('http://yui.yahooapis.com/2.6.0/build/assets/skins/sam/skin.css', 'richtext/css/richtext.css',)
        }
        js = (
            'http://yui.yahooapis.com/2.6.0/build/yahoo-dom-event/yahoo-dom-event.js',
            'http://yui.yahooapis.com/2.6.0/build/element/element-beta-min.js',
            'http://yui.yahooapis.com/2.6.0/build/container/container_core-min.js',
            'http://yui.yahooapis.com/2.6.0/build/menu/menu-min.js',
            'http://yui.yahooapis.com/2.6.0/build/button/button-min.js',
            'http://yui.yahooapis.com/2.6.0/build/editor/editor-min.js',
            'richtext/js/richtext.js',
            )
     