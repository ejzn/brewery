# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class brewery_ingredient(osv.osv):
    _name = "brewery.ingredient"
    _description = "Beer Recipe Ingredients"
    _columns = {
           'name': fields.char('Name', size=64),
           'ingredient_id' : fields.many2one('brewery.recipe', 'Recipe', select=True),
           'product_id' : fields.many2one('product.product', 'Product', required=True,  domain=[('purchase_ok', '=', 1)], select=True),
           'quantity' : fields.integer('Quantity', required=True),
    }

brewery_ingredient()

class brewery_tank(osv.osv):
    _name = "brewery.tank"
    _description = "Beer Tanks"

    def _current_volume(self, cursor, user, ids, name, args, context=None):
        res = {}

        for tank in self.browse(cursor, user, ids, context=context):
            if tank.id:
                res[tank.id] = 0

                batch_ids  = self.pool.get('brewery.batch').search(cursor, user, [('tank_id', '=', tank.id),('state', '=', 'active')])
                if len(batch_ids) > 0:
                    batch_id = batch_ids[0]
                    batch = self.pool.get('brewery.batch').browse(cursor, user, batch_id, context=None)
                    if batch:
                        res[tank.id] = batch.tank_volume
        return res

    def _current_batch(self, cursor, user, ids, name, args, context=None):
        res = {}

        for tank in self.browse(cursor, user, ids, context=context):
            if tank.id:
                res[tank.id] = 0
                batch_id = self.pool.get('brewery.batch').search(cursor, user, [('tank_id', '=', tank.id), ('state', '=', 'active')])
                if batch_id and len(batch_id) > 0:
                    batch = self.pool.get('brewery.batch').browse(cursor, user, batch_id[0])
                    res[tank.id] = ' #' + str(batch.id) + ' ' + batch.name
        return res


    _columns = {
            'name' : fields.char('Name', size=64, required=True),
            'capacity' : fields.float('Capacity', required=True),
            'current_volume' : fields.function(_current_volume, type="float"),
            'current_batch' : fields.function(_current_batch, type='char'),
    }

brewery_tank()

