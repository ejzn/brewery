# -*- coding: utf-8 -*-
##############################################################################
#
#	ENAPPS Canada
#    Copyright (C) 2013 http://enapps.ca
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
    'name': 'Brewery Management Module for Canadian Breweries',
    'version': '1.0',
    'category': 'Stock',
    'description': """
 Manage your Brewery Batches, Recipes and Stock
========================================================

By adding Batches, recipes, some special fields and the Doc 60 license requirements
this module allows Breweries to easily manage their operations.

""",
    'author': 'ENAPPS Canada',
    'website': 'http://www.enapps.ca',
    'images': ['images/something.jpeg'],
    'depends': ['web','sales', 'l10n_ca'],
    'data': [
        'brewery_view.xml',
    ],
    'css': ['static/src/css/style.css'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
