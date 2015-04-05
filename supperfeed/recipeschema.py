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


def preCleanIngredients(soup, separator=ITEM_SEPARATOR):
    """
    Break up ingredients formatted by the method of using an ingredient class
    by appending the separator character
    """
    for ing in soup.find_all(None, "ingredient"):
        ing.insert_after(soup.new_string(separator))

def preCleanInstructions(soup, splitter='br', separator=ITEM_SEPARATOR):
    """
    Break up instructions formatted by the method of inserting a br
    between steps, by appending the separator character
    """
    instructionses = soup.find_all(None, itemprop="recipeInstructions")
    for ins in instructionses:
        for sub in ins.contents:
            if sub.name == splitter:
                sub.insert_after(soup.new_string(separator))

class Options(usage.Options):
    synopsis = "recipeschema 'http://....'"

    stdout = sys.stdout
    stderr = sys.stderr

    def parseArgs(self, *urls):
        self['urls'] = urls

    def showData(self, recipes):
        for recipe in recipes:
            json.dump(recipe, self.stdout, indent=2)
            print
            print '/'  + '*' * 50 + '/'

    def cleanData(self, recipes, url):
        ret = []
        for recipe in recipes:
            props = recipe['properties']
            for k, vals in props.items():
                new = []
                for v in vals:
                    lines = v.splitlines()
                    vv = ' '.join([line.strip() for line in lines]).strip()
                    new.append(vv)
                props[k] = new
            props['importedFromURL'] = url
            ret.append(recipe)
        return ret

    def consumeData(self, data):
        ret = []

        soup = BeautifulSoup(StringIO(data))
        preCleanIngredients(soup)
        preCleanInstructions(soup)
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
