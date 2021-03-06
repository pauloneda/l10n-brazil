# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Kmee - www.kmee.com.br
#   @authors Daniel Sadamo <daniel.sadamo@kmee.com.br>
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

from openerp import models, fields, api
from openerp.osv import osv


class WizardValuationHistory(models.TransientModel):
    _inherit = 'wizard.valuation.history'

    @api.multi
    def compute(self, cr, uid, ids, date):
        ctx = dict(self._context)
        ctx['history_date'] = date
        fields = [
            'fiscal_classification_id',
            'product_id',
            'location_id',
            'move_id',
            'company_id',
            'date',
            'source',
            'quantity',
            'inventory_value',
            'price_unit_on_quant'
        ]
        group_by = [
            'product_id',
            'location_id',
            'fiscal_classification_id'
        ]
        result = self.env['stock.history'].read_group(domain=[], fields=fields,
                                                      groupby=group_by,
                                                      context=ctx)
        return result


class stock_history(osv.osv):
    _inherit = 'stock.history'

    def read_group(self, cr, uid, domain, fields, groupby, offset=0,
                   limit=None, context=None, orderby=False, lazy=True):
        res = super(stock_history, self).read_group(
            cr, uid, domain, fields, groupby, offset=offset, limit=limit,
            context=context, orderby=orderby, lazy=lazy)

        if 'fiscal_classification_id' in fields:
            product_obj = self.pool.get('product.product')
            for line in res:
                product = product_obj.browse(cr, uid, line['product_id'][0])
                fiscal_class = product.fiscal_classification_id.code
                line.update({'fiscal_classification_id': fiscal_class})
        return res


class StockHistory(models.Model):
    _inherit = 'stock.history'

    fiscal_classification_id = fields.Many2one(
        comodel_name='account.product.fiscal.classification',
        string='NCM',
        related='product_id.fiscal_classification_id'
    )
