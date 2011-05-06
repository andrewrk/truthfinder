"""More advanced security tests"""

from nose.tools import eq_

from bleach import clean


def test_nested_script_tag():
    eq_('&lt;&lt;script&gt;script&gt;evil()&lt;&lt;/script&gt;/script&gt;',
        clean('<<script>script>evil()<</script>/script>'))
    eq_('&lt;&lt;x&gt;script&gt;evil()&lt;&lt;/x&gt;/script&gt;',
        clean('<<x>script>evil()<</x>/script>'))


def test_nested_script_tag_r():
    eq_('&lt;script&lt;script&gt;&gt;evil()&lt;/script&lt;&gt;&gt;',
        clean('<script<script>>evil()</script</script>>'))


def test_invalid_attr():
    IMG = ['img', ]
    IMG_ATTR = ['src']

    eq_('<a href="test">test</a>',
        clean('<a onclick="evil" href="test">test</a>'))
    eq_('<img src="test">',
        clean('<img onclick="evil" src="test" />',
                tags=IMG, attributes=IMG_ATTR))
    eq_('<img src="test">',
        clean('<img href="invalid" src="test" />',
                tags=IMG, attributes=IMG_ATTR))


def test_unquoted_attr():
    eq_('<abbr title="mytitle">myabbr</abbr>',
        clean('<abbr title=mytitle>myabbr</abbr>'))


def test_unquoted_event_handler():
    eq_('<a href="http://xx.com">xx.com</a>',
        clean('<a href="http://xx.com" onclick=foo()>xx.com</a>'))


def test_invalid_attr_value():
    eq_('&lt;img src="javascript:alert(\'XSS\');"&gt;',
        clean('<img src="javascript:alert(\'XSS\');">'))


def test_invalid_href_attr():
    eq_('<a>xss</a>',
        clean('<a href="javascript:alert(\'XSS\')">xss</a>'))


def test_invalid_tag_char():
    eq_('&lt;script xss="" src="http://xx.com/xss.js"&gt;&lt;/script&gt;',
        clean('<script/xss src="http://xx.com/xss.js"></script>'))
    eq_('&lt;script src="http://xx.com/xss.js"&gt;&lt;/script&gt;',
        clean('<script/src="http://xx.com/xss.js"></script>'))


def test_unclosed_tag():
    eq_('&lt;script src="http://xx.com/xss.js&amp;lt;b"&gt;',
        clean('<script src=http://xx.com/xss.js<b>'))
    eq_('&lt;script src="http://xx.com/xss.js" &lt;b=""&gt;',
        clean('<script src="http://xx.com/xss.js"<b>'))
    eq_('&lt;script src="http://xx.com/xss.js" &lt;b=""&gt;',
        clean('<script src="http://xx.com/xss.js" <b>'))


def test_strip():
    """Using strip=True shouldn't result in malicious content."""
    s = '<scri<script>pt>alert(1)</scr</script>ipt>'
    eq_('pt&gt;alert(1)ipt&gt;', clean(s, strip=True))
    s = '<scri<scri<script>pt>pt>alert(1)</script>'
    eq_('pt&gt;pt&gt;alert(1)', clean(s, strip=True))
