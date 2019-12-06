# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import random
from datetime import datetime, timedelta
import math


############### El mercat del joc ##############

class market(models.Model):
    _name = 'game.market'
    name = fields.Char()
    stuff = fields.Many2one('game.stuff')
    stuffk = fields.Many2many('game.stuff', compute='_get_stuff')
    price = fields.Float()
    player = fields.Many2one(related='stuff.player')

    @api.depends('stuff')
    def _get_stuff(self):
        for m in self:
            m.stuffk = m.stuff


############## Els Clans ############################

class clan(models.Model):
    _name = 'game.clan'
    name = fields.Char()
    image = fields.Binary()
    players = fields.One2many('game.player','clan')
    battles = fields.Many2many('game.battle')


########## Les batalles #########################

class battle(models.Model):
    _name = 'game.battle'
    name = fields.Char()
    attack = fields.Many2many('game.player', 'player_attacks') # Cal especificar el nom de la taula
    defend = fields.Many2many('game.player', 'player_defends')
    characters_attack = fields.Many2many('game.character','characters_attack')
    characters_defend = fields.Many2many('game.character','characters_defend')
    def _get_date(self):
        date = datetime.now()+timedelta(hours=3)
        return fields.Datetime.to_string(date)

    date = fields.Datetime(default=_get_date) # Serà calculada a partir de l'hora de creació
    finished = fields.Boolean()


    @api.onchange('attack','defend')
    def onchange_attack(self):
        for b in self:
            characters_available = b.attack.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed==True and p.health > 0)
            characters_available_defense = b.defend.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed == True and p.health > 0)
            return {
                'domain': {'characters_attack': [('id', 'in', characters_available.ids)],
                           'characters_defend': [('id', 'in', characters_available_defense.ids)]},
            }

    def compute_battle(self):
        for b in self:
            at = b.characters_attack.ids
            print(at)
            de = b.characters_defend.ids
            print(de)
            finished = False
            first = True  # La primera ronda es amb dispars, la resta es melee
            while(not finished):
                # L'ordre de la batalla és important,
                # ja que els primers són els primers en atacar defendre
                for i in zip(at,de):
                    c_at = self.env['game.character'].browse(i[0])
                    c_de = self.env['game.character'].browse(i[1])
                    # El nivell de 'war' indica quin dels dos caracters
                    # Està més experimentat. Això li  dona un avantatge percentual
                    ratio_at_de = c_at.war / (c_at.war + c_de.war)
                    ratio_de_at = c_de.war / (c_at.war + c_de.war)
                    print("Ratios: "+str(c_at.war)+" "+str(c_de.war)+" "+str(ratio_at_de)+" "+str(ratio_de_at))
                    if first:
                        # Calcular en base al shot
                        at_best_shot = c_at.stuff.filtered(lambda s: s.type == '0')
                        if at_best_shot:
                            at_best_shot = at_best_shot.sorted(key=lambda s: s.shoot, reverse=True)[0].shoot
                        else:
                            at_best_shot = 0
                        de_best_armor = c_de.stuff.filtered(lambda  s: s.type == '2')
                        if de_best_armor:
                            de_best_armor = de_best_armor.sorted(key=lambda s: s.armor, reverse=True)[0].armor
                        else:
                            de_best_armor = 1
                        ratio_shot_armor = at_best_shot / (at_best_shot + de_best_armor)
                        print(ratio_shot_armor)
                        ratio_at_de = ratio_at_de * ratio_shot_armor
                        print(ratio_at_de)
                        if random.random() < ratio_at_de:
                            damage_de = 100*ratio_at_de
                        else:
                            damage_de = 0
                        print(damage_de)
                        health_de = c_de.health - damage_de
                        if health_de < 0:
                            health_de = 0
                        c_de.write({'health': health_de})
                    else:
                        print('melee')
                        # Calcular en base a la melee
                first = False
                finished = True





