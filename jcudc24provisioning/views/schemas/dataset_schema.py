import inspect
import colander
from colanderalchemy.declarative import Column, relationship
import deform
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum, Unicode, Integer, String
from jcudc24provisioning.models import Base
from jcudc24provisioning.views.schemas.common_schemas import Attachment, SelectMappingSchema, ConditionalCheckboxSchema
from jcudc24provisioning.views.widgets import SelectMappingWidget, ConditionalCheckboxMapping

__author__ = 'Casey Bajema'


class SamplingCondition(colander.MappingSchema):
    pass


class SamplingConditionSchema(colander.SequenceSchema):
    todo = colander.SchemaNode(colander.String())

class SamplingSchema(colander.MappingSchema):
    start_conditions = SamplingConditionSchema(title="Start conditions")
    stop_conditions = SamplingConditionSchema(title="Stop conditions")

map_location_types = (
    ("none", "---Select One---"),
    ("gml", "OpenGIS Geography Markup Language"),
    ("kml", "Keyhole Markup Language"),
    ("iso19139dcmiBox", "DCMI Box notation (iso19139)"),
    ("dcmiPoint", "DCMI Point notation"),
    ("gpx", "GPS Exchange Format"),
    ("iso31661", "Country code (iso31661)"),
    ("iso31662", "Country subdivision code (iso31662)"),
    ("kmlPolyCoords", "KML long/lat co-ordinates"),
    ("gmlKmlPolyCoords", "KML long/lat co-ordinates derived from GML"),
    ("text", "Free text"),
    )

class MapLocationSchema(colander.MappingSchema):
    type_of_research = colander.SchemaNode(colander.String(), widget=deform.widget.SelectWidget(values=map_location_types),
        title="Location Type", missing="")
    location = colander.SchemaNode(colander.String())


class MapRegionSchema(colander.SequenceSchema):
    location = MapLocationSchema(widget=deform.widget.MappingWidget(template='inline_mapping'))

class CoverageSchema(colander.MappingSchema):
    time_period_description = colander.SchemaNode(colander.String(), title="Time Period (description)",
        placeholder="A textual description of the time period (eg. Summers of 1996 to 2006)", missing="",
        description="Provide a textual representation of the time period such as world war 2 or more information on the time within the dates provided.")
    date_from = colander.SchemaNode(colander.Date(), placeholder="", title="Date From",
        description='Date data will start being collected.')
    date_to = colander.SchemaNode(colander.Date(), title="Date To",
        description='Date data will stop being collected.', missing=colander.null)
    location_description = colander.SchemaNode(colander.String(), title="Location (description)",
        description="Textual description of the location such as Australian Wet Tropics or further information such as elevation."
        , missing="", placeholder="eg. Australian Wet Tropics, Great Barrier Reef, 1m above ground level")
    coverage_map = MapRegionSchema(title="Location Map", widget=deform.widget.SequenceWidget(template='map_sequence'),missing=colander.null,
        description=
        "<p>Geospatial location relevant to the research dataset/collection, registry/repository, catalogue or index. This may describe a geographical area where data was collected, a place which is the subject of a collection, or a location which is the focus of an activity, eg. coordinates or placename.</p>"\
        "<p>You may use the map to select an area, or manually enter a correctly formatted set of coordinates or a value supported by a standard such as a country code, a URL pointing to an XML based description of spatial coverage or free text describing a location."\
        "</p><p>If you wish to generate a map display in Research Data Australia, it is strongly advised that you use <b>DCMI Box</b> for shapes, or <b>DCMI Point</b> for points.</p><p>"\
        "Formats supported by the map widget:"\
        "<ul><li><a href=\"http://www.opengeospatial.org/standards/gml\" target=\"_blank\">GML</a> - OpenGIS Geography Markup Language (GML) Encoding Standard</li>"\
        "<li><a href=\"http://code.google.com/apis/kml/\" target=\"_blank\">KML</a> - Keyhole Markup Language developed for use with Google Earth</li>"\
        "<li><a href=\"http://dublincore.org/documents/dcmi-box\" target=\"_blank\">ISO19319dcmiBox</a> - DCMI Box notation derived from bounding box metadata conformant with the iso19139 schema</li>"\
        "<li><a href=\"http://dublincore.org/documents/dcmi-point\" target=\"_blank\">DCMIPoint</a> - spatial location information specified in DCMI Point notation</li></ul>"\
        "<p>When using the map to input shapes/points, only the above formats are supported. You can use the 'Find location' feature to pan the map to an area you are interested in, but you still need to select a map region to store geospatial data.</p>"\
        "<p>Formats available for manual data entry:</p>"\
        "<ul><li><a href=\"http://www.topografix.com/gpx.asp\" target=\"_blank\">GPX</a> - the GPS Exchange Format</li>"\
        "<li><a href=\"http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm\" target=\"_blank\">ISO3166</a> - ISO 3166-1 Codes for the representation of names of countries and their subdivisions - Part 1: Country codes</li>"\
        "<li><a href=\"http://www.iso.org/iso/country-codes/background_on_iso_3166/iso_3166-2.htm\" target=\"_blank\">ISO31662</a> - Codes for the representation of names of countries and their subdivisions - Part 2: Country subdivision codes</li>"\
        "<li><a href=\"http://code.google.com/apis/kml/\" target=\"_blank\">kmlPolyCoords</a> - A set of KML long/lat co-ordinates defining a polygon as described by the KML coordinates element</li>"\
        "<li><a href=\"http://code.google.com/apis/kml/\" target=\"_blank\">gmlKmlPolyCoords</a> - A set of KML long/lat co-ordinates derived from GML defining a polygon as described by the KML coordinates element but without the altitude component</li>"\
        "<li><strong>Text</strong> - free-text representation of spatial location. Use this to record place or region names where geospatial notation is not available. In ReDBox this will search against the Geonames database and return a latitude and longitude value if selected. This will store as a DCMIPoint which in future will display as a point on a Google Map in Research Data Australia.</li></ul>")


