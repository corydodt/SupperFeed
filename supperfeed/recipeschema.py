"""
Parse a url; return as json on stdout
"""
from cStringIO import StringIO
import sys
import json

import microdata

from bs4 import BeautifulSoup

from twisted.python import usage
from twisted.internet import reactor, defer
from twisted.web.client import getPage

from txpx import runner

from supperfeed.build import ITEM_SEPARATOR

MICROFORMAT_RECIPE = 'http://schema.org/Recipe'


# list tags that cannot contain text content, and put separators after instead
# of inside
POSTFIX_TAGS = 'br img script hr'.split()

def insertSeparator(soup, el, separator):
    """
    Find the last text eleemnt of el and add the separator there
    """
    if el.name in POSTFIX_TAGS:
        el.insert_after(soup.new_string(separator))
    else:
        lastText = el.find_all(text=True)
        if lastText:
            repl = soup.new_string(lastText[-1] + separator)
            lastText[-1].replace_with(repl)

def separateByClass(soup, parent, classes, separator=ITEM_SEPARATOR):
    """
    Break up ingredients or instructions formatted by the method of using a class,
    by appending the separator character
    """
    for thing in parent.find_all(None, class_=classes):
        thing.insert_after(soup.new_string(separator))

def separateByTag(soup, parent, splitters, separator=ITEM_SEPARATOR):
    """
    Break up instructions formatted by the method of using a particular tag
    between steps, by appending the separator character
    """
    for splittee in parent.find_all(name=splitters):
        insertSeparator(soup, splittee, separator)

class Options(usage.Options):
    synopsis = "recipeschema 'http://....'"

    stdout = sys.stdout
    stderr = sys.stderr

    def parseArgs(self, *urls):
        self['urls'] = urls

    def showData(self, recipes):
        """
        Convert data to json and write to stdout
        """
        for recipe in recipes:
            json.dump(recipe, self.stdout, indent=2)
            print
            print '/'  + '*' * 50 + '/'

    def cleanData(self, recipes, url):
        """
        Remove junk spacing from structured data
        """
        ret = []
        for recipe in recipes:
            props = recipe['properties']
            for k, vals in props.items():
                new = []
                for v in vals:
                    if type(v) is dict:
                        if v.has_key('properties'):
                            vv = ''
                            for prop in v['properties'].values():
                                vv += prop[0]
                            v = vv
                        else:
                            continue
                    lines = v.splitlines()
                    vv = ' '.join([line.strip() for line in lines]).strip()
                    new.append(vv)
                props[k] = new
            props['importedFromURL'] = url
            ret.append(recipe)
        return ret

    def consumeData(self, data):
        """
        Parse the microdata into structured data
        """
        ret = []

        soup = BeautifulSoup(StringIO(data))
        ingredientses = soup.find_all(None, itemprop='ingredients')
        for ing in ingredientses:
            separateByClass(soup, ing, "ingredient")
            separateByTag(soup, ing, ['br', 'tr', 'li'])
        instructionses = soup.find_all(None, itemprop="recipeInstructions")
        for ins in instructionses:
            separateByClass(soup, ins, "instruction")
            separateByTag(soup, ins, ['br', 'tr', 'li'])
        workingDocument = StringIO(soup.encode('utf-8'))

        items = microdata.get_items(workingDocument)
        for i in items:
            for typ in i.itemtype:
                if typ.string == MICROFORMAT_RECIPE:
                    ret.append(i.json())
                    break
        return map(json.loads, ret)

    def fetchURLs(self):
        _dl = []
        for u in self['urls']:
            d = getPage(u)
            def bad(f, u):
                print "** Could not fetch {u}:".format(u=u)
                f.printException()
                return f

            d.addErrback(bad, u
                    ).addCallback(self.consumeData
                    ).addCallback(self.cleanData, u
                    ).addCallback(self.showData)
            _dl.append(d)

        dl = defer.DeferredList(_dl)
        dl.addBoth(lambda x: reactor.stop())
        return dl

    def postOptions(self):
        reactor.callWhenRunning(self.fetchURLs)
        reactor.run()


run = runner(Options)
