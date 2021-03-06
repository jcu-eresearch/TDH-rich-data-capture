"""
Customised widgets and functionality for file uploads in the EnMaSSe provisioning interface.
"""
import ast

import binascii
import colander
from pyramid_deform import chunks, string_types, _marker
import deform
import os
from deform.widget import FileUploadWidget, filedict

__author__ = 'Casey Bajema'


class ProvisioningUploadTempStore(object):
    """
    Defines how uploaded files are stored.
    """
    def __init__(self, request, directory):
        """
        Initialise the file upload storage.

        :param request: The HTTP request object.
        :param directory: Parent directory for uploaded files.
        :return: self
        """
        self.dir = os.path.normpath(directory) + os.sep
        self.request = request
        self.session = request.session
        self.tempstore = self.session.setdefault('directory_upload.tempstore', {})

    def preview_url(self, name):
        """
        Provides the text that represents the file identified by name, the returned value is what is stored in the DB.
        :param name: Name of the file (this is really a random identifier).
        :return:
        """
        return self._get_file_path(name, self.get(name)['filename'])

    def __contains__(self, name):
        return self.get(name) is not None

    def __setitem__(self, name, data):
        """
        Write a file to storage.

        :param name: Random identifier for this file.
        :param data: Data contained in this file.
        :return:
        """

        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            # TODO: This possibly leaves it open for 2 uers to change files at the same time!
            newdata['filepath'] = self._get_file_path(os.path.normpath(name), data['filename'])
            fp = open(newdata['filepath'], 'w+b')

            for chunk in chunks(stream):
                fp.write(chunk)

        self.tempstore[name] = newdata
        self.session.changed()

    def _get_file_path(self, name, filename):
        """
        Get the file path based on the random identifier and the name, this is really a way of encoding both of these
        pieces of data into a filename that the file data is written to.

        :param name: Random, unique, identifier for this file.
        :param filename: Original filename (not the full path, just the files name and extension).
        :return: <name>.<filename> as a unique filename to write the files data to while still maintaining the information to get the original filename.
        """
        return "%s.%s" % (self._get_base_path(name), filename)

    def _get_base_path(self, name):
        """
        Return the base path of all uploaded files (<directory><name>).

        :param name: Unique, random, identifier
        :return: Return the base path of this file.
        """
        return self.dir + name

    def get(self, name, default=None):
        """
        Get this file as a HTML fileupload compatible dictionary.

        :param name: Unique, random, identifier
        :param default: Default value to return if no file is found.
        :return: Dict of data compatible for outputting to a deform fileupload widget.
        """
        data = self.tempstore.get(name)

        new_data = None
        if data is None and name is not None and name:
            uid = name
            if os.sep in name:
                name = os.path.normpath(name)
                filepath = name.replace(self.dir, "")
                uid, filename = filepath.split(".", 1)

            files = os.listdir(self.dir)
            for file in files:
                if uid in file:
                    uid, filename = file.replace(self.dir, "").split(".", 1)
                    new_data = {
                        "filename": filename,
                        "filepath": self.dir + file,
                        "preview_url": self.dir + file,
                        "uid": uid
                    }
                    break
        else:
            new_data = data.copy()

        if new_data is None:
            return default

        filepath = new_data.get('filepath')

        if filepath is not None:
            try:
                new_data['fp'] = open(filepath, 'rb')
            except IOError:
                pass

        return new_data

    def __getitem__(self, name):
        data = self.get(name, _marker)
        if data is _marker:
            raise KeyError(name)
        return data


class ProvisioningFileUploadWidget(FileUploadWidget):
    """
    Deform Widget for displaying and parsing results for file uploads
    """
    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = {}

        if isinstance(cstruct, basestring):
            # IF this is a str(dict)
            if cstruct[0] == '{' and cstruct[-1] == '}' and ":" in cstruct:
                cstruct = ast.literal_eval(cstruct)
            else:
                cstruct = self.tmpstore.get(cstruct)

        if 'uid' in cstruct:
            uid = cstruct['uid']
            if not uid in self.tmpstore:
                self.tmpstore[uid] = cstruct

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null

        if not isinstance(pstruct, dict):
            pstruct = self.tmpstore.get(pstruct)
            if pstruct is None:
                return colander.null

        if pstruct.get('is_external', False):
            return pstruct

        upload = pstruct.get('upload')
        uid = pstruct.get('uid')

        if hasattr(upload, 'file'):
            # the upload control had a file selected
            data = filedict()
            data['fp'] = upload.file
            filename = upload.filename
            # sanitize IE whole-path filenames
            filename = filename[filename.rfind('\\')+1:].strip()
            data['filename'] = filename
            data['mimetype'] = upload.type
            data['size']  = upload.length
            if uid is None:
                # no previous file exists
                while 1:
                    uid = self.random_id()
                    if self.tmpstore.get(uid) is None:
                        data['uid'] = uid
                        self.tmpstore[uid] = data
                        preview_url = self.tmpstore.preview_url(uid)
                        data['preview_url'] = preview_url
                        self.tmpstore[uid]['preview_url'] = preview_url
                        break
            else:
                # a previous file exists
                data['uid'] = uid
                self.tmpstore[uid] = data
                preview_url = self.tmpstore.preview_url(uid)
                self.tmpstore[uid]['preview_url'] = preview_url
        else:
            # the upload control had no file selected
            if uid is None or not uid:
                # no previous file exists
                return colander.null
            else:
                # a previous file should exist
                data = self.tmpstore.get(uid)
                data['preview_url'] = data['filepath']
                # but if it doesn't, don't blow up
                if data is None:
                    return colander.null

        return data['preview_url']



@colander.deferred
def upload_widget(node, kw):
    """
    Deferred function that creates the ProvisioningFileUploadWidget when the schem .bind() method is called.  The
    ProvisioningFileUploadWidget requires a request object te get access to the session and .ini configurations.

    :param node: Schema node that this widget is for.
    :param kw: Arguments that are passed into the bind() method.
    :return: ProvisioningFileUploadWidget with access to the request object.
    """
    request = kw['request']
    tmp_store = ProvisioningUploadTempStore(request, request.registry.settings.get("workflows.files"))
    widget = ProvisioningFileUploadWidget(tmp_store)
    return widget


#class Attachment(colander.SchemaNode):
#    def __init__(self, typ=deform.FileData(), *children, **kw):
#        if not "widget" in kw: kw["widget"] = upload_widget
#        if not "title" in kw: kw["title"] = "Attach File"
#        colander.SchemaNode.__init__(self, typ, *children, **kw)