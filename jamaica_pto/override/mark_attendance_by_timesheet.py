import frappe
from datetime import datetime
from frappe.utils.data import getdate



def mark_attendance_on_2hrs_complete(doc, method=None):
    # frappe.msgprint("I am callable")
    pto_setting=frappe.get_doc('Paid Time Off Settings')
    minimum_working_hours=pto_setting.minimum_working_hours
    # frappe.log_error("minimum_working_hours",minimum_working_hours)
    child_timesheet = frappe.get_all("Timesheet Detail", filters={"parent": doc.name}, fields=["from_time", "to_time", "hours"])
    for child in child_timesheet:
        child['from_date'] = child.get("from_time").date() if child.get("from_time") else None
        child['to_date'] = child.get("to_time").date() if child.get("to_time") else None
        if child['hours']>=minimum_working_hours:
            if not frappe.db.exists('Attendance',{'employee':doc.employee,'attendance_date':child['from_date']}):
                mark_attendance = frappe.new_doc('Attendance')
                mark_attendance.employee=doc.employee
                mark_attendance.status='Present'
                mark_attendance.attendance_date=child['from_date']
                mark_attendance.insert()
        frappe.msgprint("done")


def submit_attendance_on_timesheet_submission(doc,method=None):
    frappe.msgprint("calling")
    child_timesheet = frappe.get_all("Timesheet Detail", filters={"parent": doc.name}, fields=["from_time", "to_time", "hours"])
    for child in child_timesheet:
        child['from_date'] = child.get("from_time").date() if child.get("from_time") else None
        frappe.db.set_value('Attendance',{'employee':doc.employee,'attendance_date':child['from_date']},{'docstatus':1})
    


