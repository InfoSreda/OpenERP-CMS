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

import re
import uuid
import base64
import os

from osv import osv
from osv import fields

URL_PREFIX = '/cms/media'


class media_file(osv.osv):

    _name = 'cms.media.file'
    _rec_name = 'path'

    def _get_path(self, cr, uid, ids, field_name, arg, context):
        result = {}
        
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.parent_id:
                path = '/'.join((obj.parent_id.path, obj.name or ''))
            else:
                path = obj.name
            result[obj.id] = path
        return result

    def _get_url(self, cr, uid, ids, field_name, arg, context):
        result = {}
        
        for obj in self.browse(cr, uid, ids, context=context):            
            result[obj.id] = '/'.join((URL_PREFIX, obj.path))
        return result

    def get_data(self, cr, uid, path, context=None):
        ids = self.search(cr, uid, [('path','=',path)], limit=1,context=context)
        if not ids:
            return ''
        return self.read(cr, uid, ids[0], ['data']).get('data') or ''


    _columns = {
        'parent_id': fields.many2one('cms.media.file', string='Folder'),
        'child_ids': fields.one2many('cms.media.file', 'parent_id',
                                     string='Files'),
        'is_folder': fields.boolean(string='Is folder'),
        'name': fields.char('Folder name', size=64),

        'path': fields.function(_get_path,
                                type='char', method=True,
                                store=True, size=512,
                                string=u'Full path', select=True),
        'url': fields.function(_get_url,
                                type='char', method=True,
                                string=u'Url'),

        'comment': fields.text('Сommentary'),
        'data': fields.binary('Data')
    }

    _defaults = {
        'is_folder': lambda *a: True
        }

media_file()
