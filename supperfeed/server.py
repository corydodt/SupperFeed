"""
The web/app server
"""
from functools import wraps
import re

from mongoengine import connect, Document, fields

from jinja2 import Environment, PackageLoader, ChoiceLoader

from zope.interface import implements

from twisted.web.server import Site
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin

from klein import Klein


supperLoader = ChoiceLoader([
    PackageLoader('supperfeed', '.'),
    # ...
    ])

env = Environment(
        loader=supperLoader,
        block_start_string='<%',
        block_end_string='%>',
        comment_start_string='<#',
        comment_end_string='#>',
        variable_start_string='<<',
        variable_end_string='>>',
        )


def render(template, **kw):
    """
    Pass keywords through a template and get a string
    """
    if isinstance(template, basestring):
        template = env.get_template(template)

    return template.render(**kw)


def simpleRenderer(template):
    """
    Render a template using the dict returned by the function
    """
    tpl = env.get_template(template)

    def renderImpl(fn):
        @wraps(fn)
        def render(self, request, *a, **kw):
            dct = fn(self, request, *a, **kw)
            return tpl.render(**dct)
        return render

    return renderImpl


def urlifyName(name):
    """
    Return a url-friendly version of name
    """
    return re.sub(r'[^-a-z0-9]', '-', name.lower())


class Recipe(Document):
    name = fields.StringField()
    url = fields.StringField()
    author = fields.StringField(default="Cory Dodt")
    image = fields.URLField()
    prepTime = fields.StringField()
    cookTime = fields.StringField()
    recipeYield = fields.StringField()
    tags = fields.ListField(fields.StringField())
    calories = fields.IntField()
    ingredients = fields.ListField(fields.StringField())
    instructions = fields.ListField(fields.StringField())


connect('supperfeed')
Recipe.objects.delete()
Recipe(
        name="macaroni and nothing",
        url=urlifyName("macaroni and nothing"),
        prepTime="PT15M",
        cookTime="CT10M",
        recipeYield="10 things",
        tags=["macaroni", "pasta"],
        calories=350,
        ingredients=["macaroni", "water"],
        instructions=["Bring water to a boil.",
            "Stir in remaining ingredients.",
            "Cook 10 minutes",
            ],
        ).save()


class BaseServer(object):
    app = Klein()

    @app.route('/')
    def home(self, request):
        request.redirect('/list')

    @app.route('/list')
    @simpleRenderer('templates/recipe-list.html')
    def recipeList(self, request):
        return {'recipes': Recipe.objects}

    @app.route('/recipe/<string:recipeURL>')
    @simpleRenderer('templates/recipe.html')
    def recipe(self, request, recipeURL):
        recipe = Recipe.objects.get(url=recipeURL)
        return {'recipe': recipe}

resource = BaseServer().app.resource
