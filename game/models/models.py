# -*- coding: utf-8 -*-

from odoo import models, fields, api

class player(models.Model):
     _name = 'game.player'
     name = fields.Char()
     fortresses = fields.One2many('game.fortress','player')
     resources = fields.Many2many('game.resource') # Este sera computat
     raws = fields.One2many('game.raws','player')

     @api.multi
     def reset_player(self):
         for p in self:
             f_template = self.env.ref('game.fortress1')
             f = self.env['game.fortress'].create({
                 'name':'Choose the name of your fortress',
                 'image': f_template.image,
                 'template': False,
                 'level': 1,
                 'player': p.id
             })

class fortress(models.Model):
    _name = 'game.fortress'
    name = fields.Char()
    player = fields.Many2one('game.player')
    image = fields.Binary()
    template = fields.Boolean()
    resources = fields.One2many('game.resource','fortress')

class resource(models.Model):
    _name = 'game.resource'
    name = fields.Char()
    productions = fields.One2many('game.production','resource') # Llista de coses que produeix
                                                                # o consumeix
    costs = fields.One2many('game.cost','resource')
    image = fields.Binary()
    fortress = fields.Many2one('game.fortress')
    level = fields.Integer()
    template = fields.Boolean()

class production(models.Model):
    _name = 'game.production'
    name = fields.Char()
    resource = fields.Many2one('game.resource') # Que recurs
    level = fields.Integer() # Cal indicar el que produeix o consumeix en cada nivell
    raw = fields.Many2one('game.raw') # Que material
    production = fields.Float()  # Producció per minut

class cost(models.Model):
    _name = 'game.cost'
    name = fields.Char()
    resource = fields.Many2one('game.resource') # Que recurs
    level = fields.Integer() # Cal indicar el que consumeix en cada nivell
    raw = fields.Many2one('game.raw') # Que material
    cost = fields.Float()  #cost total

class raw(models.Model):
    _name = 'game.raw'
    name = fields.Char()
    image = fields.Binary()
    public_hash = fields.Char()
    hidden_hash = fields.Char() # El hash és com la composició atòmica, que no es sap inicialment.
    # Propietats dels materials:
    construccio = fields.Float()
    armesblanques = fields.Float()
    armesfoc = fields.Float()
    nutricio = fields.Float()
    tecnologia = fields.Float()
    medicina = fields.Float()
    energia = fields.Float()

class raws(models.Model):
    _name = 'game.raws'
    name = fields.Char()
    player = fields.Many2one('game.player')
    raw = fields.Many2one('game.raw')
    quantity = fields.Float()

# Un recurs és, per exemple, una mina, que consumeix electricitat i produeix varis materials a un ritme distint
# Cada recurs té una llista de production que indica qué i quant produeix o consumeix.
# Els materials inicials tenen unes propietats basiques, hi ha milers de materials primaris per descobrir i
# amés es poden mesclar entre ells per tindre altres propietats.
# Un jugador pot descobrir un material i publicar el seu hash o no. Pot anar provant hashes (tarda un temps) o
# invertir en educacio i investigacio i ser mes probable que el trobe.
# La gracia esta en que els jugadors creen una base de dades del que van descobrint i que siga o no pública.



