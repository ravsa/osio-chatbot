#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to create quickstart application."""

import logging
from fuzzywuzzy import process
from rasa_core.actions import Action
import requests
import warnings
from flask import request
from rasa_core.events import SlotSet

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")
WHITE = '\033[32m {} \033[39m'
RED = '\033[31m {} \033[39m'


class CreateQuickStart:
    """Create Application API class."""

    def __init__(self, runtime, mission, application_name, handler='rratnawa'):
        """Initialize CreateQuickStart class object."""
        self.application_name = application_name
        self.handler = handler
        runtime_list = ['spring-boot', 'vert.x', 'throntail']
        mission_list = ['rest-http', 'health-check', 'configmap']
        self.runtime = process.extractOne(runtime, runtime_list)[0]
        self.mission = process.extractOne(mission, mission_list)[0]
        self.pipeline = [
            "maven-release",
            "maven-releaseandstage",
            "maven-releasestageapproveandpromote"
        ]
        self.runtime_version = {
            'spring-boot': 'current-redhat',
            'vert.x': 'redhat',
            'throntail': 'redhat'
        }
        self.group_id = {
            'spring-boot': 'spring.boot.application',
            'vert.x': 'vertx.application',
            'throntail': 'thorntail.application'
        }
        self.artifact_id = {
            'spring-boot': 'spring-boot-application',
            'vert.x': 'vertx-application',
            'throntail': 'thorntail-application'
        }
        self.project_version = "1.0.0"
        self.host = 'https://forge.api.openshift.io/api/osio/launch'
        self.token = request.headers.get('Authorization', '')
        if not self.token.startswith('Bearer'):
            self.token = "Bearer {}".format(self.token)

        self.headers = {
            'X-App': "osio",
            'X-Git-Provider': "GitHub",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': self.token
        }

    def get_space_id(env="prod", username='rratnawa', space='delme'):
        """Docstring."""
        _base_url = "https://api.openshift.io/api/namedspaces/{u}/{s}"
        _url = _base_url.format(u=username, s=space)
        _resp = requests.get(_url)
        if _resp.status_code == 200:
            print(WHITE.format("SUCCESS: openshift spaceID"))
            return _resp.json().get('data', {}).get('id')
        else:
            raise Exception(RED.format(
                "Not able to fetch space name `{}`".format(space)))

    def create_booster(self):
        """Create a quickstart booster function."""
        self.space = self.get_space_id()
        payload = {
            "mission": self.mission,
            "runtime": self.runtime,
            "runtimeVersion": self.runtime_version.get(self.runtime),
            "pipeline": self.pipeline[0],
            "projectName": self.application_name,
            "projectVersion": self.project_version,
            "groupId": self.group_id.get(self.runtime),
            "artifactId": self.artifact_id.get(self.runtime),
            "space": self.space,
            "gitRepository": self.application_name
        }
        self.space = 'delme'
        self.handler = 'rratnawa'
        resp = requests.post(self.host, headers=self.headers, data=payload)
        if resp.status_code == 200:
            return 'https://openshift.io/{h}/{s}/create/pipelines'\
                .format(h=self.handler, s=self.space)
        else:
            print("failed", resp.status_code, resp.content)


class CreateQuickStartAction(Action):
    """Action class for deployed applications."""

    def name(self):
        """Return the template name."""
        return 'action_create_quickstart'

    def run(self, dispatcher, tracker, domain):
        """Execute the main logic."""
        C = CreateQuickStart(
            tracker.get_slot("runtime"),
            tracker.get_slot("mission"),
            tracker.get_slot("application_name"),
            tracker.get_slot('handler'))
        link = C.create_booster()
        return [SlotSet('pipeline_link', link)]