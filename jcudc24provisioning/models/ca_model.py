"""
Transparently provides additional functionallity to all ColanderAlchemy models including:
- Updating the model from a Deform appstruct.
- Converting the model to a Deform appstruct
- Copverting the model to XML
"""

from datetime import date
from lxml import etree
import logging

import colander
from colanderalchemy.types import SQLAlchemyMapping
import deform
from jcudc24provisioning.controllers.ca_schema_scripts import fix_schema_field_name, convert_schema


logger = logging.getLogger(__name__)

__author__ = 'Casey Bajema'

class CAModel(object):
    """
    Transparently provides additional functionallity to all ColanderAlchemy models. This functionality is provided by
    making all ColanderAlchemy models extend this class (must be the first class extended - eg. MyModel(CAModel, Base))
    """
    def __init__(self, appstruct=None, schema=None):
        """
        Create the model enforcing that all CAModel's have an id attribute as the primary key (used to provide extra
        functionality)

        :param appstruct: Optional data to initialise the model with, this allows creating a fully populated model from
                          a Deform appstruct.
        :param schema: Actual schema to use for extended functionality, the default is usually adequate.
        :return:
        """
        if not hasattr(self, 'id'):
            raise AttributeError("All CAModel's must have an 'id' unique identifier.")

        self._schema = schema

        if appstruct is not None:
            self.update(appstruct)


    @property
    def schema(self):
        """
        Either return the schema set in the constructor (or from previous calls) or create the default ColanderAlchemy
        schema for this model type.

        :return: This models Deform schema.
        """
        if '_schema' not in locals() or self._schema is None:
            self._schema = convert_schema(SQLAlchemyMapping(type(self)))
        return self._schema

    def dictify(self, schema=None, force_not_empty_lists=False, dates_as_string=True, bool_false_as_none=True):
        """
        Convert this model into a Deform appstruct (dict)

        :param schema: Schema to use (this is primarily used for recursive calls).
        :param force_not_empty_lists: Force all lists/sequences to have at least 1 element.
        :param dates_as_string: Deform date widgets have some inconsistency with dates as objects or strings.
        :return: A deform compatible appstruct/dictionary with all data from this model.
        """
        if schema is None:
            schema = self.schema
        return self.convert_sqlalchemy_model_to_data(self, schema=schema, force_not_empty_lists=force_not_empty_lists,
            dates_as_string=dates_as_string, bool_false_as_none=bool_false_as_none)

    def update(self, appstruct):
        """
        Update this object with data in appstruct, the provided appstruct must be a deform compatible appstruct for
        this objects schema.

        :param appstruct: Data to update this object (compatible deform data for this objects schema)
        :return: Return either this object updated with the data or None if no update was made.
        """
        return self.create_sqlalchemy_model(appstruct, model_object=self) is not None
    
    def _get_field_type(self, field_name, model_object):
        """
        Read the schema to find out what type of data this field holds.  This is the python data type that represents
        this column.

        :param field_name:
        :param model_object:
        :return:
        """
        if hasattr(model_object, '_sa_class_manager'):
            class_manager = model_object._sa_class_manager[field_name]
            parent = getattr(class_manager, 'parententity', getattr(class_manager, '_parententity', None)) # Seems to have either or?
            if field_name not in parent.columns._data: # its a relationship with a value of none
                return None
            return parent.columns._data[field_name].type.python_type
        elif hasattr(model_object, '_schema'):
            for child in model_object._schema.children:
                if child.name == field_name:
                    if hasattr(child, 'python_type'):
                        return child.python_type
                    else:
                        return type(child.typ)

