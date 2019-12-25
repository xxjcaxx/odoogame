# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import random
from datetime import datetime, timedelta
import math
from openerp.exceptions import ValidationError

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
    image_small = fields.Binary(string='Clan Image', compute='_get_images', store=True)
    players = fields.One2many('game.player','clan')
    battles = fields.Many2many('game.battle')

    @api.depends('image')
    def _get_images(self):
        for i in self:
            image = i.image
            data = tools.image_get_resized_images(image)
            i.image_small = data["image_small"]


########## Les batalles #########################

class battle(models.Model):
    _name = 'game.battle'
    name = fields.Char()
    attack = fields.Many2many('game.player', relation='player_attacks', column1='b_a',column2='p_a') # Cal especificar el nom de la taula
    defend = fields.Many2many('game.player', relation='player_defends', column1='b_d',column2='p_d')
    characters_attack = fields.Many2many('game.character',relation='characters_attack')
    characters_defend = fields.Many2many('game.character',relation='characters_defend')
    state = fields.Selection([('1','Creation'),('2','Character Selection'),('3','Waiting'),('4','Finished')], compute='_get_state')
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
            check = b._check_battle()

            result = {
                'domain': {'characters_attack': [('id', 'in', characters_available.ids)],
                           'characters_defend': [('id', 'in', characters_available_defense.ids)],
                           'attack': [('id','not in', b.defend.ids)], 'defend': [('id','not in', b.attack.ids)],
                           },
            }
            if not check[0]:
                warning = {'title': "Battle not valid", 'message': check[1]}
                result['warning'] = warning
            return result

    # Funció privada cridada tant per el onchenge com per els constrains
    def _check_battle(self):
        result = [True,'']  # True és correcta i el missatge en cas de incorrecta
        attackers = self.attack
        defenders = self.defend
        if len(attackers) > 0 and len(defenders) > 0:
            # Tots els atacants i defensors han d'estar en el mateix clan
            if len(attackers.mapped('clan')) > 1:
                result = [False,'All attackers have to be the same clan']
                return result
            if len(defenders.mapped('clan')) > 1:
                result = [False,'All attackers have to be the same clan']
                return result
            if defenders[0].clan == attackers[0].clan:
                result = [False,'One clan cannot attack himself']
                return result

            # Tots els caracters atacants ha de ser de jugadors atacants
            if defenders.ids != self.characters_defend.mapped('player.id'):
                result = [False,'All the characters have to be from defender players']
                return result
            if attackers.ids != self.characters_attack.mapped('player.id'):
                result = [False,'All the characters have to be from attacker players']
                return result
        return result



    @api.multi
    def _get_state(self):
        for b in self:
            b.state = '1'
            if len(b.attack) > 0 and len(b.defend) > 0:
                b.state = '2'
            if len(b.characters_attack) > 0 and len(b.characters_defend) > 0:
                b.state = '3'
            if b.finished == True:
                b.state = '4'

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





