import bbcode

def _render_color(tag_name, value, options, parent, context):
    color = tag_name
    return '<span style="color:%s;">%s</span>' % (color, value)

def _render_size(tag_name, value, options, parent, context):
    if options and 'size' in options:
        size = options['size']
    else:
        return value
    return '<span style="font-size:%s;">%s</span>' % (size, value)

def _render_img(tag_name, value, options, parent, context):
    link = value
    return '<img src="%s" />' % (link)

def Parser():
    bbparser = bbcode.Parser(replace_cosmetic=False, install_defaults=False)
    
    for color in ('red', 'blue', 'green', 'yellow', 'black', 'white'):
        bbparser.add_formatter(color, _render_color)
    bbparser.add_simple_formatter('hr', '<hr />', standalone=True)
    bbparser.add_formatter('size', _render_size)
    bbparser.add_formatter('img', _render_img, replace_links=False, replace_cosmetic=False)
    
    # We override our formatters if a default exist.
    bbparser.install_default_formatters()
    return bbparser;

