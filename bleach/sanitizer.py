import re
from xml.sax.saxutils import escape, unescape

from html5lib.constants import tokenTypes
from html5lib.sanitizer import HTMLSanitizerMixin
from html5lib.tokenizer import HTMLTokenizer


class BleachSanitizerMixin(HTMLSanitizerMixin):
    """Mixin to replace sanitize_token() and sanitize_css()."""

    allowed_svg_properties = []

    def sanitize_token(self, token):
        """Sanitize a token either by HTML-encoding or dropping.

        Unlike HTMLSanitizerMixin.sanitize_token, allowed_attributes can be
        a dict of 'tag' => ['attribute', 'pairs'].

        Also gives the option to strip tags instead of encoding.

        """

        if token['type'] in (tokenTypes['StartTag'], tokenTypes['EndTag'],
                             tokenTypes['EmptyTag']):
            if token['name'] in self.allowed_elements:
                if 'data' in token:
                    if isinstance(self.allowed_attributes, dict):
                        allowed_attributes = self.allowed_attributes.get(
                            token['name'], [])
                    else:
                        allowed_attributes = self.allowed_attributes
                    attrs = dict([(name, val) for name, val in
                                  token['data'][::-1]
                                  if name in allowed_attributes])
                    for attr in self.attr_val_is_uri:
                        if not attr in attrs:
                            continue
                        val_unescaped = re.sub("[`\000-\040\177-\240\s]+", '',
                                               unescape(attrs[attr])).lower()
                        # Remove replacement characters from unescaped
                        # characters.
                        val_unescaped = val_unescaped.replace(u"\ufffd", "")
                        if (re.match(r'^[a-z0-9][-+.a-z0-9]*:', val_unescaped)
                            and (val_unescaped.split(':')[0] not in
                                 self.allowed_protocols)):
                            del attrs[attr]
                    for attr in self.svg_attr_val_allows_ref:
                        if attr in attrs:
                            attrs[attr] = re.sub(r'url\s*\(\s*[^#\s][^)]+?\)',
                                                 ' ',
                                                 unescape(attrs[attr]))
                    if (token['name'] in self.svg_allow_local_href and
                        'xlink:href' in attrs and
                        re.search(r'^\s*[^#\s].*', attrs['xlink:href'])):
                        del attrs['xlink:href']
                    if 'style' in attrs:
                        attrs['style'] = self.sanitize_css(attrs['style'])
                    token['data'] = [(name, val) for name, val in
                                     attrs.items()]
                return token
            elif self.strip_disallowed_elements:
                pass
            else:
                if token['type'] == tokenTypes['EndTag']:
                    token['data'] = '</%s>' % token['name']
                elif token['data']:
                    attrs = ''.join([' %s="%s"' % (k, escape(v)) for k, v in
                                    token['data']])
                    token['data'] = '<%s%s>' % (token['name'], attrs)
                else:
                    token['data'] = '<%s>' % token['name']
                if token['selfClosing']:
                    token['data'] = token['data'][:-1] + '/>'
                token['type'] = tokenTypes['Characters']
                del token["name"]
                return token
        elif token['type'] == tokenTypes['Comment']:
            if not self.strip_html_comments:
                return token
        else:
            return token

    def sanitize_css(self, style):
        """HTMLSanitizerMixin.sanitize_css replacement.

        HTMLSanitizerMixin.sanitize_css always whitelists background-*,
        border-*, margin-*, and padding-*. We only whitelist what's in
        the whitelist.

        """
        # disallow urls
        style = re.compile('url\s*\(\s*[^\s)]+?\s*\)\s*').sub(' ', style)

        # gauntlet
        if not re.match("""^([:,;#%.\sa-zA-Z0-9!]|\w-\w|'[\s\w]+"""
                        """'|"[\s\w]+"|\([\d,\s]+\))*$""",
                        style):
            return ''
        if not re.match("^\s*([-\w]+\s*:[^:;]*(;\s*|$))*$", style):
            return ''

        clean = []
        for prop, value in re.findall('([-\w]+)\s*:\s*([^:;]*)', style):
            if not value:
                continue
            if prop.lower() in self.allowed_css_properties:
                clean.append(prop + ': ' + value + ';')
            elif prop.lower() in self.allowed_svg_properties:
                clean.append(prop + ': ' + value + ';')

        return ' '.join(clean)


class BleachSanitizer(HTMLTokenizer, BleachSanitizerMixin):
    def __init__(self, stream, encoding=None, parseMeta=True, useChardet=True,
                 lowercaseElementName=True, lowercaseAttrName=True):
        HTMLTokenizer.__init__(self, stream, encoding, parseMeta, useChardet,
                               lowercaseElementName, lowercaseAttrName)

    def __iter__(self):
        for token in HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token
