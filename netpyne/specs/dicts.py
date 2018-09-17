"""
specs/dict.py
Contains Dict and ODict classes

Reproduce dict and OrderedDict behavior but add support to use object-like dot notation
e.g. cell.secs.soma.geom.diam

Contributors: salvadordura@gmail.com
"""

from collections import OrderedDict

# ----------------------------------------------------------------------------
# Dict class (allows dot notation for dicts)
# ----------------------------------------------------------------------------

class Dict(dict):

    __slots__ = []

    def __init__(*args, **kwargs):
        self = args[0]
        args = args[1:]
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            self.update(self.dotify(args[0]))
        if len(kwargs):
            self.update(self.dotify(kwargs))

    # only called if k not found in normal places
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)


    def todict(self):
        return self.undotify(self)

    def fromdict(self, d):
        d = self.dotify(d)
        for k,v in d.items():
            self[k] = v

    def __repr__(self):
        keys = list(self.keys())
        args = ', '.join(['%s: %r' % (key, self[key]) for key in keys])
        return '{%s}' % (args)


    def dotify(self, x):
        if isinstance(x, dict):
            return Dict( (k, self.dotify(v)) for k,v in x.items() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.dotify(v) for v in x )
        else:
            return x

    def undotify(self, x):
        if isinstance(x, dict):
            return dict( (k, self.undotify(v)) for k,v in x.items() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.undotify(v) for v in x )
        else:
            return x

    def __rename__(self, old, new, label=None):
        '''
        old (string): old dict key
        new (string): new dict key
        label (list/tuple of strings): nested keys pointing to dict with key to be replaced; 
            e.g. ('PYR', 'secs'); use None to replace root key; defaults to None 
        
        returns: True if successful, False otherwse
        '''
        obj = self
        if isinstance(label, (tuple, list)):
            for ip in range(len(label)):
                try:
                    obj = obj[label[ip]] 
                except:
                    return False 

        if old in obj:
            obj[new] = obj.pop(old)  # replace
            return True
        else:
            return False

    def rename(self, *args, **kwargs):
        self.__rename__(*args, **kwargs)

    def __missing__(self, key):
        if key and not key.startswith('_ipython'):
            value = self[key] = Dict()
            return value

    def __getstate__ (self):
        return self.todict()

    def __setstate__ (self, d):
        self = self.fromdict(d)


# ----------------------------------------------------------------------------
# ODict class (allows dot notation for ordered dicts)
# ----------------------------------------------------------------------------

class ODict(OrderedDict):

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(ODict, self).__init__(*args, **kwargs)

    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return super(ODict, self).__getattr__(k)
        except AttributeError:
            try:
                return super(ODict, self).__getitem__(k)
            except KeyError:
                raise AttributeError(k)


    def __setattr__(self, k, v):
        if k.startswith('_OrderedDict'):
            super(ODict, self).__setattr__(k,v)
        else:
            try:
                super(ODict, self).__setitem__(k,v)
            except:
                raise AttributeError(k)


    def __getitem__(self, k):
        return super(ODict, self).__getitem__(k)


    def __setitem__(self, k, v):
        super(ODict, self).__setitem__(k,v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                super(ODict, self).__delattr__(k)
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toOrderedDict(self):
        return self.undotify(self)

    def fromOrderedDict(self, d):
        d = self.dotify(d)
        for k,v in d.items():
            self[k] = v

    def __repr__(self):
        keys = list(self.keys())
        args = ', '.join(['%s: %r' % (key, self[key]) for key in keys])
        return '{%s}' % (args)


    def dotify(self, x):
        if isinstance(x, OrderedDict):
            return ODict( (k, self.dotify(v)) for k,v in x.items() )
        elif isinstance(x, dict):
            return Dict( (k, self.dotify(v)) for k,v in x.items() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.dotify(v) for v in x )
        else:
            return x

    def undotify(self, x):
        if isinstance(x, OrderedDict):
            return OrderedDict( (k, self.undotify(v)) for k,v in x.items() )
        elif isinstance(x, dict):
            return dict( (k, self.undotify(v)) for k,v in x.items() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.undotify(v) for v in x )
        else:
            return x

    def __rename__(self, old, new, label=None):
        '''
        old (string): old dict key
        new (string): new dict key
        label (list/tuple of strings): nested keys pointing to dict with key to be replaced; 
            e.g. ('PYR', 'secs'); use None to replace root key; defaults to None 
        
        returns: True if successful, False otherwse
        '''
        obj = self
        if isinstance(label, (tuple, list)):
            for ip in range(len(label)):
                try:
                    obj = obj[label[ip]] 
                except:
                    return False 

        if old in obj:
            obj[new] = obj.pop(old)  # replace
            return True
        else:
            return False

    def rename(self, *args, **kwargs):
        self.__rename__(*args, **kwargs)
        
    def __getstate__ (self):
        return self.toOrderedDict()

    def __setstate__ (self, d):
        self = self.fromOrderedDict(d)


