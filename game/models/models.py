# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import random
import math
import json


class player(models.Model):
     _name = 'game.player'
     name = fields.Char()
     image = fields.Binary()
     fortresses = fields.One2many('game.fortress','player')
     fortressesk = fields.One2many(related='fortresses') # Per al kanban
     resources = fields.Many2many('game.resource', compute='_get_resources')
     raws = fields.One2many('game.raws','player')
     characters = fields.Many2many('game.character', compute='_get_resources')

     weapons_points = fields.Integer()  #Els punts a repartir en cada arma
     stuff_points = fields.Integer()  # Els punts a repartir en cada stuff
     gold = fields.Float(default=100.0)
     max_fortresses = fields.Integer(default=1)

     clan = fields.Many2one('game.clan')

     @api.depends('fortresses')
     def _get_resources(self):
         for player in self:

             player.resources = player.fortresses.mapped('resources')
             player.characters = player.fortresses.mapped('characters')


     @api.multi
     def reset_player(self):
         for p in self:
             p.weapons_points = 0
             p.stuff_points = 0
             for i in p.fortresses:
                 for c in i.resources:
                     c.unlink()
                 i.unlink()
             f_template = self.env.ref('game.fortress1')
             names = ["Ardglass","Abingdon","Swindlincote","Rotherham","Far Water","Todmorden","Walden","Lanercoast","Aempleforth","Barkamsted","Swindmore","Mountmend","Dalmellington","Blencogo","Beggar's Hole","Faversham","Lindow","Dungannon","Doveport","Peterbrugh","Limesvilles","Grimsby","Thralkeld","Dawsbury","Rotherhithe","Pavv","Holmfirth","Dalmellington","Eastcliff","Bleakburn"]
             f = self.env['game.fortress'].create({
                 'name': str(random.choice(names)),
                 'image': f_template.image,
                 'template': False,
                 'level': 1,
                 'player': p.id
             })
             c_template = self.env.ref('game.cantera')
             c = self.env['game.resource'].create({
                 'name':'Cantera of: '+str(p.name),
                 'image': c_template.image,
                 'template': False,
                 'level' : 1,
                 'fortress': f.id,
                 'parent': c_template.id,
                 'knowledge': c_template.knowledge
             })
             c_template = self.env.ref('game.barn')
             c = self.env['game.resource'].create({
                 'name': 'Barn of:'+str(p.name),
                 'image': c_template.image,
                 'template': False,
                 'level': 1,
                 'fortress': f.id,
                 'parent': c_template.id,
                 'knowledge': c_template.knowledge
             })
             c_template = self.env.ref('game.kitchen')
             c = self.env['game.resource'].create({
                 'name': 'Kitchen of: '+str(p.name),
                 'image': c_template.image,
                 'template': False,
                 'level': 1,
                 'fortress': f.id,
                 'parent': c_template.id,
                 'knowledge': c_template.knowledge
             })
             for i in p.raws:
                 i.unlink()
             r = self.env['game.raws'].create({
                 'name': 'Stones',
                 'player': p.id,
                 'raw': self.env.ref('game.piedra').id,
                 'quantity': 100
             })
             r = self.env['game.raws'].create({
                 'name': 'Iron',
                 'player': p.id,
                 'raw': self.env.ref('game.hierro').id,
                 'quantity': 10
             })
             r = self.env['game.raws'].create({
                 'name': 'Food',
                 'player': p.id,
                 'raw': self.env.ref('game.food').id,
                 'quantity': 10
             })

    # @api.model
     def update_resources(self):
         print('\033[95m'+'Updating resources')
         resources = self.env['game.resource'].search([('template', '=', False)]) # Busca els recursos que no son template
         for r in resources.filtered(lambda r: r.inactive == False ):
             if r.minutes_left > 0:
                 r.minutes_left = r.minutes_left - 1
             else:
                 productions = r.current_productions
                 c_productions = json.loads(r.characters_productions)
                 # print(c_productions)
                 #productions = self.env['game.production'].search([('resource','=',r.parent.id),('level','=',r.level)])
                 for p in productions:  # La llista de les produccions d'aquest recurs
                     raws = r.fortress.player.raws.filtered(lambda r: r.raw.id == p.raw.id)  # El raws del player que es d'aquesta produccio
                     if len(raws) == 0:
                         raws = self.env['game.raws'].create({'name': p.raw.name,'player':r.fortress.player.id,'raw':p.raw.id,'quantity':0})
                     for i in raws:
                         q = i.quantity + p.production
                         # ara cal calcular la produccio dels characters:
                         characters_increment = c_productions[str(i.raw.id)]
                         q = q + characters_increment
                         #print(str(i.name)+" "+str(q))
                         i.write({'quantity': q})

                 # Les investigacions

                 for research in r.researches.filtered(lambda s: s.minutes_left > 0):
                     research.write({'minutes_left': research.minutes_left - 1})
                     print('Updating researches')
                     research.do_research()


         print('Updating characters')
         characters = self.env['game.character'].search([('health','>',0)])
         for c in characters:
             age = c.age + 1
             health = c.health
             # a partir de 100 anys, quasi segur que moren
             # 100 anys son 36500 dies, cada dia un minut de joc
             # un caracter dura com a molt 25 dies de joc
             # Funcio doble exponencial per a que dure menys de 25 dies
             p_mort=(1.00000000000001**(age**3.2)-1)/100
             # print(p_mort)
             if random.random() < p_mort:
                 health = 0
                 print('MORT!'+str(c.name))
             elif health < 100:
                 health = health + 1
             c.write({'health': health,'age':age})
             if c.resource:
               if not c.resource.inactive:
                 level = c.resource.level
                 k = c.resource.knowledge
                 if k == '1':   # Barracks
                     war = c.war + level
                     c.write({'war': war})
                 elif k == '2':  # Laboratory
                     science = c.science + level
                     c.write({'science': science})
                 elif k == '3': # Mining
                     mining = c.mining + level
                     c.write({'mining': mining})
                 elif k == '4':
                     construction = c.construction + level
                     c.write({'construction': construction})
                 elif k == '5':
                     construction = c.construction + level
                     mining = c.mining + level
                     c.write({'construction': construction,'mining': mining})


         fortresses = self.env['game.fortress'].search([])
         for f in fortresses:
             n_characters = len(f.characters)
             if n_characters > 1: # Al menys necessitem una parelleta
                 probability = n_characters/10000 # Amb 100 caracters, hi ha un 1% de probabilitat de naixer uno nou
                 #print(probability)
                 if probability > random.random():
                     c_template = self.env.ref('game.character_template' + str(random.randint(1, 2)))
                     c_template2 = self.env.ref('game.character_template' + str(random.randint(1, 12)))
                     c = self.env['game.character'].create({
                         'name': c_template2.name,
                         'image': c_template.image,
                         'fortress': f.id,
                         'science': random.randint(1, 20),
                         'construction': random.randint(1, 20),
                         'mining': random.randint(1, 20),
                         'war': random.randint(1, 20),
                         'health': random.randint(1, 20)
                     })
                     print('Growing population '+probability+" "+str(c))


         print('Updating stuff')
         stuff = self.env['game.stuff'].search([('minutes_left','>',0)])
         for s in stuff:
             s.write({'minutes_left': s.minutes_left - 1})

         print(' \033[0m')

     @api.multi
     def create_new_fortress(self):
       for p in self:
         if p.max_fortresses > len(p.fortresses):
             f_template = self.env.ref('game.fortress1')
             f = self.env['game.fortress'].create({
                 'name': 'Choose the name of your fortress',
                 'image': f_template.image,
                 'template': False,
                 'level': 1,
                 'player': p.id
             })
             c_template = self.env.ref('game.cantera')
             c = self.env['game.resource'].create({
                 'name': 'Cantera',
                 'image': c_template.image,
                 'template': False,
                 'level': 1,
                 'fortress': f.id,
                 'parent': c_template.id
             })

