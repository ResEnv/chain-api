'''This is a simple library for managing HAL documents'''


class AttrDict(dict):
    '''An AttrDict is just a dictionary that allows access using object
    attributes. For instance d['attr1'] is made available as d.attr1'''

    def __init__(self, *args):
        dict.__init__(self, *args)
        for k, v in self.iteritems():
            setattr(self, k, v)

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)
        setattr(self, k, v)


class HALLink(AttrDict):
    def __init__(self, *args):
        AttrDict.__init__(self, *args)
        if 'href' not in self:
            raise ValueError(
                "Missing required href field in link: %s" % self)


class HALDoc(AttrDict):
    def __init__(self, *args):
        '''builds a HALDoc from a python dictionary. A HALDoc can also be
        treated as a standard dict to access the raw data'''
        AttrDict.__init__(self, *args)
        self.links = AttrDict()

        if '_links' in self:
            for rel, link in self['_links'].iteritems():
                if isinstance(link, list):
                    self.links[rel] = []
                    for link_item in link:
                        self.links[rel].append(HALLink(link_item))
                else:
                    self.links[rel] = HALLink(link)
