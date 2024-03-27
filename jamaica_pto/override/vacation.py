import frappe
from datetime import datetime
from frappe.utils.data import getdate


#leave allocation after 110 and 220 days
def new_leave_allocation_of_2weeks(doc, method=None):
    current_date = datetime.now().date()
    current_year_start = datetime(current_date.year, 1, 1).date()
    next_year_end = datetime(current_date.year + 1, 12, 31).date()
    pto_setting=frappe.get_doc('Paid Time Off Settings')
    mandatory_working_days=pto_setting.mandatory_working_days
    frappe.log_error('mandatory_working_days',mandatory_working_days)
    employee_receive_1_day=pto_setting.employee_receive_1_day_on_the_basis_of_how_many_working_days
    frappe.log_error('employee_receive_1_day',employee_receive_1_day)
    start_accural_after=mandatory_working_days+employee_receive_1_day
    frappe.log_error('start_accural_after',start_accural_after)
    current_employee_list = frappe.db.get_list(
        'Employee',
        filters=[['status', '=', 'Active']],
        fields=['name', 'date_of_joining'],
        as_list=False
    )
    attendance_data = []
    
    if current_employee_list:
        for employee in current_employee_list:
            employee_name = employee['name']
            sql_query = '''
                SELECT employee, COUNT(status) as total_present_days 
                FROM `tabAttendance` 
                WHERE employee = '{}' AND status='Present' AND status!='Cancelled'
            '''.format(employee['name'])
            total_present_days = frappe.db.sql(sql_query, as_dict=True)
            if total_present_days:
                for i in total_present_days:
                    attendance_data.append(i)
    
    for pemployee in attendance_data:
        if pemployee['total_present_days'] == start_accural_after:
            leave_allocation = frappe.new_doc('Leave Allocation')
            leave_allocation.employee = pemployee['employee']
            leave_allocation.leave_type = '2 Weeks Paid vacation leave'
            leave_allocation.from_date = current_year_start
            leave_allocation.to_date = next_year_end
            leave_allocation.new_leaves_allocated = 1
            leave_allocation.carry_forward = 1
            leave_allocation.docstatus = 1
            leave_allocation.insert()
            frappe.db.set_value('Employee', pemployee['employee'], {'custom_last_leave_allocate_date': current_date})
            frappe.msgprint("Leave allocated successfully")
        
        if pemployee['total_present_days'] == 220:
            frappe.db.set_value('Leave Allocation', {'employee': pemployee['employee']}, {'new_leaves_allocated': 14, 'total_leaves_allocated': 14})
            frappe.db.set_value('Employee', pemployee['employee'], {'custom_last_leave_allocate_date': current_date})
        
        allocated_date = frappe.db.get_value('Employee', pemployee['employee'], 'custom_last_leave_allocate_date')
        sql_query = '''
            SELECT COUNT(status) 
            FROM `tabAttendance` 
            WHERE employee='{0}' AND attendance_date BETWEEN '{1}' AND '{2}' AND status='Present'
        '''.format(pemployee['employee'], allocated_date, current_date)
        days_after_leave_allocation = (frappe.db.sql(sql_query)[0][0]) - 1
        if days_after_leave_allocation == employee_receive_1_day:
            currently_allocated_leaves = frappe.db.get_value('Leave Allocation', {'employee': pemployee['employee']}, 'new_leaves_allocated')
            if currently_allocated_leaves < 14:
                currently_allocated_leaves += 1
                frappe.db.set_value('Leave Allocation', {'employee': pemployee['employee']}, {'new_leaves_allocated': currently_allocated_leaves, 'total_leaves_allocated': currently_allocated_leaves})
                frappe.db.set_value('Employee', pemployee['employee'], {'custom_last_leave_allocate_date': current_date})

                frappe.msgprint("Leave updated successfully")

        




# # Allocation if employee completed ten years              
# def new_leave_allocation_of_3weeks(doc,method=None):
#     current_year = datetime.now().year
#     current_date = datetime.now().date()
#     current_year_start = datetime(current_date.year, 1, 1).date()
#     next_year_end = datetime(current_date.year + 1, 12, 31).date()

#     current_employee_list = frappe.db.get_list(
#     'Employee',
#     filters=[
      
#         ['status', '=', 'Active']
#     ],
#     fields=['name','date_of_joining'],
#     as_list=False
# )
#     if current_employee_list:

#         for employee in current_employee_list:
#             years_since_joining  = (current_year-getdate(employee['date_of_joining']).year)
#             employee['years_since_joining'] = years_since_joining
#             if employee['years_since_joining']>=10:
#                 if frappe.db.exists('Leave Allocation',{'employee':employee['name']}):
#                     frappe.db.set_value('Leave Allocation', {'employee':employee['name']}, {'new_leaves_allocated': 21 ,'total_leaves_allocated':21,'leave_type':'3 Weeks Paid vacation leave'})
#                 else:
#                     leave_allocation = frappe.new_doc('Leave Allocation')
#                     leave_allocation.employee=employee['name']
#                     leave_allocation.leave_type='3 Weeks Paid vacation leave'
#                     leave_allocation.from_date=current_year_start
#                     leave_allocation.to_date=next_year_end
#                     leave_allocation.new_leaves_allocated=21
#                     leave_allocation.carry_forward=1
#                     leave_allocation.insert()

            

    

    

