# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import shuffle

#########################################
#### Exemples d'operacions en recordsets
#########################################

"""
Es pot provar en la terminal amb l'opció shell del comandament odoo:

>>> s=self.env['exc2.set']
>>> s.numbers
exc2.number()
>>> self.env['exc2.number'].create({'name':1})
exc2.number(1,)
>>> self.env['exc2.number'].create({'name':2})
exc2.number(2,)
>>> self.env['exc2.number'].create({'name':3})
exc2.number(3,)
>>> self.env['exc2.number'].create({'name':4})
exc2.number(4,)
>>> self.env['exc2.number'].create({'name':-1})
exc2.number(5,)
>>> self.env['exc2.number'].create({'name':-2})
exc2.number(6,)
>>> self.env['exc2.number'].create({'name':-3})
exc2.number(7,)
>>> self.env['exc2.number'].create({'name':-4})
exc2.number(8,)
>>> self.env['exc2.number'].search([]).mapped('name')
[1.0, 2.0, 3.0, 4.0, -1.0, -2.0, -3.0, -4.0]
>>> n=self.env['exc2.number'].search([])
>>> n
exc2.number(10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
>>> s.create({'name':'conjunt'})
exc2.set(1,)
>>> s=s.search([])
>>> s
exc2.set(1,)
>>> s.write({'numbers':[(4,n.ids)]})
True
>>> s.numbers
exc2.number(10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
self.env.cr.commit()
>>> s.pairs
exc2.number(10, 12, 14, 16, 17, 19, 21)
>>> s.pairs.mapped('name')
[2.0, 2.0, 4.0, 6.0, -6.0, -4.0, -2.0]
>>> self.env['exc2.set'].search([]).mapped('numbers').mapped('name')
[2.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0]
>>> self.env['exc2.set'].search([]).mapped('pairs').mapped('name')
[2.0, 2.0, 4.0, 6.0, -6.0, -4.0, -2.0]
>>> self.env['exc2.set'].search([]).mapped('odds').mapped('name')
[1.0, 3.0, 5.0, -5.0, -3.0, -1.0]
>>> self.env['exc2.set'].search([]).mapped('positives').mapped('name')
[2.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
>>> self.env['exc2.set'].search([]).mapped('pairpositives').mapped('name')
[2.0, 2.0, 4.0, 6.0]

"""

class set(models.Model):
     _name = 'exc2.set'

     name = fields.Integer()
     numbers = fields.Many2many('exc2.number')
     pairs = fields.Many2many('exc2.number',compute='_get_pairs')
     odds = fields.Many2many('exc2.number',compute='_get_pairs')
     positives = fields.Many2many('exc2.number',compute='_get_pairs')
     negatives = fields.Many2many('exc2.number',compute='_get_pairs')
     pairpositives = fields.Many2many('exc2.number',compute='_get_pairs')
     
     @api.depends('numbers')
     def _get_pairs(self):
      for s in self:
        pairs = self.env['exc2.number']
        for n in s.numbers:
          if n.name%2 == 0:
            pairs = pairs+n 
        s.pairs = pairs
        s.odds = s.numbers - pairs
        s.positives = s.numbers.filtered(lambda r: r.name > 0)
        s.pairpositives = s.pairs & s.positives


class number(models.Model):
     _name = 'exc2.number'

     name = fields.Float()
     sets = fields.Many2many('exc2.set')


##########################################################################
######### Exemples varis del controlador  #################################
##########################################################################


class deck(models.Model):
     _name='exc2.deck'
     name=fields.Char()
     cards = fields.One2many('exc2.card','deck')
     free = fields.Many2many('exc2.card')
     hearts = fields.One2many('exc2.card',compute='_get_suit')
     spades = fields.One2many('exc2.card',compute='_get_suit')
     clovers = fields.One2many('exc2.card',compute='_get_suit')
     diamonds = fields.One2many('exc2.card',compute='_get_suit')
     black = fields.One2many('exc2.card',compute='_get_suit')
     red = fields.One2many('exc2.card',compute='_get_suit')

     @api.model
     def create(self,values):     #######----->  Exemples de sobreescriure en create i write
       new_id = super(deck, self).create(values)
       for i in [1,2,3,4,5,6,7,8,9,10,'J','Q','K']:
        for j in [['♣','C'],['♠','S'],['♥','H'],['♦','D']]:
            #print(j)
            self.env['exc2.card'].create({'name':str(i)+""+str(j[0]),'identificator':str(i)+""+str(j[1]),'deck':new_id.id})
       new_id.write({'free':[(6,0,new_id.cards.ids)]})
       return new_id

     @api.multi
     def _get_suit(self):
      for i in self:
       i.hearts = self.env['exc2.card'].search([('deck','=',i.id),('identificator','like','H')]) ## Amb search
       i.spades = i.cards.filtered(lambda r: 'S' in r.identificator)   ## Amb filtered
       i.clovers = self.env['exc2.card'].search([('deck','=',i.id),('identificator','like','C')]) ## Amb search
       i.diamonds = self.env['exc2.card'].search([('deck','=',i.id),('identificator','like','D')]) ## Amb search
       black = (i.hearts+i.diamonds).ids
       print(black)
       i.black = self.env['exc2.card'].browse(black)   ## Exemple de browse
       i.red = i.spades + i.clovers     ## Exemple de suma de recordsets

     def create_hand(self):
      for d in self:
       free = d.free.ids
       shuffle(free)
       h=self.env['exc2.hand'].create({'name':'h','cards': [(6,0,[free[0],free[1],free[2],free[3],free[4]])]})
       d.write({'free':[(6,0,(d.free - h.cards).ids)]})  ## Exemple de sobre escriure en un many2many
       print(d.free)

