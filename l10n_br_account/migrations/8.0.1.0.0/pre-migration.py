# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 KMEE INFORMATICA LTDA - Luis Felipe Miléo
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

import logging
from openerp.openupgrade import openupgrade


logger = logging.getLogger('OpenUpgrade.l10n_br_account')

column_renames = {
    'account_fiscal_position': [
        ('id_dest', None),
    ],
    'account_fiscal_position_template': [
        ('id_dest', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