class CustomProcessingSchema(colander.MappingSchema):
    custom_processor_desc = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(),
        title="Describe custom processing needs", missing="", description="Describe your processing "\
                                                                          "requirements and what your uploaded script does, or what you will need help with."
        ,
        placeholder="eg. Extract some value from the comma separated file where the value is the first field.")

    custom_processor_script = Attachment(title="Upload custom script", description="Upload a custom Python script to "\
                                                                             "process the data in some way.  The processing script API can be found "\
                                                                             "<a title=\"Python processing script API\"href=\"\">here</a>."
        , missing = colander.null)

class DataSourceSchema(colander.MappingSchema):
    pass

class InternalMethodSchema(colander.MappingSchema):
    description = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(),
        placeholder="Provide a textual description of the dataset being collected.",
        description="Provide a dataset specific description that will be appended to the project description in metadata records.")

    sampling = SamplingSchema()
    custom_processing = CustomProcessingSchema(title="Custom processing")

class DatasetConfigurationSchema(ConditionalCheckboxSchema):
    data_source_configuration = DataSourceSchema(description="TODO: Dataset specific configuration of the data source for the selected method.")
    coverage = CoverageSchema()

class MethodSchema(colander.MappingSchema):
    description = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(),
        placeholder="Provide a textual description of the dataset being collected.",
        description="Provide a dataset specific description that will be appended to the project description in metadata records.")

    dataset_configuration = DatasetConfigurationSchema(widget=ConditionalCheckboxMapping(inverted_condition=True), title='(Advanced) This is a normal dataset', missing=colander.null, default=True,
        description="Un-checking this option disables metadata record generation and data ingestion.  Only un-check this if the dataset is an intermediate processing step for other dataset(s).")

    sampling = SamplingSchema(
        description="Provide filtering conditions for the data received, the most common and simplest"\
                    "cases are a sampling rate (eg. once per hour) or a repeating time periods (such as "\
                    "start at 6am, stop at 7am daily) but any filtering can be acheived by adding a custom "\
                    "sampling script.</br></br>  The sampling script API can be found <a href="">here</a>.")
    # TODO: Finish the sampling schema
    custom_processing = CustomProcessingSchema(title="Custom processing")


class PushDataSourceSchema(colander.MappingSchema):
    key = colander.SchemaNode(colander.String(), "A unique API key that can be used for authentication.",
        readonly=True)


class PullDataSourceSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String(), "Location of the server to poll.")


class SOSDataSourceSchema(colander.MappingSchema):
    server_url = colander.SchemaNode(colander.String(), description="Location of the SOS server.")
    sensor_id = colander.SchemaNode(colander.String(), description="ID of the SOS sensor.")


class MethodSelectSchema(SelectMappingSchema):
    method_a = MethodSchema(missing=colander.null)
    method_b = MethodSchema(missing=colander.null)
#    internal = InternalMethodSchema(missing=colander.null)

def __init__(self):
    pass

#        for all methods:
#            method = MethodSchema()
#            for name, obj in inspect.getmembers(foo):
#                if inspect.isclass(obj):
#                    method.add(api2colander(dataSourceSchema))
#            self.add(method)
#        self.add(InternalMethodSchema())

class Dataset(Base):
    __tablename__ = 'dataset'
    id = Column(Integer, primary_key=True, ca_widget=deform.widget.HiddenWidget())
#    data_source = MethodSelectSchema(title="Method",collapsed=False, collapse_group="dataset", collapse_legend="Dataset",
#        description="Select the data collection method for this dataset, the methods need to have been setup in the previous workflow step.</br></br>" \
#                    "<b>Will be developed so that methods created in the 'Methods' workflow step will populate the below dropbox.</b>")


    description = Column(String(), ca_widget=deform.widget.TextAreaWidget(),
            ca_placeholder="Provide a textual description of the dataset being collected.",
            ca_description="Provide a dataset specific description that will be appended to the project description in metadata records.")


class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""
    def preview_url(self, uid):
        return None

class DatasetSchema(Base):
    __tablename__ = 'project_datasets'

    dataset_id = Column(Integer, ForeignKey('dataset.id'), primary_key=True,  ca_widget=deform.widget.HiddenWidget())
    project_id = Column(Integer,ForeignKey('project.id'), primary_key=True,  ca_widget=deform.widget.HiddenWidget())
#    description = Dataset(widget=deform.widget.TextAreaWidget(),
#            placeholder="Provide a textual description of the dataset being collected.",
#            description="Provide a dataset specific description that will be appended to the project description in metadata records.")


    datasets = relationship('Dataset')


#    test = Column(Attachment())