#        return model_object._sa_class_manager[field_name]._parententity.columns._data[field_name].type.python_type

    def _get_ca_registry(self, field_name, model_class):
        """
        Return the ColanderAlchemy registry for the passed in CAModel.  This is a helper function to retreive the data
        hidden within the class.

        :param field_name: Field/attribute to get ColanderAlchemy registry/attributes for.
        :param model_class: CAModel class to get the fields registry from.
        :return: The ca_registry for the identified field and class, a NotImplementedError will be thrown if the
                 registry can't be found.
        """
        try:
            ca_registry = None
            if hasattr(model_class, '_sa_class_manager') and field_name in model_class._sa_class_manager:
                if hasattr(model_class._sa_class_manager[field_name].comparator, 'mapper') and field_name in model_class._sa_class_manager[field_name].comparator.mapper.columns._data:
                    ca_registry = model_class._sa_class_manager[field_name].comparator.mapper.columns._data[field_name]._ca_registry
                elif hasattr(model_class._sa_class_manager[field_name], '_parententity') and field_name in model_class._sa_class_manager[field_name]._parententity.columns._data:
                    ca_registry = model_class._sa_class_manager[field_name]._parententity.columns._data[field_name]._ca_registry
                elif hasattr(model_class._sa_class_manager[field_name], '_parententity') and field_name in model_class._sa_class_manager[field_name]._parententity.relationships._data:
                    ca_registry = model_class._sa_class_manager[field_name]._parententity.relationships._data[field_name].ca_registry
                elif hasattr(model_class._sa_class_manager[field_name], 'property') and hasattr(model_class._sa_class_manager[field_name].property, 'ca_registry'):
                    ca_registry = model_class._sa_class_manager[field_name].property.ca_registry
                else:
                    raise NotImplementedError("ca_registry lookup for this object isn't implemented.")
    #                return None
            return ca_registry
        except Exception as e:
            logger.exception("Exception occurred while getting model's ca_registry: %s" % e)

#    def fileupload_to_filehandle(self, field_name, value, model_object):
#        try:
#            ca_registry = self._get_ca_registry(field_name, self.get_model_class(model_object))
#
#            # This isn't a form
#            if ca_registry is None:
#                return value
#
##            Handle file uploads
##            If this is a file field
#            if 'type' in ca_registry and isinstance(ca_registry['type'], deform.FileData):
#                # If this is a new file
#                if isinstance(value, dict) and 'preview_url' in value:
#                    value = str(value['preview_url'])
#
#                # If this is an already selected and uploaded file
#                elif isinstance(value, dict) and 'fp' in value and hasattr(value['fp'], 'name'):
#                    value = str(value['fp'].name)
#
#                # File was previously uploaded and the user just removed it
#                else:
#                    value = None
#
#            return value
#
#        except Exception as e:
#            logger.exception("Exception occurred while converting file upload to filehandle: %s" % e)

    def normalize_form_value(self, field_name, value, model_object):
        """
        Convert the value as returned from the HTML form to normalised python types (eg. colander.null -> None).

        :param field_name: Field that this value was retreived from (used to find the data type from the schema)
        :param value: Value to normalise
        :param model_object: Object that the value comes from.
        :return: normalised value
        """
        try:
            # Normalise values returned from forms
            if not isinstance(value, list) and not isinstance(value, dict):
                # Best attempt, cast all values to their required type
                field_type = self._get_field_type(field_name, model_object)
                if field_type == bool and (value == 'false' or not bool(value)):
                    value = False
                elif field_type == bool and (value == 'true' or bool(value)):
                    value = True
                elif value == colander.null or value == 'None' or value == 'colander.null' or isinstance(value, str) and value == '':
#                    field_type = self._get_field_type(field_name, model_object)
#                    if field_type in (int, float, long):
#                        value = 0
#                    else:
                    value = None

                if value is not None:
                    if issubclass(field_type, (int, long, float)):
                        try:
                            value = (field_type)(value)
                        except Exception as e:
                            value = field_type()    # Set the value to the default for its field type
                            logger.error("Error casting value (%s) to field type (%s) for %s of %s.  "
                                         "Value set to default (%s)." %
                                         (value, field_type, field_name, model_object.__class__, value))
                    elif issubclass(field_type, basestring):
                        if isinstance(value, unicode):
                            value = value.encode("utf-8")
                        else:
                            value = unicode(value, "utf-8")
    
