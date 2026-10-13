"""Expose the standalone provider under its upstream package name for local tests."""

import sys

import provider as provider_package

sys.modules["music_assistant.providers.dlna_receiver"] = provider_package
