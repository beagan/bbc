import os, sys
import datetime
from tempfile import mkstemp
from django.conf import settings
from django.db import models, connection
from django.db.models import signals
from django.db.models.fields import AutoField, DateTimeField, DateField, TimeField, FieldDoesNotExist
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField
#from django.dispatch import dispatcher

def hash_dict(dictionary):
    return hash(frozenset(dictionary.items()))

class BulkInsert(models.Manager):        
    def __init__(self):
        super(models.Manager, self).__init__()
        self.queue = {}
        self.order = {}
        #Special Handlers for Self Referencing Objects
        self.ref_queue = {}
        self.ref_order = {}
        self.ref_cache = {}

        self.related_fields = {}
        self.related_queue = {}
        self.related_classes = {}

        self.m2one_queue = {}
        self.m2one_fields = {}
        self.m2one_classes = {}

        self.m2m_queue = {}
        self.m2m_fields = {}
        self.m2m_classes = {}

        self.update_map = {}
        self.defaults = {}

        self.initialized = False
        self.now = datetime.datetime.now()

        if settings.DATABASE_ENGINE == 'mysql':
            self.backend = MySQL_BulkInsert()
        else:
            #dummy backend - does nothing
            self.backend = BulkInsertBackend()
        self.threshold = 1000
    def bulk_insert_now(self, now=None):
        if now is not None:
            self.now = now
        else:
            self.now = datetime.datetime.now()

        #Some default values may be invalidated by changing 'now'
        if self.initialized:
            self._collect_field_defaults()
        else:
            self._related_init()
    def bulk_insert_threshold(self, threshold=1000):
        self.threshold = threshold
    def bulk_insert(self, now=None, raw=False, clean_args=False, send_pre_save=True, _self_ref=False, **kwargs):
        """
        Hold kwargs in queue until bulk_insert_commit

        All field preprocessing is done unless raw=True
        Returns a hash for kwargs if clean_args=True
          Primarily for internal use
        Sends pre_save signal unless send_pre_save=False

        kwargs can include any field from the underlying model including any related_name's
        specified by related models

        """
        if not self.initialized:
            #Initialize is delayed until bulk_insert is first called to ensure
            #that all relationship hooks have been added to the underlying class
            self._related_init()
            self.tempModel = self.model()

        if now is not None:
            if now != self.now:
                self.now = now
                self._collect_field_defaults()

        #check for valid field names
        self._check_fields(kwargs=kwargs)

        #Determine which related fields are present
        fk_or_one2one = set(kwargs.keys()).intersection(set(self.related_fields.keys()))
        many_to_one = set(kwargs.keys()).intersection(set(self.m2one_fields.keys()))
        many_to_many = set(kwargs.keys()).intersection(set(self.m2m_fields.keys()))

        #pop off m2m and m2one names, the tempModel can't handle them
        m2m_dict = {}
        for name in many_to_many:
            m2m_dict[name] = kwargs.pop(name)

        m2one_dict = {}
        for name in many_to_one:
            m2one_dict[name] = kwargs.pop(name)

        #Pop off Foreign Key and OneToOne names if they need to be bulk inserted first
        related = []
        for name in fk_or_one2one:
            if isinstance(kwargs[name], dict):
                manager = self._find_bulk_manager(self.related_classes[name])
                sref = self.related_classes[name] == self.model
                arg_hash = manager.bulk_insert(now=self.now, clean_args=True, _self_ref=sref, **kwargs[name])
                related += [(name, arg_hash)]

                kwargs.pop(name)
            elif isinstance(kwargs[name], self.related_classes[name]) and getattr(kwargs[name], kwargs[name]._meta.pk.attname) is None:
                args = self._generate_args(kwargs[name])
                manager = self._find_bulk_manager(self.related_classes[name])
                sref = self.related_classes[name] == self.model
                arg_hash = manager.bulk_insert(now=self.now, clean_args=True, _self_ref=sref, **args)
                related += [(name, arg_hash)]

                kwargs.pop(name)


        #Temporary model for signal dispatch and field preprocessing
        #self.tempModel = self.model()
        for name in kwargs.keys():
            field = self.tempModel._meta.get_field(name)
            if isinstance(field, ForeignKey) and isinstance(kwargs[name], int) or isinstance(kwargs[name], long):
                setattr(self.tempModel, field.attname, kwargs[name])
                continue
            setattr(self.tempModel, field.name, kwargs[name])

        #Preprocess field data unless 'raw' specified on call
        #Special handling for defaults on date and time fields to ensure
        #proper formatting for primary key recovery
        watch = {}
        for f in self.tempModel._meta.fields:
            val = getattr(self.tempModel, f.attname)
            watch[f.name] = val
            if isinstance(f, AutoField):
                if f.name in kwargs.keys():
                    kwargs[f.name] = f.get_db_prep_save(raw and val or f.pre_save(self.tempModel, True))
            elif f.name in kwargs.keys():
                kwargs[f.name] = f.get_db_prep_save(raw and val or f.pre_save(self.tempModel, True))
            else:
                kwargs[f.name] = self.defaults[f.name]

        #Presave could be called more than once for the same object
        if send_pre_save:
            dispatcher.send(signal=signals.pre_save, sender=self.tempModel.__class__, instance=self.tempModel)

        #Check for changes from pre_save
        for f in [field for field in self.tempModel._meta.fields if field.name in kwargs]:
            if watch[f.name] != getattr(self.tempModel, f.attname):
                kwargs[f.name] = f.get_db_prep_save(raw and val or f.pre_save(self.tempModel, True))

        #hash to identify this arg:value set
        key = hash_dict(kwargs)

        #Objects with the same arg:value signature are considered
        #the same object
        if _self_ref:
            if key not in self.ref_queue:
                self.ref_queue[key] = kwargs
                self.ref_order[key] = len(self.ref_queue)
        elif key not in self.queue:
            self.queue[key] = kwargs
            self.order[key] = len(self.queue)

        #With the key computed, associate it with any Fk's and one2one's
        #that will be inserted later
        for name, arg_hash in related:
            if arg_hash not in self.related_queue[name]:
                self.related_queue[name][arg_hash] = []
            self.related_queue[name][arg_hash] += [key]

        for name in many_to_one:
            self._m2one_enqueue(name, m2one_dict[name], key)

        for name in many_to_many:
            self._m2m_enqueue(name, m2m_dict[name], key)

        #tempModel = None
        self._clear_tempModel()
        if clean_args:
            return key
    def _clear_tempModel(self):
        for field in self.tempModel._meta.fields:
            val = field.get_default()
            setattr(self.tempModel, field.attname, val)

    def bulk_insert_commit(self, now=None, autoclobber=False, depth=0, max_depth=5, send_post_save=True, _self_ref=False, **kwargs):
        """
        Bulk inserts all queued objects and relations to the database with one insert per affected table
        and N/100 selects to find the primary keys where N is the number of inserted rows

        If autoclobber is False, the default, the insert is performed with IGNORE.  Any object that duplicates one
        already in the database is not reinserted but any new relationships will be

        if autoclobber is True, the insert is performed with REPLACE, clobbering any duplicates

        If autoclobber is None, no checking is done and any duplicates will raise a Database Integrity Error

        If kwargs is specified, its values are used to overide any model defaults
        """
        if not self.queue or depth > max_depth:
            return {}

        self._check_fields(no_related=True, kwargs=kwargs)

        many_to_many = filter(lambda x: x['list'] != [], self.m2m_queue.values()) != []
        many_to_one = filter(lambda x: x != [], self.m2one_queue.values()) != []
        related = filter(lambda x: x != [], self.related_queue.values()) != []

        m2m_depth = filter(lambda x: x['bulk'], self.m2m_queue.values())
        try:
            if not _self_ref:
                #Foreign Key and OneToOne are inserted first
                #Their primary keys are needed to save the root objects
                if related:
                    self._fk_one2one_insert(depth, max_depth, autoclobber)

                    #inserting a fk or one2one invalidates our kwargs signatures
                    #computing new hashes and mapping to the old hash for m2m and m2one
                    copy = {}
                    order_copy = {}
                    self.update_map = {}
                    for key, value in self.queue.items():
                        new_key = hash_dict(value)
                        self.update_map[key] = new_key
                        copy[new_key] = value
                        try:
                            order_copy[new_key] = self.order[key]
                        except KeyError:
                            #For nested inserts with self references, objects
                            #inserted across those references have no order information
                            order_copy[new_key] = sys.maxint
                    self.queue = copy
                    self.order = order_copy


                order = self.order.items()
                order.sort(lambda x,y: x[1] - y[1])
            else:
                #Related Self References are bunched together and inserted once
                #however, commit will be called for every self referencing field
                #If the commit has already been done, return the cached queue
                if not self.ref_queue:
                    return self.ref_cache, self.update_map
                order = self.ref_order.items()
                order.sort(lambda x,y: x[1] - y[1])

            #Saving the root objects
            queue = _self_ref and self.ref_queue or self.queue
            if len(queue) <= self.threshold or self.threshold < 0:
                self.backend.insert(table=self.model._meta.db_table,
                                    fields=[f for f in self.model._meta.fields if not isinstance(f, AutoField)],
                                    queue=queue,
                                    order = order,
                                    autoclobber=autoclobber)
            else:
                self.backend.write_temp_file(fields=[f for f in self.model._meta.fields if not isinstance(f, AutoField)],
                                            queue=queue)

                self.backend.insert_from_file(table=self.model._meta.db_table, 
                                            columns=[f.column for f in self.model._meta.fields if not isinstance(f, AutoField)], 
                                            autoclobber=autoclobber)


            self._recover_pks(_self_ref)

            if not _self_ref:
                if many_to_many:
                    self._many_to_many_insert(depth, max_depth, autoclobber)
                if many_to_one:
                    self._many_to_one_insert(depth, max_depth, autoclobber)

        except Exception, e:
            self.reset()
            raise Exception, e

        #Dispatch Post Save Signals
        if send_post_save:
            values = _self_ref and self.ref_queue.values() or self.queue.values()
            for args in values:
                for name in args.keys():
                    setattr(self.tempModel, self.tempModel._meta.get_field(name).attname, args[name])
                dispatcher.send(signal=signals.post_save, sender=self.tempModel.__class__, instance=self.tempModel)
                self._clear_tempModel()

        if depth > 0:
            queue = dict(_self_ref and self.ref_queue or self.queue)
            update_map = self.update_map
            self.reset(_self_ref)
            if _self_ref:
                self.ref_cache = queue
            return queue, update_map
        self.reset()
        return {}, {}

    def reset(self, _self_ref=False):
        """
        Close and remove any temp files
        Reset all queues and field maps
        """
        if _self_ref:
            self.ref_queue = {}
            self.ref_order = {}
            self.backend.clear()
            return

        self.queue = {}
        self.ref_queue = {}
        for key in self.m2one_queue.keys():
            self.m2one_queue[key] = []
        for key in self.m2m_queue.keys():
            self.m2m_queue[key] = {'list':[], 'bulk':False}
        for key in self.related_queue.keys():
            self.related_queue[key] = {}
        self.update_map = {}
        self.order = {}
        self.ref_order = {}
        self.ref_cache = {}
        self.backend.clear()

    ###################
    # PRIVATE METHODS #
    ###################
    def _related_init(self):
        """
        Find all related forward and reverse Foreign Key, OneToOne,
        ManyToMany and ManyToOne relationships and cache the relevant
        fields and model classes
        """
        self.initialized = True
        for f in self.model._meta.fields:
            if isinstance(f, ForeignKey) or isinstance(f, OneToOneField):
                self.related_classes[f.name] = f.rel.to
                self.related_fields[f.name] = f
                self.related_queue[f.name] = {}

        for r in self.model._meta.get_all_related_objects():
            name = r.field.rel.related_name or r.model.__name__.lower() + '_set'
            self.m2one_classes[name] = r.model
            self.m2one_fields[name] = r.field
            self.m2one_queue[name] = []

        for f in self.model._meta.many_to_many:
            self.m2m_classes[f.name] = f.rel.to
            self.m2m_fields[f.name] = f
            self.m2m_queue[f.name] = {'list':[], 'bulk':False}

        for m2m in self.model._meta.get_all_related_many_to_many_objects():
            name = m2m.field.rel.related_name or m2m.model.__name__.lower() + '_set'
            self.m2m_classes[name] = m2m.model
            self.m2m_fields[name] = m2m.field
            self.m2m_queue[name] = {'list':[], 'bulk':False}

        self._collect_field_defaults()

    def _collect_field_defaults(self):
        """
        Collect default values for each field
        """
        self.defaults = {}
        scrapModel = self.model()
        for f in scrapModel._meta.fields:
            if isinstance(f, DateTimeField) or isinstance(f, DateField) or isinstance(f, TimeField):
                if (f.default == datetime.datetime.now or f.auto_now or f.auto_now_add):
                    if isinstance(f, DateTimeField):
                        self.defaults[f.name] = self.now.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(f, DateField):
                        self.defaults[f.name] = self.now.strftime('%Y-%m-%d')
                    elif isinstance(f, TimeField):
                        self.defaults[f.name] = self.now.strftime('%H:%M:%S')
                    continue
            if not isinstance(f, AutoField):
                self.defaults[f.name] = scrapModel._meta.get_field(f.name).get_db_prep_save(f.pre_save(scrapModel, True))

    def _check_fields(self, no_related=False, kwargs={}):
        """
        Check that all fields given to bulk_insert and bulk_insert_commit are valid
        """
        if no_related:
            valid_fields = set([f.name for f in self.model._meta.fields])
        else:
            valid_fields = set([f.name for f in self.model._meta.fields] + self.m2m_fields.keys() + self.m2one_fields.keys())
        invalid_fields = set(kwargs.keys()) - valid_fields

        assert len(invalid_fields) == 0, \
                    "Invalid field(s): %s . Acceptable field values: %s . All Arguments: %s" %\
                    (', '.join(invalid_fields), ', '.join(valid_fields), ', '.join([str(t) for t in kwargs.items()]))

    def _fk_one2one_insert(self, depth, max_depth, autoclobber):
        """
        Commit any related fk or one2one objects to the database
        Calls bulk_insert_commit on the related class
        """
        for name in self.related_queue.keys():
            if self.related_queue[name]:
                manager = self._find_bulk_manager(self.related_classes[name])
                self_ref = self.related_classes[name] == self.model
                r_queue, update_map = manager.bulk_insert_commit(now=self.now, depth=depth+1, 
                                                        max_depth=max_depth, autoclobber=autoclobber, _self_ref=self_ref)
                if r_queue:
                    pk_name = self.related_classes[name]._meta.pk.name

                    for arg_hash, keys in self.related_queue[name].items():
                        arg_hash = update_map.get(arg_hash, arg_hash)
                        for key in keys:
                            try:
                                self.queue[key][name] = r_queue[arg_hash][pk_name]
                            except KeyError, e:
                                if key in self.ref_cache.keys():
                                    print >> sys.stderr , "Warning: Too many recursive self references on a Foreign Key or OneToOne field class:%s field:%s - Value NOT Saved" % (self.model, name)
                                else:
                                    raise KeyError, e

    def _many_to_one_insert(self, depth, max_depth, autoclobber):
        """
            Delayed bulk insert and commit of many to one relations
        """
        for name in self.m2one_queue.keys():
            manager = self._find_bulk_manager(self.m2one_classes[name])
            non_related_name = None
            for f in self.m2one_classes[name]._meta.fields:
                try:
                    if f.rel.related_name == name:
                        non_related_name = f.name
                        break
                except:
                    pass
            else:
                non_related_name = name + '_set'

            self_ref = self.m2one_classes[name] == self.model
            for args_list, key in self.m2one_queue[name]:
                key = self.update_map.get(key, key)
                pk = self.queue[key][self.model._meta.pk.name]
                for args in args_list:                      
                    args[non_related_name] = pk
                    manager.bulk_insert(now=self.now, _self_ref=self_ref, **args)
            manager.bulk_insert_commit(now=self.now, depth=depth+1, max_depth=max_depth, autoclobber=autoclobber, _self_ref=self_ref)

    def _many_to_many_insert(self, depth, max_depth, autoclobber):
        """
        Inserts all ManyToMany related objects and their relationships
        """
        for name in self.m2m_queue.keys():
            if self.m2m_queue[name]['bulk']:
                self_ref = self.m2m_classes[name] == self.model
                manager = self._find_bulk_manager(self.m2m_classes[name])
                r_queue, update_map = manager.bulk_insert_commit(now=self.now, depth=depth+1, max_depth=max_depth, autoclobber=autoclobber, _self_ref=self_ref)
                if r_queue:
                    for entry in self.m2m_queue[name]['list']:
                        for arg_hash in entry['bulk']:
                            entry['values'] += [r_queue[arg_hash][self.m2m_classes[name]._meta.pk.name]]
                else:
                    warning = "Max recursion depth, %s, exceeded. Some relationships between %s and %s may not be defined."
                    sys.stderr.write(warning % (max_depth, self.model.__name__, self.m2m_classes[name].__name__))

            if self.m2m_queue[name]['list']:
                table = self.m2m_fields[name].m2m_db_table()

                columns = [self.m2m_fields[name].m2m_column_name(), self.m2m_fields[name].m2m_reverse_name()]

                #Determine the direction of the ManyToMany Relationship
                #The special case of a self referential field requires further checking
                if self.m2m_fields[name].rel.to == self.model:
                    if self.m2m_classes[name] != self.model or not filter(lambda x: x.name==name, self.model._meta.many_to_many):
                        columns.reverse()

                #This value only matters for self referential relations
                symmetrical = False
                if self.m2m_classes[name] == self.model:
                    if getattr(self.m2m_fields[name].rel, 'symmetrical', False):
                        symmetrical = True
                    for key in self.ref_cache.keys():
                        self.queue[key] = self.ref_cache[key]


                if len(self.m2m_queue[name]['list']) <= self.threshold or self.threshold < 0:
                    self.backend.insert_m2m(table, self.model._meta.pk.name, 
                                            columns, self.queue, self.m2m_queue[name], 
                                            self.update_map, autoclobber, symmetrical)
                else:
                    self.backend.write_m2m_temp_file(self.model._meta.pk.name, self.queue, self.m2m_queue[name], self.update_map, symmetrical)

                    self.backend.insert_from_file(table, columns, autoclobber)


    def _recover_pks(self, _self_ref=False):
        """
        Store the recovered primary keys in the local queue
        Recover them 100 at a time
        """
        fields = [f for f in self.model._meta.fields if not isinstance(f, AutoField)]

        qn = connection.ops.quote_name
        cursor = connection.cursor()

        if self.model._meta.pk in fields:
            return #No keys to recover

        recovery_fields = fields + [self.model._meta.pk]

        table = self.model._meta.db_table
        primary = self.model._meta.pk

        pk_index = len(recovery_fields) - 1

        queue = _self_ref and self.ref_queue or self.queue

        recover_limit = 100
        start = 0
        for end in xrange(recover_limit, len(queue)+recover_limit, recover_limit):
            where = []
            query_data = []
            for kwargs in queue.values()[start:end]:
                temp = []
                for f in fields:
                    query_data += [kwargs[f.name]]
                    if kwargs[f.name] is None:
                        temp += ['%s is %%s' % (qn(f.column))]
                    else:
                        temp += ['%s = %%s' % (qn(f.column))]
                where += ['(' + ' AND '.join(temp) + ')']

            where = ' OR '.join(where)

            sql = "SELECT %s FROM %s WHERE " % \
                    (','.join(["%s.%s" % (qn(table), qn(f.column)) for f in recovery_fields]), qn(table)) + \
                    where + " ORDER BY %s" % qn(primary.column)

            cursor.execute(sql, query_data)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                temp = {}
                for f, r in zip(recovery_fields[:-1], row):
                    if isinstance(r, datetime.datetime):
                        r = r.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(r, datetime.date):
                        r = r.strftime('%Y-%m-%d')
                    elif isinstance(r, datetime.time):
                        r = r.strftime('%H:%M:%S')
                    temp[f.name] = r

                try:
                    queue[hash_dict(temp)][primary.name] = row[pk_index]
                except KeyError:
                    pass

            for q in queue.values()[start:end]:
                if primary.name not in q:
                    raise Exception, "Integrity Error. Object %s could not be inserted" % ', '.join([unicode(k).encode('utf8') + ' : ' + unicode(v).encode('utf8') for k,v in q.items()])

            start = end

    def _find_bulk_manager(self, cls):
        """
        Locate a bulk manager on a related class
        If there isn't one, add one
        """
        for attr in dir(cls):
            try:
                m = getattr(cls, attr)
                if isinstance(m, self.__class__):
                    m.bulk_insert_threshold(self.threshold)
                    return getattr(cls, attr)
            except:
                pass

        cls.add_to_class('_bulk_manager', self.__class__())
        cls._bulk_manager.bulk_insert_threshold(self.threshold)
        return cls._bulk_manager

    def _m2one_enqueue(self, name, value, key):
        """
        Queue for the many side of ManyToOne relationships
        Can't do anything with them until the primary key for
        the root side is available
        """
        if not isinstance(value, list):
            value = [value]
        self.m2one_queue[name] += [(value, key)]

    def _generate_args(self, obj):
        """
        If we have been supplied a model object with no primary key,
        convert it into a kwargs dictionary
        """
        args = {}
        for f in obj._meta.fields:
            if isinstance(f, AutoField):
                continue
            args[f.name] = f.get_db_prep_save(f.pre_save(obj, True))
        return args

    def _m2m_enqueue(self, name, value, key):
        """
        ManyToMany Queue
        This handles dicts of args, integer ids, and model objects with or without primary keys
        Or a list with any combination of the above
        """
        cls = self.m2m_classes[name]
        bulk = []
        self_ref = cls == self.model
        pk = self.model._meta.pk.name
        if not isinstance(value, list):
            value = [value]
        new_value = []
        for v in value:
            if isinstance(v, dict):
                if v.get(pk, None):
                    new_value += [v[pk]]
                manager = self._find_bulk_manager(cls)
                bulk += [manager.bulk_insert(now=self.now, clean_args=True, _self_ref=self_ref, **v)]
            elif isinstance(v, cls):
                if getattr(v, pk, None) is None:
                    args = self._generate_args(v)
                    manager = self._find_bulk_manager(cls)
                    bulk = [manager.bulk_insert(now=self.now, clean_args=True, _self_ref=self_ref, **args)]
                else:
                    new_value += [getattr(v, pk)]
            elif isinstance(value, (int,long)):
                new_value += [long(v)]
            else:
                raise ValueError, "ManyToMany list argument, %s=%s, must contain numbers, dicts or instances of %s" %\
                            (name, value, cls.__name__)

        if bulk:
            self.m2m_queue[name]['bulk'] = True
        self.m2m_queue[name]['list'] += [{'values':new_value, 'key':key, 'bulk':bulk}]

