import deform
from pyramid.response import Response
from views.schemas.dataset_schema import MethodSelectSchema
from views.workflow.workflows import Workflows, MemoryTmpStore

__author__ = 'Casey Bajema'

import colander
from deform.exception import ValidationFailure
from deform.form import Form
from pyramid.view import view_config
from layouts import Layouts


class Dataset(colander.SequenceSchema):
    dataSource = MethodSelectSchema(title="Method", widget=deform.widget.MappingWidget(template="select_mapping"))

class DatasetSchema(colander.MappingSchema):
    dataInputs = Dataset(title="Datasets", widget=deform.widget.SequenceWidget(min_len=1))

class DatasetsView(Workflows):
    title = "Datasets"

    def __init__(self, request):
        self.request = request
        self.schema = DatasetSchema(description="Add individual datasets that your project will be collecting.  This is the when and where using the selected data collection method (what, why and how).  Such that an iButton sensor that is used to collect temperature at numerous sites would have been setup once within the Methods step and should be set-up in this step for each site it is used at.")
        self.myform = Form(self.schema, action="datasets_submit", buttons=('Save', 'Delete'), use_ajax=True)

    @view_config(renderer="../../templates/datasets.pt", name="datasets_submit")
    def datasets_submit(self):
        if self.request.POST.get('Delete') == 'confirmed':
            location = self.request.application_url + '/'
            message = 'Project successfully deleted'
            return Response(self.myform.render(),
                headers=[('X-Relocate', location), ('Content-Type', 'text/html'), ('msg', message)])

        controls = self.request.POST.items()
        try:
            appstruct = self.myform.validate(controls)
        except ValidationFailure, e:
            return  {"page_title": 'Datasets', 'form': e.render(), 'values': False}
            # Process the valid form data, do some work

        return {"page_title": 'Datasets', "form": self.myform.render()}

    @view_config(renderer="../../templates/datasets.pt", name="datasets")
    def datasets_view(self):
        return {"page_title": 'Datasets', "form": self.myform.render(), "values": None}
