import cssutils
from xml.sax import saxutils
from lxml.html import tostring, fromstring, clean, HtmlElement
from lxml.html.soupparser import fromstring as soup_fromstring
from lxml.etree import _ElementStringResult, _ElementUnicodeResult
from lxml import etree
import cssutils
import sys

import logging

# If this code is ported to python 3 this should probably ensure that it still works
if sys.version_info.major == 3:
    unicode = str

class Cleaner(clean.Cleaner):
    def _is_redundant_node(self, is_color_span, child_nodes):
        if not is_color_span:
            return False

        for child in child_nodes:
            if type(child) == HtmlElement:
                if not (child.tag == 'span' and child.attrib.get(\
                        'style') is not None and 'color:' in child.attrib.get('style')):
                    if child.tag != 'br':
                        return False

            if type(child) == _ElementStringResult:
                if len(str(child).strip()) > 0:
                    return False
            if type(child) == _ElementUnicodeResult:
                if len(unicode(child).strip()) > 0:
                    return False

        return True

    def _remove_rendundant_html_spans_helper(self, tree):
        to_process = []
        to_process.append((tree, tree.attrib.get('style') and 'color:' in tree.attrib.get('style')))
        needs_reclean = False

        while len(to_process) > 0:
            current_elem, is_color_span = to_process.pop()
            child_nodes = current_elem.xpath("node()")
            current_style = cssutils.parseStyle(current_elem.attrib.get('style') or "")
            current_elem_dropped = False

            # We only will drop the current tag if its sole purpose is to be a color span and it is redundant
            if current_style.length == 1 and self._is_redundant_node(is_color_span, child_nodes):
                current_elem.drop_tag()
                current_elem_dropped = True
                needs_reclean = True

            for child in child_nodes:
                if type(child) == HtmlElement:
                    child_stylesheet = cssutils.parseStyle(child.attrib.get('style') or "")

                    if (not current_elem_dropped) and is_color_span and child.tag == 'span' and 'color' in child_stylesheet and child_stylesheet.length == 1 and current_style.color == child_stylesheet.color:
                        # Since we will drop this child, we should make sure to process this child's children
                        for c_child in child.xpath("node()"):
                            if type(c_child) == HtmlElement:
                                to_process.append((c_child, c_child.attrib.get('style') and 'color:' in c_child.attrib.get('style')))
                        child.drop_tag()
                        needs_reclean = True
                    else:
                        to_process.append((child, child.attrib.get('style') and 'color:' in child.attrib.get('style')))
        return needs_reclean

    def remove_rendundant_html_spans(self, html):
        """Remove redundant color span tags"""
        tree = soup_fromstring(u'<div id="parsed_and_cleaned_html_content">' + html + '</div>', features="html.parser")
        while self._remove_rendundant_html_spans_helper(tree):
            pass # Keep re-cleaning the tree until it is completely cleaned
        return tostring(tree.xpath("//div[@id='parsed_and_cleaned_html_content']")[0])[len('<div id="parsed_and_cleaned_html_content">'):-6].decode('utf-8')

    def clean_html(self, html, remove_rendundant_spans=True):
        if not isinstance(html, unicode):
            raise ValueError('We only support cleaning unicode HTML fragments')

        # Remove redundant spans with color attributes
        if remove_rendundant_spans:
            html = self.remove_rendundant_html_spans(html)

        #We wrap the content up in an extra div tag (otherwise lxml does wierd things to it - like adding in <p> tags and stuff)
        divnode = fromstring(u'<div>' + html + u'</div>')
        self(divnode)

        # Strip all class attributes
        etree.strip_attributes(divnode, 'class')

        # Drop all xml:lang and lang attributes, and handle the
        # stripping of any bad css styles
        # Also drop id and class attributes - these are not useful in RichTextEditor
        for node in divnode.xpath("//*"):
            for key, value in node.attrib.iteritems():
                if key.lower() in ('xml:lang', 'lang','id','class'):
                    node.attrib.pop(key, None)
                elif 'style' == key.lower():
                    try:
                        cssStyle = cssutils.parseStyle(value)
                    except Exception, e:
                        logging.info("Style %s failed to parse with error %s." % (value, e))
                        node.attrib.pop(key, None)
                        continue

                    # Set the line separator so that the style gets serialized
                    cssutils.ser.prefs.lineSeparator = ''
                    # Only allow valid style properties
                    cssutils.ser.prefs.validOnly = True

                    new_style = cssStyle.cssText
                    if not new_style.strip():
                        node.attrib.pop(key, None)
                    else:
                        node.attrib[key] = new_style
            # Drop all empty span tags
            if node.tag == 'span' and not node.keys():
                node.drop_tag()

        #Now unwrap the divnode (i.e. just serialize the children of our extra div node)
        cleaned = saxutils.escape(divnode.text) if divnode.text else ''

        for n in divnode:
            cleaned += tostring(n, encoding = unicode, method = 'xml')
        return cleaned

# We need safe_attrs_only set to False, otherwise it strips out style attributes completely
cleaner = Cleaner(safe_attrs_only=False)
clean_html = cleaner.clean_html
remove_rendundant_html_spans = cleaner.remove_rendundant_html_spans