class BulkInsertBackend(object):
    def __init__(self):
        self.temp_file = None
    def write_temp_file(self, fields, queue):
        pass
    def write_m2m_temp_file(self, primary_key_name, queue, m2m_queue, update_map, symmetrical):
        pass
    def insert_from_file(self, table, columns, autoclobber=False):
        pass
    def insert(self, table, columns, autoclobber=False):
        pass
    def insert_m2m(self, table, primary_key_name, columns, queue, m2m_queue, update_map, autoclobber, symmetrical):
        pass
    def clear(self):
        try:
            os.close(self.temp_file[0])
        except:
            pass
        try:
            os.remove(self.temp_file[1])
        except:
            pass

class MySQL_BulkInsert(BulkInsertBackend):
    def write_temp_file(self, fields, queue):
        """
        Creates and writes input file for LOAD DATA INSERT
        Used everywhere except for saving ManyToMany relationships
        """
        #Tab delimited fields, newlines mark rows
        self.temp_file = mkstemp(suffix='.import', prefix='bulk', 
                        dir=getattr(settings, 'BULK_INSERT_DIR', '.'))
        assert self.temp_file is not None
        fh, path = self.temp_file
        line = u'\t'.join(["%s"] * len(fields))
        for kwargs in queue.values():
            values = []
            for f in fields:
                val = kwargs[f.name] is None and u'\\N' or unicode(kwargs[f.name]).replace(u'\t', u'\\t').replace(u'\n', u'\\n')

                values.append(val)

            out = line % tuple(values) + u'\n'
            os.write(fh, out.encode('utf8'))


        os.close(fh)
        os.chmod(path, 0100644)

    def write_m2m_temp_file(self, primary_key_name, queue, m2m_queue, update_map, symmetrical):
        """
        Creates and writes ManyToMany relationship input file for LOAD DATA INSERT
        """

        #Tab delimited fields, newlines mark rows
        #Write to the file incrementally
        self.temp_file = mkstemp(suffix='.import', prefix='bulk', 
                        dir=getattr(settings, 'BULK_INSERT_DIR', '.'))
        assert self.temp_file is not None
        fh, path = self.temp_file
        line = u'\t'.join(["%s"] * 2)
        for obj in m2m_queue['list']:
            for value in obj['values']:
                key = obj['key']
                if key in update_map:
                    key = update_map[key]
                out = line % (queue[key][primary_key_name], value) + u'\n'
                if symmetrical:
                    out += line % (value, queue[key][primary_key_name]) + u'\n'                 
                os.write(fh, out.encode('utf8'))

        os.close(fh)
        os.chmod(path, 0100644)

    def insert_from_file(self, table, columns, autoclobber=False):
        """
        executes LOAD DATA INFILE
        Inserts Data from temp file created by write_temp_file
        or write_m2m_temp_file

        """
        qn = connection.ops.quote_name
        cursor = connection.cursor()

        if autoclobber is None:
            autoclobber = ''
        else:
            autoclobber = autoclobber and 'REPLACE' or 'IGNORE'

        query = "LOAD DATA INFILE '%s' %s INTO TABLE %s (%s)" % \
                (self.temp_file[1], autoclobber, qn(table), 
                ','.join([qn(c) for c in columns]))
        cursor.execute(query)

        os.remove(self.temp_file[1])

    def insert_m2m(self, table, primary_key_name, columns, queue, m2m_queue, update_map, autoclobber, symmetrical):
        qn = connection.ops.quote_name
        cursor = connection.cursor()    

        if autoclobber is None or autoclobber == True:
            autoclobber = ''
        else:
            autoclobber = 'IGNORE'

        sql = u'INSERT %s INTO %s (%s) ' % \
                (autoclobber, qn(table), ', '.join([qn(c) for c in columns]))

        value_list = []
        for obj in m2m_queue['list']:
            for value in obj['values']:
                key = update_map.get(obj['key'], obj['key'])

                value_list += [queue[key][primary_key_name], value]

                if symmetrical:
                    value_list += [value, queue[key][primary_key_name]]

        arg_string = ', '.join([u'(' + ','.join(['%s']*2) + ')'] * (len(value_list)/2))
        values = 'VALUES %s' % arg_string
        sql = sql + values

        cursor.execute(sql, value_list)
    def insert(self, table, fields, queue, order, autoclobber=False):
        """
        Bulk insert using INSERT
        ***Limited by max packet size on mysql server***
        """
        qn = connection.ops.quote_name
        cursor = connection.cursor()

        if autoclobber is None or autoclobber == True:
            autoclobber = ''
        else:
            autoclobber = 'IGNORE'

        sql = u'INSERT %s INTO %s (%s) ' % \
                (autoclobber, qn(table), ', '.join([qn(f.column) for f in fields]))

        value_list = []
        for key, order in order:
            kwargs = queue[key]
            value_list += [kwargs[f.name] for f in fields]

        arg_string = ', '.join([u'(' + ','.join(['%s']*len(fields)) + ')'] * len(queue.values()))
        values = 'VALUES %s' % arg_string

        sql = sql + values

        cursor.execute(sql, value_list)