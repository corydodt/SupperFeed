"""
Build the database entries from the live spreadsheet
"""
import re

from twisted.python import usage

from mongoengine import connect, Document, fields

from supperfeed.sheets import getSheetData


ITEM_SEPARATOR = '@@SEPARATOR@@'


class Recipe(Document):
    """
    Ingredients and instructions to prepare one dish
    """
    name = fields.StringField()
    url = fields.StringField(unique=True)
    importedFrom = fields.URLField()
    author = fields.StringField(default="Cory Dodt")
    image = fields.URLField()
    prepTime = fields.StringField()
    cookTime = fields.StringField()
    recipeYield = fields.StringField()
    tags = fields.ListField(fields.StringField())
    calories = fields.IntField()
    ingredients = fields.ListField(fields.StringField())
    instructions = fields.ListField(fields.StringField())

    @classmethod
    def fromLoadedData(cls, jsonData):
        """
        Load data from the simple datastructure extracted by recipeschema
        """
        props = jsonData['properties']
        name = props['name'][0]
        url = urlifyName(name)
        self, created = cls.objects.get_or_create(url=url)
        self.name = name
        self.url = urlifyName(self.name)
        self.image = props.get('image', [None])[0]
        self.author = props.get('author', [None])[0]
        self.recipeYield = props.get('recipeYield', [None])[0]
        keys = props.keys()
        if 'ingredients' in keys and 'recipeInstructions' in keys and 'importedFromURL' in keys:
            self.ingredients = []
            for i in props['ingredients']:
                self.ingredients.extend(i.split(ITEM_SEPARATOR))

            self.instructions = []
            for ii in props['recipeInstructions']:
                self.instructions.extend(ii.split(ITEM_SEPARATOR))

            self.importedFrom = props['importedFromURL']
            return self
        else:
            return None

def urlifyName(name):
    """
    Return a url-friendly version of name
    """
    return re.sub(r'[^-a-z0-9]', '-', name.lower())


class Build(usage.Options):
    """
    Create the ingredients from the google sheet
    """
    synopsis = "build"

    optFlags = [
        ["delete", None, "Delete all recipes before loading new ones"],
        ]

    def postOptions(self):
        connect('supperfeed')

        if self['delete']:
            Recipe.objects.delete()

        rows = getSheetData()
        for row in rows:
            name = row['title']
            url = urlifyName(name)
            rec, success = Recipe.objects.get_or_create(url=url)
            rec.name = name
            rec.recipeYield = row.get('servings')
            rec.tags = map(str.strip, row.get('tags', '').split(','))
            rec.ingredients = row['ingredients'].split('\n')
            rec.instructions = row['instructions'].split('\n')
            rec.save()

        print 'Recipe count = %s' % len(Recipe.objects)
