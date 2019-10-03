# -*- coding: utf-8 -*-

from odoo import models, fields, api

class player(models.Model):
     _name = 'game.player'
     name = fields.Char()
     fortresses = fields.One2many('game.fortress','player')

class fortress(models.Model):
    _name = 'game.fortress'
    name = fields.Char()
    player = fields.Many2one('game.player')

class resource(models.Model):
    _name = 'game.resource'
    name = fields.Char()
    productions = fields.One2many('game.production','resource') # Llista de coses que produeix
                                                                # o consumeix
class production(models.Model):
    _name = 'game.production'
    name = fields.Char()
    resource = fields.Many2one('game.resource') # Que recurs
    level = fields.Integer() # Cal indicar el que produeix o cunsumeix en cada nivell
    raw = fields.Many2one('game.raw') # Que material
    production = fields.Float()  # Producció per minut

class raw(models.Model):
    _name = 'game.raw'
    name = fields.Char()