class fortress(models.Model):
    _name = 'game.fortress'
    name = fields.Char()
    player = fields.Many2one('game.player')
    image = fields.Binary()
    image_small = fields.Binary(string='Image',compute='_get_images', store=True)
    template = fields.Boolean()
    resources = fields.One2many('game.resource','fortress')
    available_resources = fields.Many2many('game.resource', compute='_get_available_resources')
    characters = fields.One2many('game.character','fortress')
    max_resources = fields.Integer(default=10)

    @api.depends('image')
    def _get_images(self):
        for i in self:
          image = i.image
          data = tools.image_get_resized_images(image)
          i.image_small = data["image_small"]

    @api.multi
    def create_new_character(self):
        for p in self:
            c_template = self.env.ref('game.character_template'+str(random.randint(1,2)))
            c_template2 = self.env.ref('game.character_template'+str(random.randint(1,12)))
            c = self.env['game.character'].create({
                'name': c_template2.name,
                'image': c_template.image,
                'fortress': p.id,
                'science': random.randint(1,20),
                'construction': random.randint(1,20),
                'mining': random.randint(1,20),
                'war': random.randint(1,20),
                'health': random.randint(1,20)
            })

    @api.multi
    def _get_available_resources(self):
        for f in self:
            print('aaa')
            r = self.env['game.resource'].search([('template','=',True)])
            f.available_resources = [(6,0,r.ids)]

