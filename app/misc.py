
def unicode2str(obj):
    if isinstance(obj,dict):
        new_dict = {}
        for k,v in obj.iteritems():
            new_dict[unicode2str(k)] = unicode2str(v)
        return new_dict
    elif isinstance(obj, list):
        new_list = [ unicode2str(i) for i in obj]
        return new_list
    elif isinstance(obj,unicode):
        return str(obj)
    else:
        return obj 