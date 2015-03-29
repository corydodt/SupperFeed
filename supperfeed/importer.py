"""
Import recipes from URLs to our database
"""
import re

from txpx import background, EchoProcess

from supperfeed.build import Recipe


class ImportProcess(EchoProcess):
    """
    Import a recipe by loading the json data dumped by the downloader process
    """
    def __init__(self, *a, **kw):
        self.linebuf = []

    def outLineReceived(self, line):
        if re.match(line, r'^/\*+/$'):
            self.finished()
        self.linebuf.append(line)

    def finished(self):
        data = json.loads('\n'.join(self.linebuf))
        recipe = Recipe.fromLoadedData()
        recipe.save()
        self.linebuf[:] = []


