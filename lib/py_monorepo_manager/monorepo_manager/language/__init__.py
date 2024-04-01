from .javascript import JavascriptProject
from .python import PythonProject
from .rust import RustProject

LanguageProjects = JavascriptProject | PythonProject | RustProject