#            elif (isinstance(value, dict) or value is None):
#                value = self.fileupload_to_filehandle(field_name, value, model_object)
    
            return value
        except Exception as e:
            logger.exception("Exception occurred while normalizing model value: %s" % e)

    def get_model_class(self, model_object):
        """
        Helper method for getting a CAModel's class from an object instance.

        :param model_object: Object to get the class for
        :return: The class that the pased in model represents.
        """
        if not hasattr(self, '_model_class'):
            self._model_class = model_object._sa_instance_state.class_
        return self._model_class


    def create_sqlalchemy_model(self, data, model_class=None, model_object=None):
        """
        Convert a deform appstruct into a CAModel object.

        :param data: Data to create the CAModel from.
        :param model_class: Optionally provide the model class (if the class isn't provided an object instance must be)
        :param model_object: Optionally provide the object instance (if the object isn't provided an class must be)
        :return: CAModel that has been created from the passed in data or None if the data caused no change.
        """
        is_data_empty = True
        if model_object is None and model_class is not None:
            model_object = model_class()

        if model_class is None and model_object is not None:
            model_class = self.get_model_class(model_object)

        if model_class is None or model_object is None:
            raise ValueError("Model class or model object could not be found while creating sqlalchemy model.")

        if data is None or not isinstance(data, dict) or len(data) <= 0:
            return None

        prefix = ''.join(str(x + ":") for x in data.items()[0][0].split(":")[:-1])
        new_model = True
        if model_object.id is not None and model_object.id >= 0:
            new_model = False
        elif prefix + 'id' in data and (isinstance(data[prefix + 'id'], (long, int)) or (isinstance(data[prefix + 'id'], basestring) and data[prefix + 'id'].isnumeric())) and long(data[prefix + 'id']) >= 0:
            new_model = False

        for field_name, value in data.items():
            field_name = fix_schema_field_name(field_name)

            # If this is a grouping - add its fields to the current model_object
            if not hasattr(model_object, field_name) and isinstance(value, dict): # NOTE: hasattr() WILL RETURN FALSE ON ANY EXCEPTION TO getattr() -> eg. wrong DB table fields.
                self.create_sqlalchemy_model(value, model_class=model_class, model_object=model_object)
            elif hasattr(model_object, field_name):
                # Fix form values to be the correct class and type and post formatting (eg. fileupload gets file handle from dict, bool is converted from 'false' to False, etc.).
                value = self.normalize_form_value(field_name, value, model_object)

                if isinstance(getattr(model_object, field_name), list) or isinstance(value, list):
                    # If the value hasn't changed
                    if value is None or value == getattr(model_object, field_name):
                        continue
                    # If all items have been removed
                    if value is None:
                        is_data_empty = False
                        setattr(model_object, field_name, [])
                        continue

                    # Otherwise the list has been changed in some other way
                    # Remove all items from the list, so that any items that aren't there are deleted.
                    old_items = []
                    for i in reversed(range(len(getattr(model_object, field_name, [])))):
                        old_items.append(getattr(model_object, field_name)[i])

                    for item in value:
                        if item is None or item is colander.null or not isinstance(item, dict) or len(item) <= 0:
                            continue

#                        if 'schema_select' in item and len(item) == 2:  # This is the custom developed select mapping - flatten the select out
#                            method = item.pop('schema_select')
#                            item = item.values()[0]

                        current_object = None

                        prefix = ''.join(str(x + ":") for x in item.items()[0][0].split(":")[:-1])

                        child_model_class=model_object._sa_class_manager[field_name].property.mapper.class_
                        unknown_model = False
                        # If the item has an id and the id==an item in the model_object, update the model object item instead of creating a new one.
                        if prefix + 'id' in item and (isinstance(item[prefix + 'id'], (long, int)) or (isinstance(item[prefix + 'id'], basestring) and item[prefix + 'id'].isnumeric())):
                            for model_item in old_items:
    #                            print "ID's: " + str(getattr(model_item, 'id', None)) + " : " + str(item['id'])
                                current_object_id = getattr(model_item, 'id', None)
    #                            print (isinstance(current_object_id, (int, long)) or (isinstance(current_object_id, basestring) and current_object_id.isnumeric()))
                                if (isinstance(current_object_id, (int, long)) or (isinstance(current_object_id, basestring) and current_object_id.isnumeric())) and int(getattr(model_item, 'id', None)) == int(item[prefix + 'id']):
                                    current_object = model_item
                                    old_items.remove(current_object)
    #                                print "Current Object: " + str(current_object)
                                    break

                            # If this is an object referenced from the database that the current model has no previous known state for.
                            if current_object is None:
                                current_object = self._sa_instance_state.session.query(child_model_class).filter_by(id=int(item[prefix + 'id'])).first()
                                unknown_model = True

                        if not unknown_model:
                            child_table_object = self.create_sqlalchemy_model(item, model_class=child_model_class, model_object=current_object)
                        else:
                            child_table_object = current_object
                            current_object = None

                        # If the child object has changed
                        if child_table_object is not None:
                            is_data_empty = False

                            # If the child object is new
                            if current_object is None:
                                getattr(model_object, field_name).append(child_table_object) # Add the modified object

                        # If the child object was just updated SQLAlchemy keeps track of the changes internally
