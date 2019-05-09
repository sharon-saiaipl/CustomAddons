from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError


# Created By | Created Date |Info.
# Pradip    |14-03-19 | take operation.master dropdown from master

class MrpRoutingWorkcenter_inherited(models.Model):
    _inherit= 'mrp.routing.workcenter'


    _sql_constraints = [('name valida', 'unique(name,routing_id)', 'Please Enter Unique Combination of Routing Name and Work Center Operation'),]

    name = fields.Char('Operation', compute='oper_desc_id_to_name_cpy',store=True)
    # name = fields.Char('Operation')

    operation_descr_id = fields.Many2one('operation.master','Operation',required=True) # 1-4-2019updatedby-pradip required=true ,bcause-update-set issue to jeevan

    """Created By-Pradip|Created Date-3-Apr-2019
    operation name select from operation.master 
    and it set to operation name column(mrp.routing.workcenter)
    """
    # @api.onchange('operation_descr_id')
    # def select_operation_name(self):
    #     # for i in self:
    #         if self.operation_descr_id:
    #             self.name=(self.operation_descr_id.operation_description)
            

    # @api.onchange('operation_descr_id','name')
    # def select_operation_name(self):
    #     # for i in self:
    #         # if self.operation_descr_id:
    #             self.operation_descr_id=
    #             # print("================99990",self.name)
    #         # return 


    # @api.depends('operation_descr_id','name')
    # def oper_desc_id_to_name_cpy(self):
    #     for i in self:
    #         if i.operation_descr_id:
    #             i.name=str(i.operation_descr_id.operation_description)
      
    @api.depends('operation_descr_id','name')
    def oper_desc_id_to_name_cpy(self):
        for i in self:
            if i.operation_descr_id:
                i.name=str(i.operation_descr_id.operation_description)
      