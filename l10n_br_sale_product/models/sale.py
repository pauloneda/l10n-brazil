# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2014  Renato Lima - Akretion                                  #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

from openerp import models, fields, api
from openerp import _
from openerp.exceptions import ValidationError

from openerp.addons import decimal_precision as dp
from openerp.addons.l10n_br_base.tools.misc import calc_price_ratio
from openerp.addons.l10n_br_account_product.models.l10n_br_account_product \
    import (GNRE_RESPONSE,
            GNRE_RESPONSE_DEFAULT)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def onchange_partner_id(self, partner_id):
        result = super(SaleOrder, self).onchange_partner_id(partner_id)

        if not partner_id:
            return result
        partner = self.env['res.partner'].browse(partner_id)
        result['value']['has_gnre'] = partner.has_gnre
        result['value']['gnre_due_days'] = partner.gnre_due_days
        result['value']['gnre_response'] = partner.gnre_response

        return result

    @api.one
    @api.depends('order_line.price_unit', 'order_line.tax_id',
                 'order_line.discount', 'order_line.product_uom_qty',
                 'order_line.freight_value', 'order_line.insurance_value',
                 'order_line.other_costs_value', 'order_line.gnre_value')
    def _amount_all_wrapper(self):
        """
        Wrapper because of direct method passing as parameter
        for function fields
        """
        return self._amount_all()

    @api.one
    def _amount_all(self):
        self.amount_untaxed = 0.0
        self.amount_tax = 0.0
        self.amount_total = 0.0
        self.amount_extra = 0.0
        self.amount_discount = 0.0
        self.amount_gross = 0.0
        self.amount_total_gnre = 0.0

        amount_tax = amount_untaxed = amount_extra = \
            amount_discount = amount_gross = amount_gnre = 0.0
        for line in self.order_line:
            amount_tax += sum(amount for amount in self._amount_line_tax(line))
            amount_extra += (line.insurance_value +
                             line.freight_value + line.other_costs_value)
            amount_untaxed += line.price_subtotal
            amount_discount += line.discount_value
            amount_gross += line.price_gross
            amount_gnre += line.gnre_value

        self.amount_total_gnre = amount_gnre
        self.amount_tax = self.pricelist_id.currency_id.round(amount_tax)
        self.amount_untaxed = self.pricelist_id.currency_id.round(
            amount_untaxed)
        self.amount_extra = self.pricelist_id.currency_id.round(amount_extra)
        self.amount_total = (self.amount_untaxed +
                             self.amount_tax)
        self.amount_discount = self.pricelist_id.currency_id.round(
            amount_discount)
        self.amount_gross = self.pricelist_id.currency_id.round(amount_gross)

    @api.one
    def _amount_line_tax(self, line):
        value = 0.0
        price = line._calc_line_base_price()
        qty = line._calc_line_quantity()
        for computed in line.tax_id.compute_all(
                price,
                qty,
                partner=line.order_id.partner_invoice_id,
                product=line.product_id,
                # line.order_id.partner_id,
                fiscal_position=line.fiscal_position,
                insurance_value=line.insurance_value,
                freight_value=line.freight_value,
                other_costs_value=line.other_costs_value)['taxes']:
            tax = self.env['account.tax'].browse(computed['id'])
            if not tax.tax_code_id.tax_discount:
                value += computed.get('amount', 0.0)
        return value

    @api.model
    def _default_ind_pres(self):
        company = self.env['res.company'].browse(self.env.user.company_id.id)
        return company.default_ind_pres

    @api.one
    def _get_costs_value(self):
        """ Read the l10n_br specific functional fields. """
        freight = costs = insurance = 0.0
        for line in self.order_line:
            freight += line.freight_value
            insurance += line.insurance_value
            costs += line.other_costs_value
        self.amount_freight = freight
        self.amount_costs = costs
        self.amount_insurance = insurance

    @api.one
    def _set_amount_freight(self):
        for line in self.order_line:
            line.write({
                'freight_value': calc_price_ratio(
                    line.price_gross,
                    self.amount_freight,
                    line.order_id.amount_gross),
                })
        return True

    @api.one
    def _set_amount_insurance(self):
        for line in self.order_line:
            line.write({
                'insurance_value': calc_price_ratio(
                    line.price_gross,
                    self.amount_insurance,
                    line.order_id.amount_gross),
                })
        return True

    @api.one
    def _set_amount_costs(self):
        for line in self.order_line:
            line.write({
                'other_costs_value': calc_price_ratio(
                    line.price_gross,
                    self.amount_costs,
                    line.order_id.amount_gross),
                })
        return True

    ind_pres = fields.Selection([
        ('0', u'Não se aplica'),
        ('1', u'Operação presencial'),
        ('2', u'Operação não presencial, pela Internet'),
        ('3', u'Operação não presencial, Teleatendimento'),
        ('4', u'NFC-e em operação com entrega em domicílio'),
        ('9', u'Operação não presencial, outros')], u'Tipo de operação',
        readonly=True, states={'draft': [('readonly', False)]},
        required=False,
        help=u'Indicador de presença do comprador no estabelecimento \
             comercial no momento da operação.', default=_default_ind_pres)
    amount_untaxed = fields.Float(
        compute='_amount_all_wrapper', string='Untaxed Amount',
        digits=dp.get_precision('Account'), store=True,
        help="The amount without tax.", track_visibility='always')
    amount_tax = fields.Float(
        compute='_amount_all_wrapper', string='Taxes', store=True,
        digits=dp.get_precision('Account'), help="The tax amount.")
    amount_total = fields.Float(
        compute='_amount_all_wrapper', string='Total', store=True,
        digits=dp.get_precision('Account'), help="The total amount.")
    amount_extra = fields.Float(
        compute='_amount_all_wrapper', string='Extra',
        digits=dp.get_precision('Account'), store=True,
        help="The total amount.")
    amount_discount = fields.Float(
        compute='_amount_all_wrapper', string='Desconto (-)',
        digits=dp.get_precision('Account'), store=True,
        help="The discount amount.")
    amount_gross = fields.Float(
        compute='_amount_all_wrapper', string='Vlr. Bruto',
        digits=dp.get_precision('Account'),
        store=True, help="The discount amount.")
    amount_freight = fields.Float(
        compute=_get_costs_value, inverse=_set_amount_freight,
        string='Frete', default=0.00, digits=dp.get_precision('Account'),
        readonly=True, states={'draft': [('readonly', False)]})
    amount_costs = fields.Float(
        compute=_get_costs_value, inverse=_set_amount_costs,
        string='Outros Custos', default=0.00,
        digits=dp.get_precision('Account'),
        readonly=True, states={'draft': [('readonly', False)]})
    amount_insurance = fields.Float(
        compute=_get_costs_value, inverse=_set_amount_insurance,
        string='Seguro', default=0.00, digits=dp.get_precision('Account'),
        readonly=True, states={'draft': [('readonly', False)]})
    amount_total_gnre = fields.Float(
        string='Total de Tributos a recolher via GNRE',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_amount_all_wrapper')
    has_gnre = fields.Boolean(
        string=u"Recolhe imposto antecipadamente atraves de GNRE")
    gnre_due_days = fields.Integer(
        string=u"Vencimento (em dias)")
    gnre_response = fields.Selection(
        selection=GNRE_RESPONSE,
        default=GNRE_RESPONSE_DEFAULT,
        string=u'Responsabilidade'
    )

    def _fiscal_comment(self, cr, uid, order, context=None):
        fp_comment = []
        fc_comment = []
        fc_ids = []

        fp_comment = super(SaleOrder, self)._fiscal_comment(
            cr, uid, order, context)

        for line in order.order_line:
            if line.product_id.fiscal_classification_id:
                fc = line.product_id.fiscal_classification_id
                if fc.inv_copy_note and fc.note:
                    if fc.id not in fc_ids:
                        fc_comment.append(fc.note)
                        fc_ids.append(fc.id)

        return fp_comment + fc_comment


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('price_unit', 'tax_id', 'discount', 'product_uom_qty')
    def _amount_line(self):
        price = self._calc_line_base_price()
        qty = self._calc_line_quantity()
        taxes = self.tax_id.compute_all(
            price,
            qty,
            product=self.product_id,
            partner=self.order_id.partner_invoice_id,
            fiscal_position=self.fiscal_position,
            insurance_value=self.insurance_value,
            freight_value=self.freight_value,
            other_costs_value=self.other_costs_value)
        self.gnre_value = taxes['total_gnre']
        self.price_subtotal = (self.order_id.pricelist_id
                               .currency_id.round(taxes['total']))
        self.price_gross = self._calc_price_gross(qty)
        self.discount_value = self.order_id.pricelist_id.currency_id.round(
            self.price_gross - (price * qty))

    insurance_value = fields.Float(
        'Insurance',
        default=0.0,
        digits=dp.get_precision('Account'))
    other_costs_value = fields.Float(
        'Other costs',
        default=0.0,
        digits_compute=dp.get_precision('Account'))
    freight_value = fields.Float(
        'Freight',
        default=0.0,
        digits_compute=dp.get_precision('Account'))
    discount_value = fields.Float(
        compute='_amount_line', string='Vlr. Desc. (-)',
        digits=dp.get_precision('Sale Price'))
    price_gross = fields.Float(
        compute='_amount_line', string='Vlr. Bruto',
        digits=dp.get_precision('Sale Price'))
    price_subtotal = fields.Float(
        compute='_amount_line', string='Subtotal',
        digits=dp.get_precision('Sale Price'))
    gnre_value = fields.Float(
        compute='_amount_line',
        string=u'Valor do recolhimento via GNRE',
        digits=dp.get_precision('Sale Price'))
    xped = fields.Char(
        string=u"Código do Pedido (xPed)",
        size=15,
    )
    nitemped = fields.Char(
        string=u"Item do Pedido (nItemPed)",
        size=6,
    )

    @api.onchange("nitemped")
    def _check_nitemped(self):
        if self.nitemped and not self.nitemped.isdigit():
            raise ValidationError(
                _(u"nItemPed must be a number with up to six digits")
            )

    @api.model
    def _fiscal_position_map(self, result, **kwargs):
        context = dict(self.env.context)
        context.update({'use_domain': ('use_sale', '=', True)})
        fp_rule_obj = self.env['account.fiscal.position.rule']

        partner_invoice = self.env['res.partner'].browse(
            kwargs.get('partner_invoice_id'))

        product_fc_id = fp_rule_obj.with_context(
            context).product_fiscal_category_map(
                kwargs.get('product_id'),
                kwargs.get('fiscal_category_id'),
                partner_invoice.state_id.id)

        if product_fc_id:
            kwargs['fiscal_category_id'] = product_fc_id

        result['value']['fiscal_category_id'] = kwargs.get(
            'fiscal_category_id')

        result.update(fp_rule_obj.with_context(context).apply_fiscal_mapping(
            result, **kwargs))
        fiscal_position = result['value'].get('fiscal_position')
        product_id = kwargs.get('product_id')

        if product_id and fiscal_position:
            obj_fposition = self.env['account.fiscal.position'].browse(
                fiscal_position)
            obj_product = self.env['product.product'].browse(product_id)
            context.update({
                'fiscal_type': obj_product.fiscal_type,
                'type_tax_use': 'sale', 'product_id': product_id})
            taxes = obj_product.taxes_id
            if obj_product.fiscal_classification_id:
                taxes |= fp_rule_obj.with_context(
                    context).product_fcp_map(
                    kwargs.get('product_id'), partner_invoice.state_id)
            tax_ids = obj_fposition.with_context(context).map_tax(taxes)
            result['value']['tax_id'] = tax_ids

        return result

    def _prepare_order_line_invoice_line(self, cr, uid, line,
                                         account_id=False, context=None):
        result = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id, context)

        result['insurance_value'] = line.insurance_value
        result['other_costs_value'] = line.other_costs_value
        result['freight_value'] = line.freight_value
        result['xped'] = line.xped
        result['nitemped'] = line.nitemped

        # FIXME
        # Necessário informar estes campos pois são related do
        # objeto account.invoice e quando o método create do
        # account.invoice.line é invocado os valores são None
        result['company_id'] = line.order_id.company_id.id
        result['partner_id'] = line.order_id.partner_id.id

        if line.product_id.fiscal_type == 'product':
            if line.fiscal_position:
                cfop = self.pool.get("account.fiscal.position").read(
                    cr, uid, [line.fiscal_position.id], ['cfop_id'],
                    context=context)
                if cfop[0]['cfop_id']:
                    result['cfop_id'] = cfop[0]['cfop_id'][0]
                result['ind_final'] = line.fiscal_position.ind_final
        return result