#                        elif current_object is not None:
#                            getattr(model_object, field_name).append(current_object) # Re-add the un-modified object

                    # Delete items in the list that were missing from the new data
                    for item in old_items:
                        getattr(model_object, field_name).remove(item)
                        del item
                        is_data_empty = False

                elif isinstance(getattr(model_object, field_name), dict) or isinstance(value, dict):
                    # If the value hasn't been changed

                    if value == getattr(model_object, field_name):
                        continue
                    elif value is None:
                        # If the value is now empty and it was set previously
                        is_data_empty = False
                        setattr(model_object, field_name, None)
                        continue

                    current_object = None
                    if getattr(model_object, field_name) is not None:
                        current_object = getattr(model_object, field_name, None)

                    if not hasattr(model_object._sa_class_manager[field_name].property, 'mapper'):
                        raise AttributeError("Model conversion scripts have an error, trying to generate a model with invalid values.")
                    child_table_object = self.create_sqlalchemy_model(value, model_class=model_object._sa_class_manager[field_name].property.mapper.class_, model_object=current_object)

                    if child_table_object is not None:
                        setattr(model_object, field_name, child_table_object)
                        is_data_empty = False

                else:
                    # If the value hasn't been changed
                    field_type = self._get_field_type(field_name, model_object)
                    str(value)
                    str(getattr(model_object, field_name))
                    if str(value) == str(getattr(model_object, field_name)) or\
                       (field_type in (int, float, long) and (value is None or value==0) and (getattr(model_object, field_name) is None or getattr(model_object, field_name) == 0)):
                        continue

                    # If the value is now empty and it was set previously
                    elif value is None:
                        setattr(model_object, field_name, None)
                        is_data_empty = False
                        continue
                    try:

                        # Don't use default values to determine if the data is a new object.
                        ca_registry = self._get_ca_registry(field_name, model_class)
                        if ca_registry is None or ('default' not in ca_registry or not value == ca_registry['default'] or not new_model):
                            is_data_empty = False
                        setattr(model_object, field_name, value)

                    except Exception as e:
                        logger.exception("Failed to set model attribute: %s" % field_name)
                        continue


        if is_data_empty:
            return None

        return model_object
    
    def convert_sqlalchemy_model_to_data(self, model, schema=None, force_not_empty_lists=False, dates_as_string=True,
                                         bool_false_as_none=True):
        """
        Functionality behind CAModel dictify(), this is a recursive function that will call itself for each child.

        :param model: Model to dictify.
        :param schema: Schema to dictify for (mainly used for recursive functionality).
        :param force_not_empty_lists: Ensure there is always at least 1 element in sequences/lists.
        :param dates_as_string: Output dates as objects or strings (deform widgets are inconsistent with this...)
        :return: Deform compatible appstruct for the passed in CAModel.
        """
        if schema is None:
            # This will not take groupings into account
            schema = convert_schema(SQLAlchemyMapping(type(model)))

        data = {}
    
        if model is None:
            return data
    
        for node in schema:
            name = fix_schema_field_name(node.name)
    
            if hasattr(model, name):
                value = getattr(model, name, None)

                if isinstance(value, basestring):
                    if isinstance(value, unicode):
                        value = value.encode("utf-8")
                    value = unicode(value, "utf-8")
    
                if isinstance(value, date) and dates_as_string:
                    value = str(value)
    
                if isinstance(value, bool):
                    if hasattr(node.widget, 'true_val') and value:
                        value = node.widget.true_val
                    else:
                        if bool_false_as_none:
                            value = None
                        elif hasattr(node.widget, 'false_val'):
                            value = node.widget.false_val
    
                if isinstance(value, list):
                    node_list = []

                    while node.widget is not None and len(value) < node.widget.min_len:
                        value.append(node.children[0]._reg.cls())

                    for item in value:
                        node_list.append(self.convert_sqlalchemy_model_to_data(item,  node.children[0], force_not_empty_lists, dates_as_string))

                    if force_not_empty_lists and len(value) == 0:
                        node_list.append(self.convert_sqlalchemy_model_to_data(node.children[0]._reg.cls(),  node.children[0], force_not_empty_lists, dates_as_string))
    
                    data[node.name] = node_list
