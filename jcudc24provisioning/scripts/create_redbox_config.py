from collections import OrderedDict
import json
import colander
from lxml import etree
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import Column
import sys
from jcudc24provisioning.controllers.sftp_filesend import SFTPFileSend
from jcudc24provisioning.models.ca_model import CAModel
from jcudc24provisioning.models.project import Metadata, Party, Keyword, Collaborator, MetadataNote, CitationDate, Attachment, RelatedPublication, RelatedWebsite, FieldOfResearch, SocioEconomicObjective, Location, Creator
from jcudc24provisioning.views.ca_scripts import fix_schema_field_name
import os

__author__ = 'Casey Bajema'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %(cmd)s [arguments] <file>\t\t\tWrite the configuration to a local file.\n'
          '\t(example: "%(cmd)s -s http:\\\\www.example.com\\redbox\\home\\harvest\\my-harvester\\config\\myXmlMapping.xml development.ini)"\n\n'
          'Arguments:\n'
          '\t -s <config>\t\t\tSend the created XML mapping to ReDBox over sftp using the provided configuration.' % {
              "cmd": cmd})
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) > 4 or len(argv) < 2 or\
       len(argv) > 2 and argv[1] != "-s":
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    xmlMapping = create_json_config()

    file = argv[len(argv) - 1]
    f = open(file, 'w')
    f.write(xmlMapping)

    if argv[1] == "-s":
        settings = get_appsettings(config_uri)
        file_send = SFTPFileSend(settings['redbox.ssh_host'], settings['redbox.ssh_port'],
            settings['redbox.ssh_username'],
            settings['redbox.ssh_password'],
            settings['redbox.rsa_private_key'])
        file_send.upload_file(file, settings['redbox.ssh_config_file'])
        file_send.close()


def create_json_config():
# TODO: Work out if any of these fields are needed?
#    "dc:extent": "",                                   # Size of data

# Data management fields
#na     "redbox:disposalDate": "",                      # Data owner
#na     "locrel:own.foaf:Agent.0.foaf:name": "",        # Data owner
#na     "locrel:dtm.foaf:Agent.foaf:name": "",          # Data custodian - TODO: Should this be filled with JCU?
#     "foaf:Organization.dc:identifier": "",            # Data affiliation
#     "foaf:Organization.skos:prefLabel": "",           # Data affiliation
#     "swrc:ResearchProject.dc:title": "",   # TODO: Should this be added? - would map to the project title field?
#na     "locrel:dpt.foaf:Person.foaf:name": "",         # Depositor
#na    "dc:SizeOrDuration": "",                         # Data size
#na     "dc:Policy": "",                                # Institutional data management policy
#na    "redbox:ManagementPlan.redbox:hasPlan": null,    # Data management policy
#na     "redbox:ManagementPlan.skos:note": "",          # Data management policy
#na     "skos:note.0.dc:created": "",
#na     "skos:note.0.foaf:name": "",                    # Seems to be a notes squence that is split between muliple places as individual fields
#na     "skos:note.0.dc:description": "",


