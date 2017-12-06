# coding: utf-8
#    Base Module Code Stats module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, modules
import os
import subprocess
import logging
import tempfile
import unicodecsv

logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    type = fields.Selection([
        ('official', 'Official'),
        ('oca', 'OCA'),
        ('community', 'Community (excluding OCA)'),
        ('specific', 'Specific'),
        ], string='Module Type', store=True, readonly=True,
        compute='set_module_type_repository')
    integrator = fields.Selection([
        ('with_integrator', 'With your Integrator'),
        ('only_integrator', 'By your Integrator'),
        ('other', 'Other integrator'),
        ], string='Integrator', store=True, readonly=True,
        compute='_compute_integrator',
        help="Indicate the degree of participation of the integrator")
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

    @api.multi
    @api.depends('author', 'name')
    def _compute_integrator(self):
        for rec in self:
            if rec.author and self._get_integator_name() in rec.author and \
                    len(self._get_integator_name()) == len(rec.author):
                rec.integrator = 'only_integrator'
            elif rec.author and self._get_integator_name() in rec.author:
                rec.integrator = 'with_integrator'
            else:
                rec.integrator = 'other'

    @api.model
    def _get_integator_name(self):
        """ Customize with the integrator name """
        return 'Akretion'

    @api.model
    def _get_specific_prefix_module(self):
        """ Customize with the prefix of your specific modules """
        return 'barroux'

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
        elif isinstance(self.name, (str, unicode)) and self.name.endswith(
                '_profile'):
            type = 'specific'
        elif isinstance(self.name, (str, unicode)) and self.name.startswith(
                self._get_specific_prefix_module()):
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
                    '--follow-links',
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
            except Exception:
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