#                elif isinstance(node.typ, deform.FileData) and value is not None:
#                    tempstore = node.widget.tmpstore.tempstore
#                    data[node.name] = node.default
#                    if value is not None:
#                        randid = value.split("/")[-1]
#                        for file_uid in tempstore:
#                            if 'randid' in tempstore[file_uid] and (tempstore[file_uid]['randid']) == str(randid):
#                                data[node.name] = tempstore[file_uid]
#                                break
    
                elif len(node.children):
                    data[node.name] = self.convert_sqlalchemy_model_to_data(value,  node, force_not_empty_lists, dates_as_string)
    
                elif value is None:
                    data[node.name] = node.default
                else:
                    if isinstance(node.widget, deform.widget.SelectWidget):
                        label = None
                        for select_value, select_label in node.widget.values:
                            if select_value == value:
                                label = select_label
                                break
                        # Give a best effor to set the redbox label fields that go along with all select fields
                        if hasattr(model, name + "_label"):
                            data[node.name + "_label"] = label

                    data[node.name] = value
            elif len(node.children) > 0:
                node_data = self.convert_sqlalchemy_model_to_data(model, node.children, force_not_empty_lists, dates_as_string)
    
                # Fix data for select mapping schemas
#                if not ':' in node.name:
#                    data['schema_select'] = str(getattr(model, 'method_id', None))

                data[node.name] = node_data
    
        return data

    def _add_xml_elements(self, root, data):
        """
        Implements to_xml() functionality in a recursive manner.

        :param root: Root XML element to add all created elements to.
        :param data: Data to convert to XML
        :return: The created XML node/element.
        """
        element = None

        for key, value in data.items():
            key = fix_schema_field_name(key)

            # Don't add empty items to the XML
            if value is colander.null or value is None or (isinstance(value, list) and len(value) == 0) or value is False or value == 'false':
                continue

            # If this is a group node for the purpose of displaying data nicely, ignore it and just add its children.
            if isinstance(value, dict):
                self._add_xml_elements(root, value)
            elif isinstance(value, list):
                element = etree.SubElement(root, key)
                for i in range(len(value)):
                    if value is not None:
                        child_element = etree.SubElement(element, key + ".%i" % i)
                        self._add_xml_elements(child_element, value[i])
                    else:
                        test = 1
            else:
                element = etree.SubElement(root, key)
                element.text = str(value)

        return element

    def to_xml(self):
        root = etree.Element(self.__class__.__name__.lower())
        root.append(self._add_xml_elements(root, self.dictify()))

        return etree.ElementTree(root.getroottree().getroot())

#    def __getattribute__(self, name):
#        """
#        Convert string values read from the database into utf-8 encoded unicode (supports non-alphanumeric characters)
#
#        :param name:
#        :return:
#        """
#        value = super(CAModel, self).__getattribute__(name)
#
#        if name == "brief_desc":
#            test = 1
#
#        try:
#            if isinstance(value, basestring):
##                if isinstance(original_value, unicode):
##                    value = original_value.encode("utf-8")
##                value = unicode(original_value, "utf-8")
#                if isinstance(value, str):
#                    value = value.decode("utf-8")
#
#                if isinstance(value, unicode):
#                    value = value.encode("utf-8")
#
#            return value
#        except Exception as e:
#            return value
#
#    def __setattr__(self, name, value):
#        if isinstance(value, basestring):
#            if isinstance(value, str):
#                value = value.decode("utf-8")
#
#            if isinstance(value, unicode):
#                value = value.encode("utf-8")
#
#        return super(CAModel, self).__setattr__(name, value)



    

