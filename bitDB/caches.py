import json
from bitDB.models import Element

#The class CacheForViewDB is needed exclusively for displaying the database.
#In order to during render() not to request to DB.
#The class CacheForViewDB is the parent of the class CacheForViewCache
#that performs the main work.
class CacheForViewDB():
    def __init__(self, *args, **kwargs):
        self.file_cache = "cache_for_view_DB.json"
        self.tree = None
        self._get_data()

    def update_data(self):
        tree=Treelist(list(Element.objects.values('id','value','parentID',
                                                  'level','status')))
        self.tree= tree.dry_list
        with open(self.file_cache, "w") as write_file:
            json.dump(self.tree, write_file)

    def _get_data(self):
        with open(self.file_cache, "r") as read_file:
	        self.tree = json.load(read_file)

    def get_choicelist(self):
        choicelist = []
        if self.tree is not None:
            for e in self.tree:
                if e['status']==False:
                    action='removed: '
                else:
                    action=''
                S1=' - '
                option_label=(S1*e['level']+action+e['value']+'   '
                              +'(id= '+str(e['id'])+')')
                choicelist.append([e['id'],option_label])
        return (tuple(choicelist))

    def check_element_is_removed (self,id):
        for e in self.tree:
            if (e['status']==False) and (e['id']==id):
                return True

