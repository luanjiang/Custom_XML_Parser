
# coding: utf-8

# In[1]:

import re
import requests


# In[3]:

test_snippet = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xml> <!-- not actually valid xml-->
<!-- This is a comment -->
<note date="8/31/12">
    <to>Tove</to>
    <from>Jani</from>
    <heading type="Reminder"/>
    <body>Don't forget me this weekend!</body>
    <!-- This is a multiline comment,
         which take a bit of care to parse -->
</note>
"""


# In[30]:

class XMLNode:
    def __init__(self, tag, attributes, raw_content):
        """ Initialize an XML tree with the supplied root tag and attributes,
        plus content.        
        Args:
            - tag (string): string indicating the tag type of this node
            - attributes (dictionary): dictionary of
            attribute_name/attribute_value pairs
            - raw_content (string): all content in the file that comes 
            _after_ the tag
            
        Attributes:
            - tag (string): a copy of the string indicating the node tag
            - attributes (dictionary): a copy of the attributes passed to the 
            initializer
            - content (string): a string that contains the content just within
            this tag.  Note that this is _different_ from the "content" variable
            passed to the content passed to the initializer; that variable has
            to contain the content after the tag, but which may go to the end of
            the file, while after initializer, the content attribute of the
            class must contain _just_ the content within that tag.
            - children (list): a list of all child nodes of this XML node, in
            the order that they occur in the file.
        """
        self.tag = tag
        self.attributes = attributes
        self.children = []
    
        
        tag_pattern=re.compile('<')
        comment_pattern = re.compile(r'(<!--\s*.*?\s*-->)', re.DOTALL)
        xml_prolog_pt = re.compile(r'(<\?.*?\?>)')
        html_prolog_pt = re.compile(r'(<![a-zA-Z0-9_\s]*?>)')
        tag_open_pt = re.compile(r'(<[a-zA-Z0-9_]+[^/\s]?[^<]*>)')
        tag_close_pt = re.compile(r'(</[a-zA-Z0-9_]+[^\s]?[^<]*>)')
        tag_open_close_pt=re.compile(r'(<[^><\s]+\s*[^<>]*/>)')
        tag_open = re.compile(r'(?<=<)([a-zA-Z0-9_]+[^/\s]?)([^<]*)(?=>)')
        tag_close = re.compile(r'(?<=</)([a-zA-Z0-9_]+[^\s]?)([^<]*)(?=>)')
        tag_open_close = re.compile(r'(?<=<)([^><\s]+)\s*([^<>]*)(?=/>)')
        self.parent_skip_over_len=0
        match= tag_pattern.search(raw_content)
        if match != None:
            current_pos=match.start()
            found_valid_tag=False 
            #while (found_valid_tag== False): #valid_tag will be True when it is open or close tag
            while(tag_pattern.search(raw_content[(current_pos):]) != None):
                if comment_pattern.search(raw_content[current_pos:]) != None:
                    if comment_pattern.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start(): 
                        current_pos=current_pos+ comment_pattern.search(raw_content[current_pos:]).end()
                if xml_prolog_pt.search(raw_content[current_pos:]) != None:
                    if xml_prolog_pt.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start():
                        current_pos=current_pos+ xml_prolog_pt.search(raw_content[current_pos:]).end()
                if html_prolog_pt.search(raw_content[current_pos:]) != None:
                    if html_prolog_pt.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start():
                        current_pos=current_pos+ html_prolog_pt.search(raw_content[current_pos:]).end()
                match1=tag_pattern.search(raw_content[current_pos:])
                if match1 != None: #see if there are any remaining < left
                    current_pos=current_pos+ match1.start()
                    if tag_open_pt.search(raw_content[current_pos:])!=None:
                        if tag_open_pt.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start():
                            found_valid_tag=True
                            # found open tag, now extract its tag name and attributes
                            child_tag= tag_open.findall(raw_content[current_pos:])[0][0]
                            child_attributes=tag_open.findall(raw_content[current_pos:])[0][1]
                            child_attr_dict={}
                            if re.search(" ", child_attributes) != None:
                                for i in range(len(child_attributes.split(" "))):
                                    stuff=child_attributes.split(" ")[i]
                                    if re.search('''="''', stuff) != None:
                                        key=stuff.split('''="''')[0]
                                        value=stuff.split('''="''')[1]
                                        value=value[:-1]
                                        child_attr_dict[key]=value
                                    elif re.search("='", stuff) != None:
                                        key=stuff.split("='")[0]
                                        value=stuff.split("='")[1]
                                        value=value[:-1]
                                        child_attr_dict[key]=value 
                            else:
                                if re.search('''="''', child_attributes) != None:
                                    key=child_attributes.split('''="''')[0]
                                    value=child_attributes.split('''="''')[1]
                                    value=value[:-1]
                                    child_attr_dict[key]=value
                                elif re.search("='", child_attributes) != None:
                                    key=child_attributes.split("='")[0]
                                    value=child_attributes.split("='")[1]
                                    value=value[:-1]
                                    child_attr_dict[key]=value 
                            if tag_open_close_pt.search(raw_content[current_pos:])!=None:
                                # remaining content has open close tag, now check if it starts with open close tag
                                if tag_open_close_pt.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start():
                                    child_tag= tag_open_close.findall(raw_content[current_pos:])[0][0]
                                    child_attributes=tag_open_close.findall(raw_content[current_pos:])[0][1]
                                    child_attr_dict={}
                                    if re.search(" ", child_attributes) != None:
                                        for i in range(len(child_attributes.split(" "))):
                                            stuff=child_attributes.split(" ")[i]
                                            if re.search('''="''', stuff) != None:
                                                key=stuff.split('''="''')[0]
                                                value=stuff.split('''="''')[1]
                                                value=value[:-1]
                                                child_attr_dict[key]=value
                                            elif re.search("='", stuff) != None:
                                                key=stuff.split("='")[0]
                                                value=stuff.split("='")[1]
                                                value=value[:-1]
                                                child_attr_dict[key]=value 
                                    else:
                                        if re.search('''="''', child_attributes) != None:
                                            key=child_attributes.split('''="''')[0]
                                            value=child_attributes.split('''="''')[1]
                                            value=value[:-1]
                                            child_attr_dict[key]=value
                                        elif re.search("='", child_attributes) != None:
                                            key=child_attributes.split("='")[0]
                                            value=child_attributes.split("='")[1]
                                            value=value[:-1]
                                            child_attr_dict[key]=value  
                                    
                                    
                                    self.children.append(XMLNode(child_tag, child_attr_dict, ''))
                                    current_pos=current_pos+tag_open_close_pt.search(raw_content[current_pos:]).end()                                                         - tag_open_close_pt.search(raw_content[current_pos:]).start()
                                else: 
                                    child_open_end_pos=current_pos+                                                                   tag_open_pt.search(raw_content[current_pos:]).end() #the position where open tag ends           
                                    child=XMLNode(child_tag, child_attr_dict, raw_content[child_open_end_pos:])
                                    self.children.append(child)
                                    child_len=len(child.content)
                                    current_pos=child_open_end_pos + child_len+child.parent_skip_over_len
                            else: #no open close tag at all
                                child_open_end_pos=current_pos+                                                               tag_open_pt.search(raw_content[current_pos:]).end()   
                                child=XMLNode(child_tag, child_attr_dict, raw_content[child_open_end_pos:])
                                self.children.append(child)
                                child_len=len(child.content)
                                current_pos=child_open_end_pos + child_len+child.parent_skip_over_len
                    if tag_close_pt.search(raw_content[current_pos:])!=None:
                        if tag_close_pt.search(raw_content[current_pos:]).start()==tag_pattern.search(raw_content[current_pos:]).start():
                            found_valid_tag=True
                            self.parent_skip_over_len=tag_close_pt.search(raw_content[current_pos:]).end()                                                    - tag_close_pt.search(raw_content[current_pos:]).start()
                            if tag_close.findall(raw_content[current_pos:])[0][0] != tag:
                                raise Exception("Error: <{0}> tag closed with {1}".format(tag, tag_close.findall(raw_content[current_pos:])[0][0]))                
                            else:
                                child_close_beg_pos= current_pos+tag_close_pt.search(raw_content[current_pos:]).start()
                                current_level_content=raw_content[:child_close_beg_pos]
                                self.content=current_level_content
                                current_pos=child_close_beg_pos
                                current_pos=child_close_beg_pos +tag_close_pt.search(raw_content[current_pos:]).end()                                                    - tag_close_pt.search(raw_content[current_pos:]).start()
                                return
                    else: #the next < we found is not open or close tag, so it must be something weird
                         found_valid_tag=True
                else: 
                    found_valid_tag=True                
            self.content=raw_content
        else:
            self.content=raw_content


            
            
    def find(self, tag, **kwargs):
        """
        Search for a given tag and atributes anywhere in the XML tree
        
        Args:
        tag (string): tag to match
        kwargs (dictionary): list of attribute name / attribute value pairs to match
            
        Returns:
        (list): a list of XMLNode objects that match from anywhere in the tree
        """
        result_list = []
        if self.tag == tag and all(self.attributes[k]==v for k, v in kwargs.iteritems()):
            result_list.append(self)
        for child in self.children:
            result_list += child.find(tag, **kwargs)
        return result_list


# In[31]:

root = XMLNode("", {}, test_snippet)

print "root.tag: ", root.tag
print "root.attributes: ", root.attributes
print "root.content: ", repr(root.content)
print "root.children: ", root.children
print ""
print "note.tag: ", root.children[0].tag
print "note.attributes: ", root.children[0].attributes
print "note.content: ", repr(root.children[0].content)
print "note.children: ", root.children[0].children
print ""
print "to.tag: ", root.children[0].children[0].tag
print "to.attributes: ", root.children[0].children[0].attributes
print "to.content: ", repr(root.children[0].children[0].content)
print "to.children: ", root.children[0].children[0].children
print ""
print "heading.tag: ", root.children[0].children[2].tag
print "heading.attributes: ", root.children[0].children[2].attributes
print "heading.content: ", repr(root.children[0].children[2].content)
print "heading.children: ", root.children[0].children[2].children


# In[38]:

print root.find("body")[0].content