class resource(models.Model):
    _name = 'game.resource'
    name = fields.Char()
    productions = fields.One2many('game.production','resource') # Llista de coses que produeix
                                                                # o consumeix
    costs = fields.One2many('game.cost','resource')
    durations = fields.One2many('game.duration', 'resource')
    productions_child = fields.One2many(related='parent.productions')
    costs_child = fields.One2many(related='parent.costs')
    durations_child = fields.One2many(related='parent.durations')
    image = fields.Binary()
    image_small = fields.Binary(compute='_get_images', store=True)
    fortress = fields.Many2one('game.fortress')
    level = fields.Integer()
    template = fields.Boolean()
    parent = fields.Many2one('game.resource', domain="[('template', '=', True)]")
    minutes_left = fields.Integer()
    const_percent = fields.Float(compute='_get_const_percent') # sera computed el % de contruccio
    # En cas de ser barracks o academy o laboratory
    knowledge = fields.Selection([('0','None'),('1','Militar'),('2','Scientific'),('3','Mining'),('4','Construction'),('5','All Skills')])
    characters = fields.One2many('game.character','resource')
    researches = fields.One2many('game.research','resource')
    inactive = fields.Boolean(compute='_get_inactive')
    current_productions = fields.Many2many('game.production', compute='_get_productions')
    current_productionsk = fields.Char(compute='_get_productions')
    characters_productions = fields.Char(compute='_get_productions')


    color = fields.Integer(compute='_get_color')

    @api.multi
    def _get_color(self):
        for i in self:
            if i.template:
                i.color = 4
            else:
                i.color = 3
            if i.inactive:
                i.color = 1

    @api.depends('image')
    def _get_images(self):
        for i in self:
          image = i.image
          data = tools.image_get_resized_images(image)
          i.image_small = data["image_small"]

    @api.depends('minutes_left')
    def _get_const_percent(self):
        for r in self:
            total_time = r.durations_child.filtered(lambda s: s.level == r.level).minutes
            if total_time > 0:
                r.const_percent = 100- (r.minutes_left / total_time)*100

    @api.multi
    def build_it(self):
        for r in self:
            fortress = self.env['game.fortress'].browse(self.env.context['fortress'])
            if fortress.max_resources > len(fortress.resources):
                 r.create({'name': r.name, 'image': r.image, 'fortress': self.env.context['fortress'],
                      'level': 1, 'template': False, 'parent': r.id,
                      'minutes_left': r.durations.filtered(lambda s: s.level == 1).minutes,
                      'knowledge': r.knowledge
                      })

    @api.multi
    def _get_inactive(self):
        for r in self:
            inactive = False
            productions_negative = r.productions_child.filtered(lambda p: p.production <= 0 and p.level == r.level)
            for i in productions_negative:
                quantity = r.fortress.player.raws.filtered(lambda  p: p.raw.id == i.raw.id).quantity
                if quantity < -i.production:
                    inactive = True
            r.inactive = inactive

    @api.multi
    def _get_productions(self):
        for r in self:
            r.current_productions = r.productions_child.filtered(lambda p: p.level == r.level) # Les produccions del propi edifici
            characters_productions = {} # Les produccions dels characters
            for p in r.current_productions:
                if r.characters and p.production > 0:  # Sols augmenten els caracters la produccio si es positiva
                    characters_p = sum(cc.mining for cc in r.characters)  # suma de les qualitats de minig de cada caracter
                    characters_increment = math.log(characters_p, 1.1)  # Augment logaritmic
                    characters_productions[p.raw.id] = characters_increment
                else:
                    characters_productions[p.raw.id] = 0

            r.current_productionsk = r.current_productions.mapped(lambda p: str(p.raw.name)+" : "+str(p.production))
            r.characters_productions = json.dumps(characters_productions)
            #print(str(r.name)+" "+str(r.current_productions.mapped('production'))+" "+str(characters_productions))



    @api.multi
    def level_up(self):
        for r in self:
            level = r.level + 1
            minutes_left = r.durations_child.filtered(lambda d: d.level == level)
            if minutes_left:
              minutes_left = minutes_left[0].minutes
              r.write({'level': level, 'minutes_left': minutes_left})

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