class CacheForViewCache(CacheForViewDB):
    def __init__(self, *args, **kwargs):
        self.file_cache = "cache_for_view_cache.json"
        self.tree = None
        self._get_data()

    def _record_tree(self):
        with open(self.file_cache, "w") as write_file:
            json.dump(self.tree, write_file)

    def _find_lastID(self):
        with open("root_lastid.json", "r") as read_file:
	        list_json = json.load(read_file)
        lastID=list_json[0]['lastID']
        for e in self.tree:
            if e['lastID']>lastID:
                lastID=e['lastID']
        return lastID

    def _check_parent_and_record(self):
        tree=Treelist(self.tree)
        self.tree=tree.dry_list
        for e in self.tree:
            action_parent=None
            for k in self.tree:
                if k['id']==e['parentID']:
                    action_parent=k['action']
            if (action_parent=='delete') and e['status'] and (e['action']=='add'):
                e['action']='delete'
                e['status']=False
            elif (action_parent=='delete') and e['status'] and (e['action']!='add'):
                e['action']='delete'
        self._record_tree()

    def transfer_data(self, elementID):
        dict_element={}
        #!!!!! Database request
        element_obj = Element.objects.get(id=elementID)
        last_element_obj=Element.objects.latest('id')
        #!!!!!
        dict_element['id']=element_obj.id
        dict_element['value']=element_obj.value
        dict_element['parentID']=element_obj.parentID
        dict_element['level']=element_obj.level
        dict_element['status']=element_obj.status
        dict_element['lastID']=last_element_obj.id
        dict_element['action']='None'
        self.tree.append(dict_element)
        self._check_parent_and_record()

    def reset_data(self):
        with open('reset_cache_DB.json', "r") as read_file:
	        self.tree = json.load(read_file)
        #!!!!! Database request
        Element.objects.all().delete()
        for e in self.tree:
            element_obj=Element()
            element_obj.save_instance(instance=e)
        #!!!!!
        cache_DB=CacheForViewDB()
        cache_DB.update_data()
        self.tree=[]
        with open(self.file_cache, "w") as write_file:
            json.dump(self.tree, write_file)
        with open('root_lastID', "w") as write_file:
            json.dump([{"lastID": 9}], write_file)

    def add_data(self, parent_elementID, value):
        lastID=self._find_lastID()
        dict_element={}
        dict_element['id']=lastID+1
        dict_element['value']=value
        dict_element['parentID']=parent_elementID
        dict_element['level']=0
        dict_element['status']=True
        dict_element['lastID']=lastID+1
        dict_element['action']='add'
        self.tree.append(dict_element)
        self._check_parent_and_record()

    def delete_data (self, elementID):
        for e in self.tree:
            if elementID==e['id']:
                if e['action']=='add':
                    e['action']='delete'
                    e['status']=False
                else:
                    e['action']='delete'
                break
        self._check_parent_and_record()

    def change_data(self, elementID, value):
        for e in self.tree:
            if elementID==e['id']:
                e['value']=value
                e['action']='change'
                break
        self._record_tree()

    def apply_data(self):
        #!!!!! Database request
        tree_DB=Treelist(list(Element.objects.values('id','value','parentID',
                                                     'level','status')))
        #!!!!!
        #tree_DB.dry_list - this is a tree list from the Database.
        #Add an 'action' field to the list tree_DB.dry_list
        for d in tree_DB.dry_list:
            d['action']=None
        #Assign an action for each element in the list - tree_DB.dry_list.
        #And create a list tmp_add_list for further addition.
        tmp_add_list=[]
        for c in self.tree:
            if c['action']=='add':
                tmp_add_list.append(c)
            else:
                for d in tree_DB.dry_list:
                    if c['id']==d['id']:
                        if (c['action']=='delete') and (c['status']):
                            d['action']='delete'
                            c['status']=False
                        elif c['action']=='change':
                            d['value']=c['value']
                            d['action']='change'
        #Add tmp_add_list in tree_DB.dry_list
        for e in tmp_add_list:
            tree_DB.dry_list.append(e)
        #Сreate a tree again
        tree_DB=Treelist(tree_DB.dry_list)
        #Looks at the tree. What other elements need to be removed.
        for e in tree_DB.dry_list:
            action_parent=None
            for k in tree_DB.dry_list:
                if k['id']==e['parentID']:
                    action_parent=k['action']
            if (action_parent=='delete') and e['status'] and (e['action']=='add'):
                e['action']='delete'
                e['status']=False
            elif (action_parent=='delete') and e['status'] and (e['action']!='add'):
                e['action']='delete'
        #Only now changes the status of deleted elements.
        for e in tree_DB.dry_list:
            if e['action']=='delete':
                e['status']=False
        #!!!!!!!!!!!!!!!
        #Apply all changes to the Database.
        for e in tree_DB.dry_list:
            element_obj=Element()
            if e['action'] is not None :
                element_obj.save_instance(instance=e)
        cache_db=CacheForViewDB()
        cache_db.update_data()
        #!!!!!!!!!!!!!!!
        #Find and write to the file ID of the last element.
        lastID=self._find_lastID()
        with open('root_lastID', "w") as write_file:
            json.dump([{"lastID": lastID}], write_file)
        #And clean the cache.
        self.tree=[e for e in self.tree if e['status']==False]
        self._record_tree()

    #This function for validation Form_DB
    def check_id_in_cache(self,id):
        for e in self.tree:
            if (e['id']==id):
                return True

    #This function for validation Form_cache
    def check_element_is_delete (self,id):
        for e in self.tree:
            if (e['action']=='delete') and (e['id']==id):
                return True

    #This function for field 'choise element' of Form_cache
    def get_choicelist(self):
        choicelist = []
        action=''
        if self.tree is not None:
            for e in self.tree:
                S1=' - '
                if e['status']==False:
                    action='removed: '
                elif e['action']=='add':
                    action=' Add: '
                elif e['action']=='delete':
                    action=' Del: '
                elif e['action']=='change':
                    action=' Ch: '
                else:
                    action=''
                option_label=(S1*e['level']+action+e['value']+'   '
                              +'(id= '+str(e['id'])+')')
                choicelist.append([e['id'],option_label])
        return (tuple(choicelist))

#The Treelist class is needed to build a tree of elements in a views.
class Treelist():
    def __init__(self, wet_list):
        wet_list.sort(key=lambda d: (d['id']))
        self.wet_list = wet_list
        self.dry_list=[]
        self.list_ID, self.list_parentID = self._lists_ID()
        self.list_ID_without_parent=self._without_parent()
        n=len(self.wet_list)
        self._tree(n)

    def _lists_ID(self):
        list_ID=[]
        list_parentID=[]
        for e in self.wet_list:
            list_ID.append(e['id'])
            list_parentID.append(e['parentID'])
        return list_ID, list_parentID

    def _without_parent(self):
            return set(self.list_parentID).difference(set(self.list_ID))

    def _tree(self, n):
        if n>0:
            e=self.wet_list[0]
            if e['parentID'] in self.list_ID_without_parent:
                e['level']=0
                self.dry_list.append(e)
            else:
                j=0
                for k in self.dry_list:
                    if e['parentID']==k['id']:
                        e['level']=k['level']+1
                        self.dry_list.insert(j+1,e)
                        break
                    else:
                        j=j+1
            self.wet_list.remove(e)
            n=len(self.wet_list)
            self._tree(n)
