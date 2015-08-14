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


{
    'name': 'Module Code Stats',
    'version': '0.1',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': 'Give stats on the code of the modules',
    'description': """
The goal of this module is to give more information about the origin of the source code and about who is responsible for it. This information is important to the project managers of the Odoo deployment projet. For example, it can help answer the following questions :

* if I suscribe to Odoo Enterprise, how much of my code base will be covered by the contract ? and how much of my code base will not be covered by the contract ?

* how much of my code base is maintained by the OCA ?

* how much of my code base is maintained by the community outside of OCA ?

* how much of my code base is specific and not generic ?


To give an answer to these questions, this module adds several information on the modules :

* the type of module : official, OCA, community or specific

* the repository of the module

* number of lines of code, so as to measure the weight of the module (which gives an idea on the effort required to maintain it !). This information is only given for installed modules to avoid too much computing.

It also adds a graph view on module, so that you can see the number of lines of code per module type, per repository, etc...

This module requires *cloc* : you can install it with the command *sudo apt-get install cloc*

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['base'],
    'external_dependencies': {'python': ['unicodecsv']},
    'data': ['module_view.xml'],
    'installable': True,
}
