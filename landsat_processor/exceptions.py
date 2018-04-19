#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TMSError(Exception):
    """Class for TMS error exception for this module."""

    def __init__(self, errors, *args, **kwargs):
        super(TMSError, self).__init__(*args, **kwargs)
        self.errors = errors
    pass


class XMLError(Exception):
    """Class for XML error exception for this module."""

    def __init__(self, errors, *args, **kwargs):
        super(XMLError, self).__init__(*args, **kwargs)
        self.errors = errors
    pass
