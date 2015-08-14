# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Module Code Stats module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, modules
import os
import subprocess
import logging
import tempfile
import unicodecsv

logger = logging.getLogger(__name__)
SPECIFIC_PREFIX = 'barroux'


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    type = fields.Selection([
        ('official', 'Official'),
        ('oca', 'OCA'),
        ('community', 'Community (excluding OCA)'),
        ('specific', 'Specific'),
        ], string='Module Type', store=True, readonly=True,
        compute='set_module_type_repository')
    repository = fields.Char(
        string='Repository', store=True, readonly=True,
        compute='set_module_type_repository')
    js_code_lines = fields.Integer(
        string='Number of Lines of JS Code',
        compute='_compute_code_lines', readonly=True, store=True)
    xml_code_lines = fields.Integer(
        string='Number of Lines of XML',
        compute='_compute_code_lines', readonly=True, store=True)
    python_code_lines = fields.Integer(
        string='Number of Lines of Python Code',
        compute='_compute_code_lines', readonly=True, store=True)
    css_code_lines = fields.Integer(
        string='Number of Lines of CSS',
        compute='_compute_code_lines', readonly=True, store=True)
    total_code_lines = fields.Integer(
        string='Total Number of Lines of Code',
        compute='_compute_code_lines', readonly=True, store=True)

    @api.one
    @api.depends('author', 'name')
    def set_module_type_repository(self):
        type = False
        module_path = False
        web_addons_path = modules.get_module_path('web')
        official_addons_path = os.path.split(web_addons_path)[0]
        # for the official module, we could loop on addons_path
        # and take the path that contains the 'web' module -> we know it's
        full_module_path = modules.get_module_path(self.name)
        if full_module_path:
            module_path = os.path.split(full_module_path)[0]
        if self.name == 'base':
            type = 'official'
        elif module_path and module_path == official_addons_path:
            type = 'official'
        elif self.author and 'Odoo Community Association' in self.author:
            type = 'oca'
        elif self.name and self.name.endswith('_profile'):
            type = 'specific'
        elif self.name and self.name.startswith(SPECIFIC_PREFIX):
            type = 'specific'
        else:
            type = 'community'
        # set short path
        if module_path:
            module_path = os.path.split(module_path)[1]
        self.type = type
        self.repository = module_path

    @api.one
    @api.depends('name', 'state', 'latest_version', 'author')
    def _compute_code_lines(self):
        js_cl = 0
        xml_cl = 0
        py_cl = 0
        css_cl = 0
        total_cl = 0
        if self.state in ('installed', 'to upgrade'):
            path = modules.get_module_path(self.name)
            logger.debug(
                'Analysing code of module %s located in %s',
                self.name, path)
            csvres = tempfile.NamedTemporaryFile()
            try:
                subprocess.call([
                    'cloc',
                    '--exclude-dir=lib',
                    '--skip-uniqueness',
                    '--exclude-ext=xsd',
                    '--not-match-f="__openerp__.py|index.html"',
                    '--csv',
                    '--out=%s' % csvres.name,
                    path])
                logger.debug("cloc executed via subprocess.call")
                csvres.seek(0)
                res = unicodecsv.reader(csvres, encoding='utf-8')
                for row in res:
                    if row and row[0] == u'files':
                        continue
                    if row and len(row) == 5:
                        lines = int(row[4])
                        total_cl += lines
                        if row[1] == u'Python':
                            py_cl = lines
                        elif row[1] == u'XML':
                            xml_cl = lines
                        elif row[1] == u'Javascript':
                            js_cl = lines
                        elif row[1] == u'CSS':
                            css_cl = lines
            except:
                logger.warning(
                    'Failed to execute the cloc command on module %s',
                    self.name)
            finally:
                csvres.close()

        self.js_code_lines = js_cl
        self.xml_code_lines = xml_cl
        self.python_code_lines = py_cl
        self.css_code_lines = css_cl
        self.total_code_lines = total_cl
