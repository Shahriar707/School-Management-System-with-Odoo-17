def create_styled_table(student_results):
    header_style = "background-color: #4CAF50; color: white; font-weight: bold; text-align: left; padding: 12px; border-bottom: 2px solid #ddd;"
    row_style = "background-color: #ffffff; padding: 12px; text-align: left; color: black; border-bottom: 1px solid #ddd;"
    row_hover_style = "background-color: #f1f1f1;"

    table = "<table border='1' style='border-collapse: collapse; width: 100%; border-radius: 8px; overflow: hidden;'>"
    table += f"<tr style='{header_style}'>"
    table += "<th>Course Name</th>"
    table += "<th>Grade</th>"
    table += "<th>Marks</th>"
    table += "<th>Result Date</th>"
    table += "</tr>"

    if student_results:
        for result in student_results:
            table += f"<tr style='{row_style}' onmouseover='this.style.backgroundColor=\"{row_hover_style}\"' onmouseout='this.style.backgroundColor=\"white\"'>"
            table += f"<td style='padding: 8px 12px; color: black; border-right: 1px solid #ddd;'>{result['course_name']}</td>"
            table += f"<td style='padding: 8px 12px; color: black; border-right: 1px solid #ddd;'>{result['grade']}</td>"
            table += f"<td style='padding: 8px 12px; color: black; border-right: 1px solid #ddd;'>{result['marks']}</td>"
            table += f"<td style='padding: 8px 12px; color: black;'>{result['result_date']}</td>"
            table += "</tr>"

    table += "</table>"
    return table
