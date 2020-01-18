# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import random
import math
import json
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta

class ad(models.Model):
    _name = 'game.ad'
    name = fields.Char()
    image = fields.Binary()


class player_ad(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    ad = fields.Binary(compute='_get_ad')
    is_premium = fields.Boolean(compute='_get_ad')

    @api.multi
    def _get_ad(self):
        for p in self:
            sale_premium = self.env['sale.order'].search([('partner_id','=',p.id),('is_premium','=',True),('finished','=',False)])
            if len(sale_premium) > 0:
                p.is_premium = True
            else:
                ads = self.env['game.ad'].search([])
                p.ad = random.choice(ads).image
                p.is_premium = False

    @api.multi
    def sale_premium_account(self):
        for p in self:
            sale = self.env['sale.order'].create({'partner_id': p.id,'is_premium': True})
            product = self.env.ref('game.product_premium')
            sale_order_line = self.env['sale.order.line'].create({'order_id':sale.id,'product_id':product.id})


class sale_premium(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    start = fields.Datetime(default=lambda self: fields.Datetime.now())
    end = fields.Datetime(compute='_get_end')
    finished = fields.Boolean()
    is_premium = fields.Boolean(default=False)

    @api.depends('start')
    def _get_end(self):
        for s in self:
            start = fields.Datetime.from_string(self.start)
            start = start + timedelta(days=30)
            s.end = fields.Datetime.to_string(start)
            if (s.end < fields.Datetime.now()):
                s.write({'finished':True})


