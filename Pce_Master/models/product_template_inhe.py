from odoo import api,fields,models, _
from odoo.exceptions import UserError,ValidationError

class product_template_inhe(models.Model):
    _inherit='product.template'
    _sql_constraints=[('Unique Product Name','unique(unique_product)','Please Enter Unique Product Name.')]

    #updated-By:Pradip|Updated-Date-12-3-2019|Info.Fileds Added into Chatter box
    
    drawing_number =fields.Char('Drawing Number.',track_visibility='onchange',help='Drawing Number')
    revision_number =fields.Integer('Revision Number',default=0,track_visibility='onchange',help='Revision Number')
    
    text_master_id=fields.Many2one('text_master.info',string='Text',required=True)
    effect_code_description=fields.Many2one('effect_master.info',string='Effect Code Descrip.',required=True)      
    id_code_description=fields.Many2one('id_code_master.info',string="Id Code Descrip.",required=True)
    manufacturer=fields.Many2one('make_master.info',string='Manufacturer',required=True)
    mrp_type=fields.Many2one('mrp_type_master.info',string='MRP Type',track_visibility='onchange',help='MRP Type')#,compute='mrp_type_fun'
    source_code_master=fields.Many2one('source_master.info',string='Source Code',required=True)
    mf_part_no=fields.Char(string='Mf. Part No.',track_visibility='onchange',help='Mf. Part No.')
    filename=fields.Char()
    batch_qty=fields.Float(string='Batch Qty.',default=0.0,track_visibility='onchange',help='Batch Qty.')
    reorder_level=fields.Float(string='Reorder Level',default=0.0,track_visibility='onchange',help='Reorder Level')
#     lead_time=fields.Integer(string='Lead Time (Days)')
    buyer_code=fields.Many2one('res.users',string='Buyer Code',required=True)
    bin_location=fields.Char(string='Bin Location')
    bulk_issue_flag=fields.Selection([('yes','Yes'),('no','No')],'Bulk Issue Flag',track_visibility='onchange',help='Bulk Issue Flag')
    channel_flag=fields.Selection([('red','Red'),('green','Green')],'Channel Flag',track_visibility='onchange',help='Channel Flag')
    sr_no_application=fields.Selection([('yes','Yes'),('no','No')],'SrNo.Application')
    unique_product=fields.Char(string="Unique Product Name",compute='unique_product__name_fun',store=True)
    item_type=fields.Many2one('item.type.master',string='Item Type',track_visibility='onchange',help='Item Type')
    
    bom_process_id=fields.Integer(string="BOM Process Id")
    
    produce_delay = fields.Float(
        'Manufacturing Lead Time', default=0.0,track_visibility='onchange',
        help="Average delay in days to produce this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added.")

    @api.model
    def set_routes_id_for_mto_mts(self):
        return self.env['stock.location.route'].search([('name','in',['Make To Order + Make To Stock'])]).ids

    route_ids = fields.Many2many(
        'stock.location.route', 'stock_route_product', 'product_id', 'route_id', 'Routes',
        domain=[('product_selectable', '=', True)],
        default=set_routes_id_for_mto_mts,

        help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, MTO/MTS,...")
   
   
    # @api.onchange('route_ids','type')
    # def route_ids_onchange_mto_mts(self):
    #     # if self.type=='product':
    #         for i in self:
    #             if i.type=='product':
    #                 print("===================i.route_ids",i.route_ids.name)
    #                 # if not i.route_ids.name=='Make To Order + Make To Stock':
    #                 #     raise ValidationError("Please Select Routes Make To Order + Make To Stock")
       






    # Created By | Created Date |Info. 
    # Pradip    |17-1-19 |If select text master item then this text master item update product name
    @api.onchange('text_master_id')
    def onchange_text_prod_name(self):
        for i in self:
            if i.text_master_id:
                i.name=i.text_master_id.text_description or ''
    

    
    # Created By | Created Date 
    # Pradip    |17-1-19 |
    # Info. If Source Code='IN HOUSE MFG' then buyer_code='Admin',channel_flag='green',bulk_issue_flag='no'
    @api.onchange('source_code_master')
    def source_code_master_selection(self):
        buyer_name=self.env['res.users']
        usr_name="Administrator"
        a=buyer_name.search([("name","=",usr_name)])
        print("=============================",a.id)
        for i in self:
            if i.source_code_master.source_description=='IN-HOUSE MFG.':
                
                i.buyer_code=a.id
                i.channel_flag='green'
                i.bulk_issue_flag='no'
            else:
                i.buyer_code=''
                i.channel_flag=''
                i.bulk_issue_flag=''
    
    # Created By | Created Date |Info. 
    # Pradip    |17-1-19 |Product Name convert into Upper case
    @api.onchange('name')
    def product_name_in_uppercase(self):
        for i in self:
            if i.name:
                str_prod_name=(i.name).upper()
                i.name=str_prod_name
    
    
            
    @api.depends('name')
    def unique_product__name_fun(self):
        for p in self:
            text_data_uuustr=str(p.name).lower()
            p.unique_product=text_data_uuustr.replace(' ','')
     
    @api.onchange('mrp_type')
    def mrp_type_onchange(self):
        if self.mrp_type:
            self.batch_qty=0
            self.reorder_level=0

    @api.constrains('reorder_level','batch_qty')
    def check_batch_qty_reorder_level(self):
        if self.mrp_type.unique_mrp_description=='requirementbase':
            if self.batch_qty>0:
                raise ValidationError("Enter Batch Qty. Less than One")
            if self.reorder_level>0:
                raise ValidationError(_("Enter Reorder Level Less than One."))
            if self.batch_qty<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))
            if self.reorder_level<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))

        if self.mrp_type.unique_mrp_description=='consumptionbase' or self.mrp_type.unique_mrp_description=='criticalbase':
            if self.batch_qty==0:
                raise ValidationError("Enter Batch Qty. Greater than Zero")
            if self.reorder_level==0:
                raise ValidationError(_("Enter Reorder Level Greater than Zero."))
            if self.batch_qty<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))
            if self.reorder_level<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))
        
        if self.mrp_type.unique_mrp_description=='batchquantity':
            if self.batch_qty==0:
                raise ValidationError("Enter Batch Qty. Greater than Zero")
            if self.reorder_level>0:
                raise ValidationError(_("Enter Reorder Level Less than One."))
            if self.batch_qty<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))
            if self.reorder_level<0:
                raise ValidationError(_("Please Do Not Enter Negative Number."))
    
    @api.constrains('mrp_type')
    def check_batch_qty(self):
        if self.mrp_type.unique_mrp_description=='consumptionbase':
                if self.batch_qty==0:
                    raise ValidationError("Enter Batch Qty. greater than Zero")

                if self.reorder_level==0:
                    raise ValidationError("Enter Reorder Level Greater than Zero.")

        if self.mrp_type.unique_mrp_description=='criticalbase':
                if self.batch_qty==0:
                    raise ValidationError("Enter Batch Qty. greater than Zero")

                if self.reorder_level==0:
                    raise ValidationError("Enter Reorder Level Greater than Zero.")

        if self.mrp_type.unique_mrp_description=='batchquantity':
                if self.batch_qty==0:
                    raise ValidationError("Enter Batch Qty. greater than Zero")
                if self.batch_qty<0:
                    raise ValidationError(_("Please Do Not Enter Negative Number."))
                if self.reorder_level>0:
                    raise ValidationError("Enter Reorder Level Less than One.")
                if self.reorder_level<0:
                    raise ValidationError(_("Please Do Not Enter Negative Number."))

# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  default_code(Auto Sequence Code) incremented by one with no_gap 
    @api.model
    def create(self, vals):
        rmp_type_obj=self.env['mrp_type_master.info']

        if vals:
            if 'type' in vals: #Upadated-By:Pradip|Updated-Date:7-3-19|Info.if Product type is Stockable Product then create Sequence
                if vals['type']=='product':
                    vals['default_code'] = self.env['ir.sequence'].next_by_code('product.template') 
            
                    vals['drawing_number']=vals['default_code'] #Updated-By:Pradip Update-Date:21-1-19 Info.-drawing_number is same as default_code(Internal Reference) 

            if 'mrp_type' in vals:
                mrp=rmp_type_obj.search([('id','=',vals['mrp_type'])])
                if mrp.unique_mrp_description =='requirementbase':  

                         if vals['batch_qty']>0 or vals['reorder_level']>0 or vals['batch_qty']<0 or vals['reorder_level']<0:
                             raise UserError(_("Enter Batch Qty.And Reorder Level Less than One."))
                         if vals['batch_qty']<0:
                             raise UserError(_("Please Do Not Enter Negative Number."))
                         if vals['reorder_level']<0:
                             raise UserError(_("Please Do Not Enter Negative Number."))
                if mrp.unique_mrp_description =='consumptionbase' or mrp.unique_mrp_description =='criticalbase':
                    if vals['batch_qty']==0 or vals['reorder_level']==0 or vals['batch_qty']<0 or vals['reorder_level']<0:
                            raise UserError(_("Enter Batch Qty. and Reorder Level Greater than Zero."))
                    elif vals['batch_qty']<0 or vals['reorder_level']<0:
                            raise UserError(_("Please Do Not Enter Negative Number."))
                if mrp.unique_mrp_description =='batchquantity':
                    if vals['batch_qty']==0 or  vals['batch_qty']<0:
                            raise UserError(_("Enter Batch Qty. Greater than Zero."))
                    if vals['reorder_level']>0 or vals['reorder_level']<0:
                            raise UserError(_("Enter Reorder Level. Less than One."))
                    elif vals['batch_qty']<0 or vals['reorder_level']<0:
                            
                            raise UserError(_("Please Do Not Enter Negative Number."))
    
        if vals['name']:
            if vals['name'].replace(' ','')=='':
                raise UserError(_("Please Enter Product  Name."))
            
        if 'produce_delay' in vals:  #Updatd-By-Pradip update-Date:07-03-19 Info.Manufacturing Lead Time validation for Negative values
            if vals['produce_delay']<0:
                raise UserError(_("Please Do Not Enter Negative Customer Lead Time.")) 
            
            else:
                return super(product_template_inhe, self).create(vals)
    
    
    @api.multi
    def write(self,values):
        if values:
            if 'name' in values:    #Updatd-By-Pradip update-Date:21-1-19 Info.Product Name Do not Edit After Creating Product
                if values['name']:
                #.replace(' ','')=='':
                    raise UserError(_("Please Do Not Edit Product Name"))
            
            if 'text_master_id' in values:
                if values['text_master_id']:
                    raise UserError(_("Please Do Not Edit Text")) #Updatd-By-Pradip update-Date:21-1-19 Info.Text Master Id Name Do not Edit After Creating Text Master Id
                
            if 'produce_delay' in values:  #Updatd-By-Pradip update-Date:07-03-19 Info.Manufacturing Lead Time validation for Negative values  
                if values['produce_delay']<0:
                    raise UserError(_("Please Do Not Enter Negative Customer Lead Time.")) 
        return super(product_template_inhe, self).write(values)
    
    
    
    
    
    
    
    
    