class brewery_bottling_run(osv.osv):
    _name = "brewery.bottling.run"
    _description = "Beer Bottling Run"

    # Check available volume
    def action_confirm(self, cursor, user, ids, context=None):
        print "Confirming"
        self.write(cursor, user, ids, {'state': 'confirmed'})

    # Pull volume form the batch based on the amoutn bottled
    # place them into inventory
    def action_bottle(self, cursor, user, ids, context=None):

        for run in self.browse(cursor, user, ids, context=context):

            #if not run.caps:
            #    raise osv.except_osv(_('Error!'), _('Wow there Cowboy/Cowgirl you can\'t bottle without caps can you?'))
            #    return

            #if not run.labels:
            #    raise osv.except_osv(_('Error!'), _('Wow there Cowboy/Cowgirl you can\'t bottle without labels can you?'))
            #    return


            inventory = {
                'state' : 'draft',
                'name' : 'Inventory'
            }

            stock_inventory = self.pool.get('stock.inventory').create(cursor, user, inventory, context=None)
            inventory_bottles_out = {}

            prod_ids = self.pool.get('product.product').search(cursor, user, [('sale_ok', '=', 0)])
            bottles_found = False

            for prod in self.pool.get('product.product').browse(cursor, user, prod_ids):
                if prod.categ_id.name == 'Bottles' and prod.volume == run.unit_size and prod.qty_available >= run.units:
                    print prod.volume
                    print prod.categ_id.name
                    inventory_bottles_out  = {
                        'product_id' : prod.id,
                        'inventory_id' : stock_inventory,
                        'product_qty' :  prod.qty_available - run.units,
                        'location_id' : 12,
                        'product_uom' : run.product_id.uom_id.id,
                    }
                    stock_line = self.pool.get('stock.inventory.line').create(cursor, user, inventory_bottles_out, context=None)

                    bottles_found = True
                    print "Bottles out:" + str(inventory_bottles_out['product_qty'])

            if not bottles_found:
                raise osv.except_osv(_('Error!'), _('Not enough bottles or no units of ' + str(run.unit_size) + ' found'))
                return

            # Error checking on caps
            if run.caps.qty_available >= run.units:
                inventory_caps_out = {
                    'product_id' : run.caps.id,
                    'inventory_id' : stock_inventory,
                    'product_qty' : run.caps.qty_available - run.units,
                    'location_id' : 12,
                    'product_uom' : run.product_id.uom_id.id,
                }
                stock_line = self.pool.get('stock.inventory.line').create(cursor, user, inventory_caps_out, context=None)



            # Error checking on labels
            if run.labels.qty_available >= run.units:
                inventory_labels_out = {
                    'product_id' : run.labels.id,
                    'inventory_id' : stock_inventory,
                    'product_qty' : run.labels.qty_available - run.units,
                    'location_id' : 12,
                    'product_uom' : run.product_id.uom_id.id,
                }
                stock_line = self.pool.get('stock.inventory.line').create(cursor, user, inventory_labels_out, context=None)



            inventory_bottles_in  = {
                'product_id' : run.product_id.id,
                'inventory_id' : stock_inventory,
                'product_qty' : run.units + run.product_id.qty_available,
                'location_id' : 12,
                'product_uom' : run.product_id.uom_id.id,
            }

            print "Bottles In: " + str(inventory_bottles_in['product_qty'])

            stock_line = self.pool.get('stock.inventory.line').create(cursor, user, inventory_bottles_in, context=None)

            for inv in self.pool.get('stock.inventory').browse(cursor, user, [stock_inventory], context=None):
                inv.action_confirm()
                for move in inv.move_ids:
                   # TODO: Fix this line
                    move.force_assign()
                    move.action_confirm()
                    move.action_done()
                inv.action_done()

            if run.batch_id and run.unit_size and run.units:
                if run.volume_available < (run.unit_size * run.units):
                    print "Return an ERROR trying to bottle more than available inventory"
                else:
                    vol = run.batch_id.packaged_volume + (run.unit_size * run.units)
                    print "Removed added volume: " + str(run.unit_size * run.units)
                    run.batch_id.write({'packaged_volume': vol })



        self.write(cursor, user, ids, {'state': 'bottled'})

    def _unit_size(self, cursor, user, ids, name, args, context=None):
        res = {}
        for run in self.browse(cursor, user, ids, context=context):
            res[run.id] = 0
            if run.product_id:
                res[run.id] = run.product_id.volume or 0
        return res

    def _volume_available(self, cursor, user, ids, name, args, context=None):
        res = {}
        for run in self.browse(cursor, user, ids, context=context):
            res[run.id] = 0
            if run.batch_id:
                res[run.id] = run.batch_id.tank_volume or 0
        return res

    _columns = {
           'batch_id' : fields.many2one('brewery.batch', 'Batch', required=True, domain=[('state','=','active')]),
           'date': fields.date('Date Bottled', states={'draft': [('readonly', True)]}, required=True, change_default=True, select=True, track_visibility='always'),
           'product_id' : fields.many2one('product.product', 'Product', required=True,  domain=[('sale_ok', '=', 1)], select=True),
           'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('bottled', 'Bottled'),
            ], 'Status', readonly=True, track_visibility='onchange', help="State of the bottling run", required=True),
           'volume_available' : fields.function(_volume_available),
           'unit_size' : fields.function(_unit_size),
           'units' : fields.integer('Units', states={'draft': [('readonly', True)]}, required=True, change_default=True, select=True, track_visibility='always'),
           'labels' : fields.many2one('product.product', 'Label', states={'draft': [('readonly', True)]}, domain=[('sale_ok', '=', 0)], select=True, track_visiblity='always'),
           'caps' : fields.many2one('product.product', 'Cap', states={'draft': [('readonly', True)]}, domain=[('sale_ok', '=', 0)], select=True, track_visiblity='always'),
    }
    _defaults = {
        'state' : 'draft',
        'volume_available' : 0,
        'units' : 0,
        'date' : fields.date.context_today,
    }