class duration(models.Model):
    _name = 'game.duration'
    name = fields.Char()
    resource = fields.Many2one('game.resource') # Que recurs
    level = fields.Integer() # Cal indicar el que tarda en cada nivell
    minutes = fields.Integer()  #cost total
    max_characters = fields.Integer()

class raw(models.Model):
    _name = 'game.raw'
    name = fields.Char()
    image = fields.Binary()
    public_hash = fields.Char(readonly=True)
    hidden_hash = fields.Char(readonly=True) # El hash és com la composició atòmica, que no es sap inicialment.
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
    production = fields.Float(compute='get_production')
    spending = fields.Float(compute='get_production')
    total_production = fields.Float(compute='get_production')
    character_production = fields.Float(compute='get_production')

    @api.multi
    def get_production(self):
        for raws in self:
            resources = raws.player.fortresses.mapped('resources').filtered(lambda r: r.minutes_left == 0)
            productions = self.env['game.production']
            for r in resources:
                productions = productions + r.mapped('current_productions').filtered(lambda p: p.raw.id == raws.raw.id)
            print(str(productions) +' '+ str(raws.raw.id))
            productions_positive = sum(productions.filtered(lambda p: p.production > 0).mapped('production'))
            productions_negative = sum(productions.filtered(lambda p: p.production <= 0).mapped('production'))
            # Calcul de les produccions de caracters
            c_production = 0
            #resources = raws.player.fortresses.mapped('resources')
            for r in resources:
                c_productions = json.loads(r.characters_productions)
                if str(raws.raw.id) in c_productions:
                    c_production = c_production + c_productions[str(raws.raw.id)]

            raws.production = productions_positive
            raws.spending = productions_negative
            raws.character_production = c_production
            raws.total_production = productions_positive + productions_negative + raws.character_production

# Un recurs és, per exemple, una mina, que consumeix electricitat i produeix varis materials a un ritme distint
# Cada recurs té una llista de production que indica qué i quant produeix o consumeix.
# Els materials inicials tenen unes propietats basiques, hi ha milers de materials primaris per descobrir i
# amés es poden mesclar entre ells per tindre altres propietats.
# Un jugador pot descobrir un material i publicar el seu hash o no. Pot anar provant hashes (tarda un temps) o
# invertir en educacio i investigacio i ser mes probable que el trobe.
# La gracia esta en que els jugadors creen una base de dades del que van descobrint i que siga o no pública.

class character(models.Model):
    _name = 'game.character'
    name = fields.Char()
    image = fields.Binary()
    fortress = fields.Many2one('game.fortress')
    science = fields.Float()
    construction = fields.Float()
    mining = fields.Float()
    war = fields.Float()
    health = fields.Float()
    age = fields.Integer(default=1)
    resource = fields.Many2one('game.resource') # Falta que no puga ser d'un altre fortress
    stuff = fields.One2many('game.stuff','character')

class character_template(models.Model):
    _name = 'game.character.template'
    image = fields.Binary()
    name = fields.Char()

### Les investigacions