class card(models.Model):
     _name='exc2.card'
     name=fields.Char()
     identificator=fields.Char()
     deck = fields.Many2one('exc2.deck')

class hand(models.Model):
     _name='exc2.hand'
     name=fields.Char()
     cards=fields.Many2many('exc2.card')

"""
Exemple d'ús en la terminal

>>> self.env['exc2.deck'].create({'name':'d2'})
>>> 
>>> 
>>> self.env['exc2.deck'].search([])
exc2.deck(2, 3)
>>> self.env['exc2.deck'].search([('name','=','d2')])
exc2.deck(3,)
>>> self.env['exc2.deck'].search([('name','=','d2')]).cards
exc2.card(49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96)
>>> self.env['exc2.deck'].search([('name','=','d2')]).hearts
exc2.card(51, 55, 59, 63, 67, 71, 75, 79, 83, 87, 91, 95)
>>> self.env['exc2.deck'].search([('name','=','d2')]).spades
exc2.card(50, 54, 58, 62, 66, 70, 74, 78, 82, 86, 90, 94)
>>> self.env['exc2.deck'].search([('name','=','d2')]).spades.mapped('name')
[u'1\u2660', u'2\u2660', u'3\u2660', u'4\u2660', u'5\u2660', u'6\u2660', u'7\u2660', u'8\u2660', u'9\u2660', u'J\u2660', u'Q\u2660', u'K\u2660']
>>> self.env['exc2.deck'].search([('name','=','d2')]).spades.mapped('identificator')
[u'1S', u'2S', u'3S', u'4S', u'5S', u'6S', u'7S', u'8S', u'9S', u'JS', u'QS', u'KS']
>>> self.env['exc2.deck'].search([('name','=','d2')]).clovers.mapped('identificator')
[u'1C', u'2C', u'3C', u'4C', u'5C', u'6C', u'7C', u'8C', u'9C', u'JC', u'QC', u'KC']
>>> self.env['exc2.deck'].search([('name','=','d2')]).diamonds.mapped('identificator')
[u'1D', u'2D', u'3D', u'4D', u'5D', u'6D', u'7D', u'8D', u'9D', u'JD', u'QD', u'KD']
>>> d.create_hand()
exc2.card(481, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 508, 509, 510, 511, 512, 513, 514, 515, 516, 518, 520, 521, 522, 523, 524, 526, 527, 528)
>>> d.create_hand()
exc2.card(481, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 494, 495, 496, 497, 499, 501, 502, 503, 504, 505, 506, 508, 509, 510, 511, 512, 514, 515, 516, 518, 520, 521, 522, 523, 524, 527, 528)
>>> d.create_hand()
exc2.card(483, 484, 485, 486, 487, 489, 490, 491, 492, 494, 496, 497, 499, 501, 502, 504, 505, 506, 508, 509, 510, 512, 514, 515, 516, 518, 520, 521, 522, 523, 524, 527, 528)
>>> 


"""


##########################################################################
############# Exemples de crear models ##################################
###########################################################################

class rorder(models.Model):
    _name = 'exc2.rorder'

    name = fields.Char()
    products = fields.Many2many('product.product',compute='_get_products')

    @api.multi
    def _get_products(self):
      for r in self:
       tots = self.env['product.product'].search([]).ids
       shuffle(tots)
       r.products = self.env['product.product'].browse(tots[0:10]) # browse

    def create_order(self):
      client = self.env['res.partner'].search([])[0]
      for r in self:
        order=self.env['sale.order'].create({'partner_id':client.id}) #create
        print(order.name)
        for p in r.products:
          l=self.env['sale.order.line'].create({'order_id':order.id,'product_id':p.id}) #create
          print(l)


##############################################################################################
##################### Exemples de programació funcional #############################
########################################################################################

class round(models.Model):
    _name = 'exc2.round'
    name = fields.Datetime(default=lambda self: fields.Date.today())
    cardboards = fields.Many2many('exc2.cardboard')
    balls = fields.Many2many('exc2.ball')
    winner = fields.Many2one('exc2.cardboard')
    
    def new_number(self):
     for round in self:
       if round.winner != False:
        remaining = (self.env['exc2.ball'].search([]) - round.balls).ids
        shuffle(remaining)
        round.write({'balls':[(4,remaining[0])]})
        


class cardboard(models.Model):
    _name = 'exc2.cardboard'
    name = fields.Char()
    numbers = fields.Many2many('exc2.ball')

class ball(models.Model):
    _name = 'exc2.ball'
    name = fields.Integer()

    def start(self):
     for i in range(1,100):
       print(i)
       self.create({'name':i})


