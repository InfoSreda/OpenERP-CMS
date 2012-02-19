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
from osv import osv
from osv import fields
from lxml import html
    
class cms_site(osv.osv):
    _name = 'cms.site'
    _description = 'CMS Site'
    _order = 'name'

    _columns = {
        'name': fields.char("Name", size=50, required=True),
        'host': fields.char("Host", size=100, select=1, required=True),
        'default_language_id': fields.many2one('res.lang',
                                       string='Default language', required=True)
    }

cms_site()

class cms_slot(osv.osv):
    _name = 'cms.slot'
    _description = 'CMS Slot'

    _columns = {
        'name': fields.char("Name", size=50, required=True),
    }

cms_slot()

class cms_template(osv.osv):
    _name = 'cms.template'
    _description = 'CMS Template'
    _order = 'name'

    _columns = {
        'name': fields.char("Name", size=50, required=True),
        'slot_ids': fields.many2many('cms.slot', 'cms_templates_slots',
                                             'template_id', 'slot_id', 'Slots'),
    }

cms_template()

class cms_page(osv.osv):
    _name = 'cms.page'
    _description = 'CMS Page'
    _order = 'sequence'
    _rec_name = 'default_title_name'
    _parent_store = True
    
    _columns = {
        'default_title_name': fields.related('title_ids', 'title',
                                             string='Default title',
                                             type='char'),
        'default_title_path': fields.related('title_ids', 'path',
                                             string='Default path',
                                             type='char'),

        'parent_id': fields.many2one('cms.page', 'Parent Page', select=1),
        'child_ids': fields.one2many('cms.page', 'parent_id', 'Child Pages'),
        'publication_date': fields.date('Publication date'),
        'publication_end_date': fields.date('Publication end date'),
        'in_navigation': fields.boolean('In navigation', select=1),
        'soft_root': fields.boolean('Soft root', select=1),
        'reverse_id': fields.char("ID", size=40, select=1),
        'navigation_extenders': fields.char("Attached menu", size=80, select=1),
        'published': fields.boolean('Is published'),
        'template_id': fields.many2one('cms.template','Template',required=True),

        'site_id': fields.many2one('cms.site', 'Site', required=True),
        'title_ids': fields.one2many('cms.title', 'page_id', 'Titles',
                                          required=False, ondelete='cascade'),
        'sequence': fields.integer('Sequence', select=1),
    }


    def _get_first(model_name):
        def wrapper(obj, cr, uid, context):
            model = obj.pool.get(model_name)
            ids = model.search(cr, uid, [], context=context)
            return ids[0] if ids else False
        return wrapper

    _defaults = {
        'site_id': _get_first('cms.site'),
        'template_id': _get_first('cms.template'),
        'in_navigation': lambda *a: True,
        'published': lambda *a: True,
        #'sequence': lambda *a: 1000
    }

    _constraints = [
        (osv.osv._check_recursion, 'Error! You can`t create recursive CMSPage.',
                                                                 ['parent_id'])
    ]

    def write(self, cr, uid, ids, vals, context=None):
        res = super(cms_page, self).write(cr, uid, ids, vals, context)
        if res and 'sequence' in vals:
            # need rewrite title.page_sequence
            for rec in self.browse(cr, uid, ids):
                for title in rec.title_ids:
                    title.write({'page_id': rec.id}, context=context)
        return res

cms_page()