class research(models.Model):
    _name = 'game.research'
    name = fields.Char()
    resource = fields.Many2one('game.resource')
    type = fields.Selection([('1','Weapons'),('2','Chemist'),('3','Nutrition'),('4','Medicine'),('5','Energy')])
    minutes_left = fields.Integer()
    research_percent = fields.Float() # sera computed el % de investigació
    result = fields.Char()

    @api.multi
    def do_research(self):
        for r in self.filtered(lambda s: s.minutes_left == 1):
            if r.type == '1':
                print('millora en armes')
                character_skills = sum(r.resource.characters.mapped('science'))
                weapons_points = r.resource.fortress.player.weapons_points
                ratio_skills_points = math.ceil(character_skills/(weapons_points+1))+1
                points_extra = random.randint(0,ratio_skills_points)
                r.resource.fortress.player.write({'weapons_points': weapons_points + points_extra})
                r.write({'result': str(points_extra)+' Points extra in Weapon Points \n Ratio Skills/Weapon points: '+str(ratio_skills_points)})
            if r.type == '2':
                print('millora en química')
                character_skills = sum(r.resource.characters.mapped('science'))
                n_raws = len(r.resource.fortress.player.raws)
                ratio_skills_n_raws = math.ceil(character_skills/(n_raws+1))+1
                # print(ratio_skills_n_raws)
                chance = random.randint(0, ratio_skills_n_raws)
                # print(str(n_raws)+' '+str(chance))
                if chance >= random.randint(0,1):
                   not_discovered = self.env['game.raw'].search([]) - r.resource.fortress.player.raws.mapped('raw')
                   not_discovered = not_discovered.ids
                   random.shuffle(not_discovered)
                   # print(not_discovered)
                   new_raw = not_discovered[0]
                   self.env['game.raws'].create({'player': r.resource.fortress.player.id, 'raw': new_raw})
                   r.write({'result': 'Discovered new Raw material: '+str(self.env['game.raw'].search([('id','=',new_raw)]).name)})
                   print('Discovered: '+ str(new_raw))
            if r.type == '3':
                print('millora en nutricio')
            if r.type == '4':
                print('millora en medicina')
            if r.type == '5':
                print('millora en energia')


### Els accessoris

## Cal crear un wizard per a crear stuff.

class stuff(models.Model):
    _name = 'game.stuff'
    name = fields.Char(readonly=True)
    hash = fields.Char(readonly=True)
    image = fields.Binary(readonly=True)
    character = fields.Many2one('game.character')
    player = fields.Many2one('game.player')
    type = fields.Selection([('0','Fire Weapons'),('1','Melee Weapons'),('2','Armor'),
                             ('3','Chemist'),('4','Nutrition'),('5','Medicine'),('6','Energy')])
    # Propietats:
    melee = fields.Integer()
    shoot = fields.Integer()
    armor = fields.Integer()

    science = fields.Integer()
    cook = fields.Integer()
    medicine = fields.Integer()
    energy = fields.Integer()

    minutes_left = fields.Integer()
    duration = fields.Integer()

    @api.multi
    def generate_name(self):
        for s in self:
         words = {'1': ["Sword","Knive","Dagger","Axe","Sickle","Kama","Halberd","Spear","Guandao",
                 "scythe","Mace","Stick","Nunchaku"],
                 '0': ["Gun","Shotgun","Rifle","Carbine","Machine Gun","Sniper rifle","Musket"],
                 '2': ["Armor", "Uniform", "Camouflaje armor", "Bulletproof vest"],
                 '3': ["Microscope", "Tube", "Pipette", "Balance", "Beaker", "Crucible"],
                 '4': ["Knive","Balance","Stove","Oven","Pan","Pot"],
                 '5': ["Thermometer", "Cannula", "Enema", "Scissors", "Stethoscope", "Bandage"],
                 '6': ["Cables", "Voltimeter", "Generator", "Solar Panel", "Boiler", "Engine"]}

         adjectives = ["Premium","Obsolete","Glorious","False","Astonishing",
                          "Splendid", "Pathetic", "Bizarre", "Sordid", "Studendous", "Sharp",
                          "Overconfident", "Pleasant", "Sweet", "Last", "Curly", "Freezing", "Aberrant",
                          "Profuse", "Dangerous", "Powerful"]

         word = words[s.type]
         random.shuffle(word)
         word = word[0]
         random.shuffle(adjectives)
         adjective = adjectives[0]
         image = self.env.ref('game.stuff_template'+str(s.type)).image
         s.write({'name': adjective+" "+word,'image':image})

    @api.onchange('character')
    def _onchange_character(self):
        self.player = self.character.fortress.player.id


class stuff_images(models.Model):
    _name = 'game.stuff.image'
    type = fields.Selection([('0','Fire Weapons'),('1','Melee Weapons'),('2','Armor'),
                             ('3','Chemist'),('4','Nutrition'),('5','Medicine'),('6','Energy')])
    image = fields.Binary()