#    # TODO: What is the metalist?
##    "metaList": [...]



    dict_config = {
        "comment": "This James Cook University's XML mapping is generated from the DC24 RichDataCapture provisioning interface.  It is generated on startup to create a ReDBox json configuration file that matches the models XML conversion.",
        "mappings": {
            "/%s" % Metadata.record_export_date.key: "dc:created",
            "/%s" % Metadata.dc_spec.key: "xmlns:dc",
            "/%s" % Metadata.foaf_spec.key: "xmlns:foaf",
            "/%s" % Metadata.anzsrc_spec.key: "xmlns:anzsrc",
            "/%s" % Metadata.view_id.key: "viewId",
            "/%s" % Metadata.package_type.key: "packageType",
            "/%s" % Metadata.record_origin.key: "dc:identifier.redbox:origin",
            #TODO: What should this be prefilled with? Internal or something like rdc?
            "/%s" % Metadata.new_redbox_form.key: "redbox:newForm", #TODO: Should this be true?
            "/%s" % Metadata.redbox_form_version.key: "redbox:formVersion",
            "/%s" % Metadata.record_type.key: "dc:type.rdf:PlainLiteral",
            "/%s" % Metadata.record_type_label.key: "dc:type.skos:prefLabel",
            "/%s" % Metadata.language.key: "dc:language.dc:identifier",
            "/%s" % Metadata.language_label.key: "dc:language.skos:prefLabel",

            #    "dc:identifier.dc:type.rdf:PlainLiteral": "",   # TODO: Set the redbox identifier - What should the type be?
            #    "dc:identifier.dc:type.skos:prefLabel": "",
            "/%s" % Metadata.redbox_identifier.key: "dc:identifier.rdf:PlainLitera",


            "/%s" % Metadata.data_storage_location.key: "vivo:Location.vivo:GeographicLocation.gn:name",
            "/%s" % Metadata.ccdam_identifier.key: "bibo:Website.0.dc:identifier",
            "/%s" % Metadata.project_title.key: ["title", "dc:title", "redbox:submissionProcess.dc:title"],
            "/%s" % Metadata.internal_grant.key: "foaf:fundedBy.vivo:Grant.0.redbox:internalGrant",
            "/%s" % Metadata.grant_number.key: "foaf:fundedBy.vivo:Grant.0.redbox:grantNumber",
            "/%s" % Metadata.grant_label.key: "foaf:fundedBy.vivo:Grant.0.skos:prefLabel",
            "/%s" % Metadata.grant.key: "foaf:fundedBy.vivo:Grant.0.dc:identifier",
            "/%s" % Metadata.parties.key: {
                Party.party_relationship_label.key: "dc:creator.foaf:Person.0.jcu:relationshipLabel",
                Party.party_relationship.key: "dc:creator.foaf:Person.0.jcu:relationshipType",
                Party.identifier.key: "dc:creator.foaf:Person.0.dc:identifier",
                Party.name.key: ["dc:creator.foaf:Person.0.foaf:name", "locrel:prc.foaf:Person.foaf:name"],
                Party.title.key: ["dc:creator.foaf:Person.0.foaf:title", "locrel:prc.foaf:Person.foaf:title"],
                #                Party.coprimary: "dc:creator.foaf:Person.0.redbox:isCoPrimaryInvestigator",       # TODO: Are these needed?
                #                Party.primary: "dc:creator.foaf:Person.0.redbox:isPrimaryInvestigator",
                Party.given_name.key: ["dc:creator.foaf:Person.0.foaf:givenName", "locrel:prc.foaf:Person.foaf:title"],
                Party.family_name.key: ["dc:creator.foaf:Person.0.foaf:familyName",
                                        "locrel:prc.foaf:Person.foaf:familyName"],
                Party.organisation.key: "dc:creator.foaf:Person.0.foaf:Organization.dc:identifier",
                Party.organisation_label.key: "dc:creator.foaf:Person.0.foaf:Organization.skos:prefLabel",
                Party.email.key: "locrel:prc.foaf:Person.foaf:email",
            },
            "/%s" % Metadata.collaborators.key: {
                Metadata.collaborators.key: "dc:contributor.locrel:clb.0.foaf:Agent",
            },
            "/%s" % Metadata.full_desc_label.key: "rif:description.0.label",
            "/%s" % Metadata.full_desc_type.key: "rif:description.0.type",
            "/%s" % Metadata.breif_desc_label.key: "rif:description.0.label",
            "/%s" % Metadata.breif_desc_type.key: "rif:description.0.type",
            "/%s" % Metadata.brief_desc.key: ["description", "dc:description", "rif:description.0.value"],
            "/%s" % Metadata.full_desc.key: "rif:description.0.value",
            "/%s" % Metadata.notes.key: {
                MetadataNote.note.key: "rif:description.0.value",
                MetadataNote.note_desc_label.key: "rif:description.0.label",
                MetadataNote.note_desc_type.key: "rif:description.0.type",
            },
            "/%s" % Metadata.keywords.key: {
                Keyword.keyword.key: "dc:subject.vivo:keyword.0.rdf:PlainLiteral",
            },
            "/%s" % Metadata.fieldOfResearch.key: {
                FieldOfResearch.field_of_research.key: "dc:subject.anzsrc:for.0.skos:prefLabel",
                FieldOfResearch.field_of_research_label.key: "dc:subject.anzsrc:for.0.skos:prefLabel",
            },
            "/%s" % Metadata.socioEconomicObjective.key: {
                SocioEconomicObjective.socio_economic_objective.key: "dc:subject.anzsrc:seo.0.rdf:resource",
                SocioEconomicObjective.socio_economic_objective_label.key: "dc:subject.anzsrc:seo.0.skos:prefLabel",
            },
            "/%s" % Metadata.no_research_theme.key: "jcu:research.themes.notAligned",
            "/%s" % Metadata.ecosystems_conservation_climate.key: "jcu:research.themes.tropicalEcoSystems",
            "/%s" % Metadata.industries_economies.key: "jcu:research.themes.industriesEconomies",
            "/%s" % Metadata.peoples_societies.key: "jcu:research.themes.peopleSocieties",
            "/%s" % Metadata.health_medicine_biosecurity.key: "jcu:research.themes.tropicalHealth",
            "/%s" % Metadata.type_of_research_label.key: "dc:subject.anzsrc:toa.skos:prefLabel",
            "/%s" % Metadata.type_of_research.key: "dc:subject.anzsrc:toa.rdf:resource",
            "/%s" % Metadata.time_period_description.key: "dc:coverage.redbox:timePeriod",
            "/%s" % Metadata.date_from.key: "dc:coverage.vivo:DateTimeInterval.vivo:start",
            "/%s" % Metadata.date_to.key: "dc:coverage.vivo:DateTimeInterval.vivo:end",

#            "/%s" % Metadata.location_description.key: "",
            "/%s" % Metadata.locations.key: {
                Location.location_type.key: "dc:coverage.vivo:GeographicLocation.0.dc:type",
                # TODO: create hidden field prefilled with text.
                Location.name.key: "", #TODO: Do something with location names and elevations.
                Location.location.key: ["dc:coverage.vivo:GeographicLocation.0.redbox:wktRaw",
                                        "dc:coverage.vivo:GeographicLocation.0.rdf:PlainLiteral"],
                Location.elevation.key: "",
            },
            "/%s" % Metadata.access_rights.key: "dc:accessRights.skos:prefLabel",
            "/%s" % Metadata.access_rights_url.key: "dc:accessRights.dc:identifier",
            "/%s" % Metadata.rights.key: "dc:accessRights.dc:RightsStatement.skos:prefLabel",
            "/%s" % Metadata.rights_url.key: "dc:accessRights.dc:RightsStatement.dc:identifier",

            "/%s" % Metadata.license_name.key: "dc:license.skos:prefLabel",
            "/%s" % Metadata.license.key: "dc:license.dc:identifier",
            "/%s" % Metadata.other_license_name.key: "dc:license.rdf:Alt.skos:prefLabel",
            "/%s" % Metadata.other_license_url.key: "dc:license.rdf:Alt.dc:identifier",
            "/%s" % Metadata.citation_title.key: "dc:biblioGraphicCitation.dc:hasPart.dc:title",
            "/%s" % Metadata.citation_creators.key: {
                Creator.title.key: "dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.0.foaf:title",
                Creator.given_name.key: "dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.0.foaf:givenName",
                Creator.family_name.key: "dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.0.foaf:familyName",
            },
            "/%s" % Metadata.citation_edition.key: "dc:biblioGraphicCitation.dc:hasPart.dc:hasVersion.rdf:PlainLiteral",
            "/%s" % Metadata.citation_publisher.key: "dc:biblioGraphicCitation.dc:hasPart.dc:publisher.rdf:PlainLiteral",
            "/%s" % Metadata.citation_place_of_publication.key: [
                "dc:biblioGraphicCitation.dc:hasPart.vivo:Publisher.vivo:Location",
                "dc:biblioGraphicCitation.dc:hasPart.dc:date.0.rdf:PlainLiteral"],
            "/%s" % Metadata.citation_dates.key: {
                CitationDate.label.key: "dc:biblioGraphicCitation.dc:hasPart.dc:date.0.dc:type.skos:prefLabel",
                # TODO: Get this label as the name in the dropdown (datetype is the value)
                CitationDate.type.key: "dc:biblioGraphicCitation.dc:hasPart.dc:date.0.dc:type.rdf:PlainLiteral",
                CitationDate.date.key: "dc:biblioGraphicCitation.dc:hasPart.dc:date.0.rdf:PlainLiteral",
            },
            "/%s" % Metadata.citation_url.key: "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier",
            "/%s" % Metadata.citation_data_type.key: "dc:biblioGraphicCitation.dc:hasPart.jcu:dataType",
            "/%s" % Metadata.citation_context.key: "dc:biblioGraphicCitation.dc:hasPart.skos:scopeNote",
            "/%s" % Metadata.send_citation.key: "dc:biblioGraphicCitation.redbox:sendCitation",
            "/%s" % Metadata.use_curation.key: "dc:biblioGraphicCitation.dc:hasPart.dc:identifier.skos:note",
            # TODO: Citation->use identifier provided during curation? - Ask if this should be on?
            "/%s" % Metadata.retention_period.key: "redbox:retentionPeriod",
            "/%s" % Metadata.related_publications.key: {
                RelatedPublication.title.key: "dc:relation.swrc:Publication.0.dc:title",
                RelatedPublication.url.key: "dc:relation.swrc:Publication.0.dc:identifier",
                RelatedPublication.notes.key: "dc:relation.swrc:Publication.0.skos:note",
            },
            "/%s" % Metadata.related_websites.key: {
                RelatedWebsite.title.key: "dc:relation.bibo:Website.0.dc:title",
                RelatedWebsite.url.key: "dc:relation.bibo:Website.0.dc:identifier",
                RelatedWebsite.notes.key: "dc:relation.bibo:Website.0.skos:note",

            },
            "/%s" % Metadata.attachments.key: {
                Attachment.type.key: "",
                Attachment.attachment.key: "", # TODO: How to add attachments?
                Attachment.note.key: "",

            },

            #             # TODO: Prefill this with project dataset + each sibling dataset
            #            "dc:relation.vivo:Dataset.0.dc:identifier": "",
            #            "dc:relation.vivo:Dataset.0.vivo:Relationship.rdf:PlainLiteral": "isDescribedBy",
            #            "dc:relation.vivo:Dataset.0.vivo:Relationship.skos:prefLabel": "Described by:",
            #            "dc:relation.vivo:Dataset.0.dc:title": "test related attachment",
            #            "dc:relation.vivo:Dataset.0.skos:note": "test",
            #            "dc:relation.vivo:Dataset.0.redbox:origin": "on",
            #            "dc:relation.vivo:Dataset.0.redbox:publish": "on",
            #
            #
            #            # TODO: This is the related servces fields
            #            "dc:relation.vivo:Service.0.dc:identifier": "some_identifier",
            #            "dc:relation.vivo:Service.0.vivo:Relationship.rdf:PlainLiteral": "isProducedBy",
            #            "dc:relation.vivo:Service.0.vivo:Relationship.skos:prefLabel": "Is produced by:",
            #            "dc:relation.vivo:Service.0.dc:title": "Artificial tree sensor",
            #            "dc:relation.vivo:Service.0.skos:note": "test notes",
        }, "exceptions": {
            "fields": []
        },
        "defaultNamespace": {}
    }

    json_config = json.dumps(dict_config, sort_keys=True, indent=4, separators=(',', ': '))
    return json_config

