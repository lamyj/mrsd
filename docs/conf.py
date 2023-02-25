project = "mrsd"
copyright = "2023, Julien Lamy"
author = "Julien Lamy"

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_default_options = {
    "member-order": "bysource"
}

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "css/style.css",
]
html_show_sphinx = False

