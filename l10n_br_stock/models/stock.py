# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2009  Renato Lima - Akretion
# Copyright (C) 2012  Raphaël Valyi - Akretion
# Copyright (C) 2014  Luis Felipe Miléo - KMEE - www.kmee.com.br
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import models, fields


class StockIncoterms(models.Model):
    _inherit = 'stock.incoterms'

    freight_responsibility = fields.Selection([('0', u'Emitente'),
                                               ('1', u'Destinatário'),
                                               ('2', u'Terceiros'),
                                               ('9', u'Sem Frete')],
                                              'Frete por Conta',
                                              required=True,
                                              default='0')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    cnpj_cpf = fields.Char(
        string=u'CNPJ/CPF',
        related='partner_id.cnpj_cpf',
    )
    legal_name = fields.Char(
        string=u'Razão Social',
        related='partner_id.legal_name',
    )
    ie = fields.Char(
        string=u'Inscrição Estadual',
        related='partner_id.inscr_est',
    )