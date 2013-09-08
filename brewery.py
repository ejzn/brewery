# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_itc_config(osv.osv):
    _name = "account.itc.config"
    _description = "Accounting ITC Tax Configuration"
    _columns = {
        'software_code' : fields.char('Software Verification Code', size=128, required=True),
        'transaction_set_id' : fields.char('Transaction Set Id', size=128, required=True),
        'business_number' : fields.char('Business Number', size=20, required=True),
    }
account_itc_config()

class account_itc_return(osv.osv):
    STATE_SELECTION = [
        ('draft', 'Draft Return'),
        ('confirmed', 'Confirmed'),
        ('filed', 'CRA Filed'),
    ]


    _name = "account.itc.return"
    _description = "Accounting ITC Tax Submission"
    _columns = {
        'reporting_period_start' : fields.date('Reporting Period Start', required=True, states={'filed':[('readonly',True)]}, help="The start date of this ITC return"),
        'reporting_period_end' : fields.date('Reporting Period END', required=True, states={'filed':[('readonly',True)]}, help="The end date of this ITC return"),
        'date_filed' : fields.date('Date Filed', states={'filed':[('readonly',True)]}, readonly=True, help="Date the return was processed to CRA"),
        'state' : fields.selection(STATE_SELECTION, 'Status', readonly=True, help="Status of the ITC Return", select=True),
        'line_101' : fields.float('Sales & Revenue', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_105' : fields.float('Total GST/HST', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_108' : fields.float('Total ITC\'s & adj', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_109' : fields.float('Net Tax', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_110' : fields.float('Installments & Revenue', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_111' : fields.float('Rebates', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_205' : fields.float('GST/HST due to aquisition of property', states={'filed':[('readonly',True)]}, digits=[12,2], required=True),
        'line_405' : fields.float('Other GST/HST', digits=[12,2], states={'filed':[('readonly',True)]}, required=True),
        'line_114' : fields.float('Refund Claimed', digits=[12,2], states={'filed':[('readonly',True)]}, required=True),
        'line_115' : fields.float('Amount Owing', digits=[12,2], states={'filed':[('readonly',True)]}, required=True),
        'line_135' : fields.float('Total GST New housing Rebates', digits=[12,2], states={'filed':[('readonly',True)]}, required=True),
        'line_136' : fields.float('Deduction for Pension', digits=[12,2], states={'filed':[('readonly',True)]}, required=True),
    }

    _defaults = {
        'state': 'draft',
        'reporting_period_end': fields.date.context_today,
    }

    # Calculate the values in the object by pulling data from the
    # Accounting module for the specified period
    def action_calculate_period(self, cr, uid, ids, context=None):
        print "Calculating, should return a value here"

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed', 'date_filed': fields.date.context_today(self,cr,uid,context=context)})

    # File the return to CRA
    def action_file(self, cr, uid, ids, context=None):
        # Do some work by sending and receiving the response from CRA, then set to filed.
        self.write(cr, uid, ids, {'state': 'filed', 'date_filed': fields.date.context_today(self,cr,uid,context=context)})

        datas = {
                 'model': 'account_itc',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }

        return {'type': 'ir.actions.report.xml', 'report_name': 'account_itc.return', 'datas': datas, 'nodestroy': True}
        # Now open up the CRA website for our users
        #return {
        #    'type': 'ir.actions.act_url',
        #    'url': 'http://www.cra-arc.gc.ca/gsthst-internetfiletrans/',
        #    'target': 'new'
        #}

    # Cancel a return, not sure if it is possible yet, may need to re-file
    # which is okay, since we can just amend and re-file
    def action_ammend(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})

account_itc_return()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
