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


class assign_raws(models.TransientModel):
    _name = 'game.assign_raws'

    def _default_raws(self):
        return self.env['game.raws'].browse(self._context.get('active_id'))

    def _default_clan(self):
        clan = self.env['game.raws'].browse(self._context.get('active_id')).clan
        return clan

    raws = fields.Many2one('game.raws', default=_default_raws)
    clan = fields.Many2one('game.clan', default=_default_clan)
    player = fields.Many2one('res.partner', domain="[('clan','=',clan)]")
    quantity = fields.Float('')
    max = fields.Float(related='raws.quantity', string='Max')

    def launch(self):
        for i in self:
            player = i.player
            if i.quantity > i.max:
                q = i.max
            else:
                q = i.quantity

            raw = i.raws.raw.id
            raws =  player.raws.search([('raw', '=', raw),('player','=',player.id)])[0]
            raws.write({'quantity': q + raws.quantity})
            i.raws.write({'quantity': i.raws.quantity - q})


class create_battle(models.TransientModel):
    _name = 'game.create_battle'

    def _default_attacker(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))  # El context conté, entre altre coses,
        # el active_id del model que està obert.

    attack = fields.Many2one('res.partner', default=_default_attacker, readonly=True)
    clan = fields.Many2one('game.clan',related='attack.clan')
    characters = fields.Many2many('game.character', domain="[('player','=',attack)]")
    defend = fields.Many2one('res.partner',domain="[('clan','!=',clan)]")

    state = fields.Selection([
        ('i', "Player Attack"),
        ('c', "Characters Selection"),
        ('d', "Defense Selection"),
    ], default='i')



    @api.multi
    def next(self):
        if self.state == 'i':
            self.state = 'c'
        elif self.state == 'c':
            self.state = 'd'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Battle',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


    @api.multi
    def create_battle(self):
        print(self.attack)
        print(self.characters)
        print(self.defend)
        b = self.env['game.battle'].create({
            'attack': [(6,0,[self.attack.id])],
            'characters_attack': [(6,0,self.characters.ids)],
            'defend': [(6,0,[self.defend.id])]
        })
        return {
            'name': 'Battle',
            'view_type': 'form',
            'view_mode': 'form',  # Pot ser form, tree, kanban...
            'res_model': 'game.battle',  # El model de destí
            'res_id': b.id,  # El id concret per obrir el form
            # 'view_id': self.ref('wizards.reserves_form') # Opcional si hi ha més d'una vista posible.
            'context': self._context,  # El context es pot ampliar per afegir opcions
            'type': 'ir.actions.act_window',
            'target': 'current',  # Si ho fem en current, canvia la finestra actual.
        }


class proves_wizardraws(models.TransientModel):
        _name = 'game.proves_wizardraws'

        wiz = fields.Many2one('game.proves_wizard')
        raw = fields.Many2one('game.raw')
        quantity = fields.Integer()


class proves_wizard(models.TransientModel):
    _name = 'game.proves_wizard'

    def _default_player(self):
        print(self.id)
        return self.env['res.partner'].browse(self._context.get('active_id'))

    player = fields.Many2one('res.partner', default=_default_player)
    raw = fields.Many2one('game.raw')
    quantity = fields.Integer()
    #raws = fields.Many2many('game.proves_wizardraws', compute='_get_raws')
    raws = fields.One2many('game.proves_wizardraws', 'wiz')

    def _get_raws(self):
        for p in self:
            list= self.env['game.proves_wizardraws'].search([])
            p.raws = list.ids


    def create_raws(self):
        print(self.raw.id)
        raw = self.env['game.proves_wizardraws'].create({'wiz': self.id, 'raw': self.raw.id, 'quantity': self.quantity})
        print(self.id)
        print(raw)
        return {
            'name': 'proves wizards',
            'view_type': 'form',
            'view_mode': 'form',  # Pot ser form, tree, kanban...
            'res_model': 'game.proves_wizard',  # El model de destí
            'res_id': self.id,  # El id concret per obrir el form
            # 'view_id': self.ref('wizards.reserves_form') # Opcional si hi ha més d'una vista posible.
            'context': self._context,  # El context es pot ampliar per afegir opcions
            'type': 'ir.actions.act_window',
            'target': 'new',  # Si ho fem en current, canvia la finestra actual.
        }


