
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

config_data = {
    "theme": {
        "primaryColor": "#0054A4",
        "secondaryColor": "#009D5C",
        "fontFamily": "Roboto"
    },
    "layout": {
        "sections": [
            {"name": "Upload Documents", "icon": "upload_icon"},
            {"name": "Search Policies", "icon": "search_icon"},
            {"name": "View Approvals", "icon": "approval_icon"}
        ]
    }
}

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Management App</title>
    <style>
        body { font-family: {{ theme.fontFamily }}; background-color: {{ theme.primaryColor }}; color: white; text-align: center; }
        h1 { background-color: {{ theme.secondaryColor }}; padding: 20px; margin: 0; }
        .section { margin: 20px; padding: 10px; border: 1px solid white; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Dynamic Theming App</h1>
    <div id="dashboard">
        {% for section in layout.sections %}
        <div class="section">
            <h2>{{ section.name }}</h2>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(html_template, theme=config_data['theme'], layout=config_data['layout'])

@app.route('/config')
def get_config():
    return jsonify(config_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    