brewery_bottling_run()

class brewery_recipe(osv.osv):
    _name = "brewery.recipe"
    _description = "Beer Recipe"
    _columns = {
           'name' : fields.char('Recipe Name',size=64, required=True),
           'yield' : fields.float('Yield', required=True),
           'ingredients' : fields.one2many('brewery.ingredient', 'ingredient_id','Ingredients', required=True, select=True),
    }

brewery_recipe()

class brewery_batch(osv.osv):
    _name = "brewery.batch"
    _description = "Beer Batches"

    def action_activate(self, cursor, user, ids, context=None):
        for batch in self.browse(cursor, user, ids, context=context):
            for batch_ids in self.search(cursor, user, [('state', '=', 'active')]):
                for match in self.browse(cursor, user, [batch_ids]):
                    if match.tank_id.id == batch.tank_id.id:
                        print 'Wowzers we cant enable another one!'
                        raise osv.except_osv(_('Error!'), _('You can\'t activate a batch in a tank with another active batch. You have to either finish or commit to waste the other batch first.'))
                        return

            inventory = {
                            'state' : 'draft',
                            'name' : 'Inventory'
                        }

            inventory_run_out = self.pool.get('stock.inventory').create(cursor, user, inventory, context=None)
            for ingredient in batch.recipe_id.ingredients:

                if (ingredient.product_id.qty_available - ingredient.quantity) < 0:
                    raise osv.except_osv(_('Error!'), _('Not enough of ingredient ' + ingredient.product_id.name + ' found'))
                    return

                inventory_out  = {
                        'product_id' : ingredient.product_id.id,
                        'inventory_id' : inventory_run_out,
                        'product_qty' :  ingredient.product_id.qty_available - ingredient.quantity,
                        'location_id' : 12,
                        'product_uom' : ingredient.product_id.uom_id.id,
                }
                stock_line = self.pool.get('stock.inventory.line').create(cursor, user, inventory_out, context=None)

            for inv in self.pool.get('stock.inventory').browse(cursor, user, [inventory_run_out], context=None):
                inv.action_confirm()
                for move in inv.move_ids:
                    move.force_assign()
                    move.action_confirm()
                    move.action_done()
                inv.action_done()

        self.write(cursor, user, ids, {'state': 'active'})

    def action_finish(self, cursor, user, ids, context=None):
        for batch in self.browse(cursor, user, ids, context=context):
            if (batch.recipe_id['yield'] - (batch.waste + batch.packaged_volume)) > 0:
                raise osv.except_osv(_('Error!'), _('Please commit the volume to waste, or bottle it before finishing this batch for future tracking'))
            else:
                self.write(cursor, user, ids, {'state': 'finished'})


    def _tank_volume(self, cursor, user, ids, name, args, context=None):
        res = {}
        for batch in self.browse(cursor, user, ids, context=context):
            packaged = batch.packaged_volume or 0
            waste = batch.waste or 0
            res[batch.id] = 0
            if batch.recipe_id:
                res[batch.id] = batch.recipe_id['yield'] - packaged - waste
        return res

    _columns = {
           'name':fields.char('Batch Name',size=64, required=True),
           'brew_date': fields.date('Brew Date', required=True),
           'tank_id': fields.many2one('brewery.tank', 'Tank', required=True),
           'state': fields.selection([
           ('prepping', 'Prepping'),
           ('active', 'Active'),
           ('finished', 'Finished')], readonly=True),
           'waste': fields.float('Waste Volume', required=True),
           'tank_volume': fields.function(_tank_volume, 'Tank Volume'),
           'packaged_volume': fields.float('Packaged Volume', readonly=True, required=True),
           'recipe_id' : fields.many2one('brewery.recipe', 'Recipe', required=True),
           'run_id' : fields.one2many('brewery.bottling.run', 'batch_id', 'Bottling Runs', readonly=True),
    }

    _defaults = {
        'state' : 'prepping',
        'packaged_volume' : 0.0
    }

brewery_batch()

 #vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
