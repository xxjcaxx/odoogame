# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
    players = fields.One2many('res.partner','clan')
    battles = fields.Many2many('game.battle')
    raws = fields.One2many('game.raws','clan', domain= lambda s: [('quantity','>',0)])

    @api.depends('image')
    def _get_images(self):
        for i in self:
            image = i.image
            data = tools.image_get_resized_images(image)
            i.image_small = data["image_small"]

    @api.model
    def create(self, values):
        new_id = super(clan, self).create(values)
        for i in self.env['game.raw'].search([]): # Assignar tots els Raws amb 0
            r = self.env['game.raws'].create({'name': i.name, 'clan': new_id.id, 'raw': i.id, 'quantity': 0})
        return new_id


########## Les batalles #########################

class battle(models.Model):
    _name = 'game.battle'
    name = fields.Char(compute='_get_name')
    attack = fields.Many2many('res.partner', relation='player_attacks', column1='b_a',column2='p_a', domain="[('is_player','!=',True)]") # Cal especificar el nom de la taula
    defend = fields.Many2many('res.partner', relation='player_defends', column1='b_d',column2='p_d', domain="[('is_player','!=',True)]")
    characters_attack_available = fields.Many2many('game.character', compute='_get_characters_available')
    characters_defend_available = fields.Many2many('game.character', compute='_get_characters_available')
    characters_attack = fields.Many2many('game.character',relation='characters_attack', domain="[('id', 'in', characters_attack_available)]")
    characters_defend = fields.Many2many('game.character',relation='characters_defend', domain="[('id', 'in', characters_defend_available)]")
    state = fields.Selection([('1','Creation'),('2','Character Selection'),('3','Waiting'),('4','Finished')], compute='_get_state')
    time_remaining = fields.Char(compute='_get_state')
    def _get_date(self):
        date = datetime.now()+timedelta(hours=3)
        return fields.Datetime.to_string(date)

    date = fields.Datetime(default=_get_date) # Serà calculada a partir de l'hora de creació
    finished = fields.Boolean()


    @api.multi
    def _get_characters_available(self):
        for c in self:
            c.characters_attack_available =  c.attack.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed==True and p.health > 0)
            c.characters_defend_available = c.defend.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed == True and p.health > 0)



    @api.onchange('attack','defend')
    def onchange_attack(self):
        for b in self:
            characters_available = b.attack.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed==True and p.health > 0)
            characters_available_defense = b.defend.mapped('fortresses').mapped('characters').filtered(
                lambda p: p.unemployed == True and p.health > 0)

            b.characters_attack_available = characters_available
            b.characters_defend_available = characters_available_defense


            attackers = self.attack
            defenders = self.defend
            result={}

            if len(attackers) > 0 and len(defenders) > 0:
                # Tots els atacants i defensors han d'estar en el mateix clan
                if len(attackers.mapped('clan')) > 1:
                    warning = {'title': "Battle not valid", 'message': 'All attackers have to be the same clan'}
                    result['warning'] = warning
                    return result

                if len(defenders.mapped('clan')) > 1:
                    warning = {'title': "Battle not valid", 'message': 'All attackers have to be the same clan'}
                    result['warning'] = warning
                    return result

                if defenders[0].clan == attackers[0].clan:
                    warning = {'title': "Battle not valid", 'message': 'One clan cannot attack himself'}
                    result['warning'] = warning
                    return result

                # Tots els caracters atacants ha de ser de jugadors atacants
                if len(self.characters_defend) > 0 and defenders.ids != self.characters_defend.mapped('player.id'):
                    warning = {'title': "Battle not valid", 'message': 'All the characters have to be from defender players'}
                    result['warning'] = warning
                    return result

                if len(self.characters_attack) > 0 and attackers.ids != self.characters_attack.mapped('player.id'):
                    warning = {'title': "Battle not valid", 'message': 'All the characters have to be from attacker players'}
                    result['warning'] = warning
                    return result


            # En cas de superar tots els tests
            result = {
                'domain': {'characters_attack': [('id', 'in', characters_available.ids)],
                           'characters_defend': [('id', 'in', characters_available_defense.ids)],
                           'attack': [('id','not in', b.defend.ids),('is_player','=',True)], 'defend': [('id','not in', b.attack.ids),('is_player','=',True)],
                           #'attack': [('clan', 'in', b.attack.mapped('clan'))], 'defend': [('clan', 'in', b.defend.mapped('clan'))],
                           },
            }
            if len(attackers) > 0:
                result['domain']['attack'] = [('id','not in', b.defend.ids),('clan', 'in', b.attack.mapped('clan').ids),('clan','not in',b.defend.mapped('clan').ids)]
            if len(defenders) > 0:
                result['domain']['defend'] = [('id', 'not in', b.attack.ids),('clan', 'in', b.defend.mapped('clan').ids),('clan','not in',b.attack.mapped('clan').ids)]

            return result

    @api.depends('attack','defend')
    def _get_name(self):
        for b in self:
            name = ''
            for i in b.attack:
                name = name  + i.name + ', '
            name = name + ' VS '
            for i in b.defend:
                name = name + i.name  + ', '
            b.name = name


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
            start = datetime.now()
            end = fields.Datetime.from_string(b.date)
            relative = relativedelta(end, start)
            if end > start:
                b.time_remaining = str(relative.hours)+":"+str(relative.minutes)
            else:
                b.time_remaining = '00:00'

    def compute_battle(self):
        for b in self:
            at = b.characters_attack.ids  # Els atacants
            print(at)
            de = b.characters_defend.ids  # Els Defensors
            print(de)
            finished = False
            first = True  # La primera ronda es amb dispars, la resta es melee
            rounds = 1
            while(not finished):
                # L'ordre de la batalla és important,
                # ja que els primers són els primers en atacar defendre
                for i in zip(at,de):
                    c_at = self.env['game.character'].browse(i[0]) # El caracter atacant
                    c_de = self.env['game.character'].browse(i[1])
                    b.calculate_attack(c_at,c_de,first)
                    b.calculate_attack(c_de,c_at,first)
                at = b.characters_attack.filtered(lambda c: c.health > 0).ids
                de = b.characters_defend.filtered(lambda c: c.health > 0).ids
                first = False
                if len(at) == 0 or len(de) == 0:
                    finished = True
                else:
                    rounds = rounds + 1

            # Ja ha acabat, ara a repartir experiencia i botin de guerra
            if len(at) == 0:
                wins = 'Defenders ('+str(len(de))+' survivors)'
                for d in self.env['game.character'].browse(de):
                    d.write({'war':d.war+100})
                botin = b.characters_attack.mapped('stuff')
                players = b.defend.ids
                for s in botin:
                    player = random.choice(players)
                    s.write({'character':False,'player':player})
            else:
                wins = 'Attackers ('+str(len(at))+' survivors)'
                for a in self.env['game.character'].browse(at):
                    a.write({'war':a.war+100}) # Augmenta la experiència en guerra de l'atacant
                botin = b.characters_defend.mapped('stuff') # Totes les armes passen al botin de guerra
                players = b.attack.ids
                for s in botin:
                    player = random.choice(players)
                    s.write({'character':False,'player':player})
                # L'atacant ataca per obtindre recursos del defensor
                first_defender = b.defend[0]
                #print(first_defender)
                for r in first_defender.raws:
                    raw = r.raw.id
                    raws  = b.attack[0].clan.raws.search([('raw','=',raw),('clan','=',b.attack[0].clan.id)])[0]
                    #print(raws)
                    raws.write({'quantity':r.quantity/2}) # El clan obté la meitat dels recursos del defensor

            # Anem a fer que alguns dels caiguts siguen ferits i no morts
            death = (b.characters_attack + b.characters_defend).filtered(lambda c: c.health == 0)
            for d in death:
                if random.random() > 0.5: # 50% de que no estiga mort
                    d.write({'health':1,'war':d.war+50}) # Augmenta la seua experiencia en guerra


            self.env['game.log'].create({'title': 'Battle '+str(b.name), 'description': wins+' wins in '+str(rounds)+' rounds'})
            b.write({'finished':True})

    def calculate_attack(self,c_at,c_de,first):
        print('Ataca: '+c_at.name+' Defen: '+c_de.name)
        # El nivell de 'war' indica quin dels dos caracters
        # Està més experimentat. Això li  dona un avantatge percentual
        ratio_at_de = c_at.war / (c_at.war + c_de.war)
        ratio_de_at = c_de.war / (c_at.war + c_de.war)
        print("Ratios: At. War: "+str(c_at.war)+" Def War: "+str(c_de.war)+" Ratio At: "+str(ratio_at_de)+" Ration Def: "+str(ratio_de_at))
        if first:
            # Calcular en base al shot
            at_best_shot = c_at.stuff.filtered(lambda s: s.type == '0') # Si va equipat en armes de foc
            if at_best_shot:
                at_best_shot = at_best_shot.sorted(key=lambda s: s.shoot, reverse=True)[0].shoot # La millor arma de foc
            else:
                at_best_shot = 1

        else:
            # Calcular en base al melee
            at_best_shot = c_at.stuff.filtered(lambda s: s.type == '1') # Si va equipat en armes de melee
            if at_best_shot:
                at_best_shot = at_best_shot.sorted(key=lambda s: s.melee, reverse=True)[0].melee # La millor arma de foc
            else:
                at_best_shot = 1


        de_best_armor = c_de.stuff.filtered(lambda  s: s.type == '2') # Si te armadura
        if de_best_armor:
            de_best_armor = de_best_armor.sorted(key=lambda s: s.armor, reverse=True)[0].armor # La millor armadura
        else:
            de_best_armor = 1
        ratio_shot_armor = at_best_shot / (at_best_shot + de_best_armor) # El ratio de arma/armadur
        print("Ratio Shot/armor: "+str(ratio_shot_armor))
        ratio_at_de = ratio_at_de * ratio_shot_armor
        print("Ratio final: "+str(ratio_at_de))
        if random.random() < ratio_at_de:   # quan més ratio mes probabilitat de fer mal
            damage_de = 100*ratio_at_de  # Com que el ratio no pot ser > 1, el mal no pot ser > 100
            print('LI FA MAL')
        else:
            damage_de = 0
        print("Li fa este mal: "+str(damage_de))
        health_de = c_de.health - damage_de
        if health_de < 0:
            health_de = 0
        c_de.write({'health': health_de})


            # Calcular en base a la melee







