"""
# open & fill Excel template for attachment:
if template == 'industrial':
    template_file = path.join("..", "output", "webapp_resources", "OG_Operator_Feedback_2024.xlsx")
else:
    template_file = path.join("..", "output", "webapp_resources", "Landfill_Operator_Feedback_2023.xlsx")

#suppress warnings about data validation - Excel's extensions aren't fully compatible with openpyxl but these modified templates should work
#https://www.reddit.com/r/learnpython/comments/mfy9qa/openpyxl_deleting_data_validation/
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    wb = openpyxl.load_workbook(template_file, keep_vba=False)
ws = wb.active
ws["$D$9"] = id_incidence
#ws["$D$10"] = plumeIdList
ws["$D$10"] = datetime.now().date().strftime("%Y-%m-%d")
ws["$D$11"] = coordinates
ws["$D$12"] = plume_timestamp

# https://stackoverflow.com/a/58812798
wb_bytes = BytesIO()
wb.save(wb_bytes)
wb_bytes.seek(0)
excel_attachment = MIMEApplication(wb_bytes.getvalue())
excel_attachment.add_header("Content-Disposition", "attachment", filename=f"out_{id_incidence}.xlsx")
excel_attachment.add_header("Content-Type", "application/vnd.ms-excel; charset=UTF-8")
email_message.attach(excel_attachment)
"""
