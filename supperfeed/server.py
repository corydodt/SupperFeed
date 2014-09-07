"""
The web/app server
"""
from functools import wraps

from jinja2 import Environment, PackageLoader, ChoiceLoader

from klein import Klein

from mongoengine import connect

from supperfeed.build import Recipe


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


class BaseServer(object):
    app = Klein()

    def __init__(self):
        connect("supperfeed")

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

    @app.route('/recipe/<string:recipeURL>/edit', methods=['GET'])
    @simpleRenderer('templates/recipe-editor.html')
    def editRecipe(self, request, recipeURL):
        recipe = Recipe.objects.get(url=recipeURL)
        return {'recipe': recipe}

    @app.route('/recipe/<string:recipeURL>/edit', methods=['POST'])
    def saveRecipe(self, request, recipeURL):
        recipe = Recipe.objects.get(url=recipeURL)

        recipe.name = request.args.get('name', [''])[0]
        recipe.author = request.args.get('author', [''])[0]
        recipe.publisher = request.args.get('publisher', [''])[0]
        #recipe.image = request.args.get('image', [''])[0]
        recipe.prepTime = request.args.get('prep', [''])[0]
        recipe.cookTime = request.args.get('cooktime', [''])[0]
        recipe.yields = request.args.get('yield', [''])[0]
        #recipe.calories = request.args.get('calories', [''])[0]
        recipe.save()

        request.redirect('/recipe/' + recipeURL)

        return None

resource = BaseServer().app.resource
