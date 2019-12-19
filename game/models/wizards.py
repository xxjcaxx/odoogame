from odoo import models, fields, api, tools

from openerp.exceptions import ValidationError


class add_raws(models.TransientModel):
    _name = 'game.add_raws'

    def _default_resource(self):
        return self.env['game.resource'].browse(self._context.get('active_id'))

    resource = fields.Many2one('game.resource', default=_default_resource)
    productions = fields.Many2many('game.raw', related='resource.produccions')
    production_spend = fields.Selection(related='resource.production_spend')
    need = fields.Float(compute='_get_needs')

    @api.depends('resource') # És precís el depends, ja que és un model general al vol
    def _get_needs(self):
        for a in self:
            print(a.resource.production_spend)
            need = 0
            # Costs productius
            #for raw in a.resource.produccions:
            #    raws_needed = {'0': 0, '1': raw.construccio, '2': raw.armesblanques, '3': raw.armesfoc,
            #                   '4': raw.nutricio, '5': raw.tecnologia, '6': raw.medicina, '7': raw.energia}
            #    need = need + raws_needed[a.resource.production_spend] * raw.production_cost
            # Costs no productius
            if (len(a.resource.produccions) == 0 and a.resource.production_spend != '0'):
                need = 2 ** a.resource.level * (len(a.resource.characters) + 1)
                

            a.need = need

