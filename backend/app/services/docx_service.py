from docxtpl import DocxTemplate

def render_template(template_path: str, context: dict, output_path: str):
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)
    return output_path