class cms_title(osv.osv):
    _name = 'cms.title'
    _description = 'CMS Title'
    _order = 'page_sequence'
    _rec_name = 'title'

    def _get_path(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        objs = self.browse(cr, uid, ids, context=context)
        for obj in objs:
            if obj.slug and (obj.slug.startswith('http://') or obj.slug.startswith('https://')):
                res[obj.id] = obj.slug
                continue
            path = obj.slug
            if obj.page_id.parent_id:
                title_model = self.pool.get('cms.title')
                parent_ids = title_model.search(cr, uid, [
                    ('page_id', '=', obj.page_id.parent_id.id),
                    ('language_id', '=', obj.language_id.id)],context=context)
                if parent_ids:
                    par_path = title_model.read(cr, uid, parent_ids[0],['path'],
                                         context=context)['path']
                    if par_path:
                        path = '%s/%s' % (par_path, obj.slug)
            res[obj.id] = path
        return res    

    _columns = {
        'language_id': fields.many2one('res.lang', 'Language', required=True),
        'title': fields.char("Title", size=255, required=True),
        'menu_title': fields.char("Menu title", size=255, select=1),
        'slug': fields.char("Slug", size=255, select=1),
        'path': fields.function(_get_path, string='Path', method=True,
                                 store=True, type='char', size=1024, select=1),
        'has_url_overwrite': fields.boolean('Has url overwrite', select=1),
        'application_urls': fields.char('Application', size=200, select=1),
        'redirect': fields.char('Redirect', size=255),

        'meta_title': fields.char('Title', size=512),
        'meta_description': fields.text('Description'),
        'meta_keywords': fields.text('Keywords'),

        'page_title': fields.char('Title', size=255),

        'page_id': fields.many2one('cms.page', 'Page'),
        'placeholder_ids': fields.one2many('cms.placeholder', 'title_id',
                                        'Placeholders'),
        'template_name': fields.related('page_id', 'template_id', 'name',
                                        type='char'),
        'page_sequence': fields.related('page_id', 'sequence',
                                        type='integer', store=True, select=1),

        'publication_date': fields.related('page_id', 'publication_date',
                                       type='date', string='Publication date'),
        'publication_end_date': fields.related('page_id',
                         'publication_end_date', type='date',
                                              string='Publication end date'),
        'old_path': fields.char('Old path', size=512, select=1,
                                readonly=True)
    }

    def _check_unique_path(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            data = self._get_path(cr, uid, [r.id], 'path', [])            
            path = data[r.id]
            same_path_count = self.search(cr, uid,
                           [('page_id.site_id', '=', r.page_id.site_id.id),
                            ('id', '!=', r.id),
                            ('language_id', '=', r.language_id.id),
                            ('path', '=', path)], count=True, context=context)
            return not(same_path_count)

    def _check_count_page_langs(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid,
                     [('id', '!=', r.id),
                      ('page_id.site_id', '=', r.page_id.site_id.id),
                      ('language_id', '=', r.language_id.id),
                      ('page_id', '=', r.page_id.id)], count=True) > 0:
                return False
        return True

    def _check_slug(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.slug and (r.slug.startswith('http://') or r.slug.startswith('https://')):
                continue
            if (r.page_id and r.page_id.parent_id and not r.slug) or \
               (isinstance(r.slug, basestring) and \
                                          not re.search('^[\w-]*$', r.slug)):
                return False
        return True

    _constraints = [
        (_check_count_page_langs, 'Error ! You cannot create CMS Title.',
                                                                     ['title']),
        (_check_unique_path,
              'Error ! You cannot create CMS Title not unique path.', ['path']),
        (_check_slug,
               'Error ! You cannot create CMS Title incorrect slug.', ['slug']),
    ]

    _defaults = {
        'language_id': lambda obj, cr, uid, ctx: obj.pool.get('res.lang').search(cr, uid, [], context=ctx)[0]
    }

cms_title()


class cms_placeholder(osv.osv):
    _name = 'cms.placeholder'
    _description = 'CMS Placeholder'
    _rec_name = 'slot_id'
    _order = 'slot_id'

    SHORT_BODY_LENGTH = 100

    def _get_short_body(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            if not r.body:
                res[r.id] = r.body
            try:
                strip_body = html.fromstring(r.body).text_content().strip()
            except Exception, exc:
                strip_body = 'NOT VALID HTML_TEXT'
            short_body = strip_body[:self.SHORT_BODY_LENGTH]
            if len(strip_body) > self.SHORT_BODY_LENGTH:
                short_body += '...'
            res[r.id] = short_body
        return res

    _columns = {
        'slot_id': fields.many2one('cms.slot', 'Slot',required=True, select=1),
        'body': fields.text('Body'),
        'title_id': fields.many2one('cms.title'),
        'short_body': fields.function(_get_short_body, method=True,
                                        string='Short Body', type='char')
    }

cms_placeholder()
