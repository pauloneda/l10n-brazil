# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
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
    'name': 'Brazilian Invoice on Timesheets',
    'category': 'Sales Management',
    'author': 'KMEE, Odoo Community Association (OCA)',
    'website': 'http://odoo-brasil.org',
    'version': '8.0.0.0.0',
    'depends': [
        'l10n_br_account',
        'account_analytic_analysis',
    ],
    'data': [
    ],
    'test': [
        'test/test_hr_timesheet_invoice.yml',
        'test/test_hr_timesheet_invoice_no_prod_tax.yml',
        'test/hr_timesheet_invoice_report.yml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
