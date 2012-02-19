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

{
    'name': 'openerp cms',
    'version': '0.2.0',
    'category': 'Others',
    'description': """OpenERP CMS""",
    'author': 'Infosreda LLC',
    'website': 'http://infosreda.com/',
    'depends': ['base', 'web'],
    'init_xml': [],
    'update_xml': [
        'security/cms_security.xml',
        'security/ir.model.access.csv',
        'cms_view.xml',
        'media_view.xml',
        ],
    "js": [
        'static/src/js/tiny_mce/jquery.tinymce.js',
        'static/src/js/oe_tinymce.js',
    ],
    "css": [],
    'qweb' : [],
    'installable': True,
    'active': False,
    'web': True,
}
