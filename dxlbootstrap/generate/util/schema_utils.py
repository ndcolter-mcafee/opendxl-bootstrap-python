# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 McAfee LLC - All Rights Reserved.
################################################################################

import copy
import yaml

# The OpenDXL API Specification version
SCHEMA_VERSION = "0.1"

# Keys to be used for schema objects/definitions
SOLUTION_KEY = "solutions"
SERVICE_KEY = "services"
EVENT_KEY = "events"
REQUEST_KEY = "requests"

# Service definition
SERVICE_DICT_TMPL = {
    "info": {
        #"title"
        "version": "<version of this DXL service (may be the same as the solution)>",
        "description": "This is a description of this service."
    },
    "externalDocs": {
        "description": "<external link such as a github repository or API>",
        "url": "http://opendxl.com"
    },
    REQUEST_KEY: []
}

# Base message definition
MESSAGE_PROPS_DICT_TMPL = {
    "description": "This is a description of this message.",
    "payload": {
        "properties": {
            "property1": {
                "description": "This is a description of this property.",
                "type": "<message property type (ex: integer, object, string, etc.)>"
            },
            "property2": {
                "description": "This is a description of this property.",
                "type": "<message property type (ex: integer, object, string, etc.)>"
            }
        },
        "example": {
            "property1": "<Example value of property1>",
            "property2": "<Example value of property2>"
        }
    }
}

# Request definition
REQUEST_DICT_TMPL = copy.deepcopy(MESSAGE_PROPS_DICT_TMPL)
REQUEST_DICT_TMPL["response"] = copy.deepcopy(MESSAGE_PROPS_DICT_TMPL)

# Event definition
EVENT_DICT_TMPL = copy.deepcopy(MESSAGE_PROPS_DICT_TMPL)
EVENT_DICT_TMPL["isIncoming"] = True


def topic_ref_transform(ref_string, topic):
    """
    Converts a topic string with forward-slashes into a JSON reference-friendly format
    ("/" becomes "~1"), then places the new string into the provided base reference path.

    :param ref_string: The base reference path
    :param topic: The DXL topic string to convert
    """
    return str(ref_string.format(topic.replace("/", "~1")))


class DxlSchemaWriter(object):

    def __init__(self, app_name):
        """
        Constructs the schema writer.

        :param app_name: The application name
        """

        # Define the app name and the general template for the schema
        self.app_name = app_name
        self.schema_dict_tmpl = {
            "openDxlApi": SCHEMA_VERSION,
            "info": {
                "title": app_name,
                "version": "0.1",
                "description": "This is a general description of this API specification.",
                "contact": {
                    "url": "www.company-website-url.com"
                }
            },
            SOLUTION_KEY: {
                app_name: {
                    "info": {
                        "title": app_name,
                        "version": "<solution/product version number>",
                        "description": "This is a description of this solution."
                    },
                    "externalDocs": {
                        "description": "This is a link to further documentation for this solution.",
                        "url": "http://opendxl.com"
                    },
                    SERVICE_KEY: [],
                    EVENT_KEY: []
                }
            },
            SERVICE_KEY: {},
            EVENT_KEY: {},
            REQUEST_KEY: {}
        }

    @property
    def schema_dict_yaml(self):
        """
        Returns the current constructed version of the schema.
        """
        return yaml.dump(self.schema_dict_tmpl, default_flow_style=False)

    def add_service_ref_to_solution(self, service_type):
        """
        Adds a service reference to a solution's "services" array.

        :param service_type: The service type
        """
        self.schema_dict_tmpl[SOLUTION_KEY][self.app_name][SERVICE_KEY]\
            .append({"$ref": topic_ref_transform("#/services/{0}", service_type)})

    def add_event_ref_to_solution(self, event_topic):
        """
        Adds an event message reference to a solution's "events" array.

        :param event_topic: The DXL topic on which the event is sent
        """
        self.schema_dict_tmpl[SOLUTION_KEY][self.app_name][EVENT_KEY]\
            .append({"$ref": topic_ref_transform("#/events/{0}", event_topic)})

    def add_request_ref_to_service(self, service_type, request_topic):
        """
        Adds a request message reference to a service's "requests" array.

        :param service_type: The DXL topic on which the event is sent
        :param request_topic: The DXL topic on which the request is sent
        """
        self.schema_dict_tmpl[SERVICE_KEY][service_type][REQUEST_KEY]\
            .append({"$ref": topic_ref_transform("#/requests/{0}", request_topic)})

    def add_service_def_to_schema(self, service_type):
        """
        Adds a service definition to the schema. Uses the service type as a
        key for the service definition object.

        :param service_type: The service type
        """
        self.schema_dict_tmpl[SERVICE_KEY][service_type] = \
            copy.deepcopy(SERVICE_DICT_TMPL)

    def add_request_def_to_schema(self, request_topic):
        """
        Adds a request message definition to the schema. Uses the request
        topic as a key for the request definition object.

        :param request_topic: The DXL topic on which the request is sent
        """
        self.schema_dict_tmpl[REQUEST_KEY][request_topic] = \
            copy.deepcopy(REQUEST_DICT_TMPL)

    def add_event_def_to_schema(self, event_topic):
        """
        Adds an event message definition to the schema. Uses the event
        topic as a key for the event definition object.

        :param event_topic: The DXL topic on which the event is sent
        """
        self.schema_dict_tmpl[EVENT_KEY][event_topic] = \
            copy.deepcopy(EVENT_DICT_TMPL)
