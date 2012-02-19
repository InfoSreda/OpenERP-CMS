# -*- coding: utf-8 -*-

##############################################################################
#
#    Authors: Boris Timokhin, Peter A. Kurishev
#    Participants: Alexey Samoukin, Dmitry Zhuravlev-Nevsky
#    Copyright (C) 2011 - 2012 by InfoSreda LLC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import mimetypes
import os
import time
import base64
import web.common.http as openerpweb

DEFAULT_MIMETYPE = 'application/octet-stream'

def set_valid_session_id(func):
    '''
    OpenERP by default get session_id from request.params
    That decorator get first active session from sessio pool
    '''
    def wrapper(self, request, *args, **kwargs):
        for sess in request.httpsession.itervalues():
            if sess._uid:
                request.session = sess
                break
        request.session.config = request.config
        return func(self, request, *args, **kwargs)
    return wrapper


class CmsMedia(openerpweb.Controller):
    _cp_path = '/cms'

    pref = _cp_path + '/media/'

    def get_mime_type(self, file_name):
        mime_type = mimetypes.guess_type(file_name)[0]
        if mime_type is None:
            return DEFAULT_MIMETYPE
        return mime_type

    @openerpweb.httprequest
    @set_valid_session_id
    def media(self, request, **kwargs):
        file_path = request.httprequest.path[len(self.pref):]
        MediaFile = request.session.model('res.partner')
        context = request.session.eval_context(request.context)
        data = request.session.model('cms.media.file').get_data(file_path,
                                                                context)
        data = base64.decodestring(data)
        mime_type = self.get_mime_type(file_path.rsplit('/', 1)[-1])
        return request.make_response(data, [('Content-Type',
                                             mime_type)])
