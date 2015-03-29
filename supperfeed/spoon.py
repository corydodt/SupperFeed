import sys

from twisted.python import usage

from txpx import runner

from supperfeed.build import Build


class Options(usage.Options):
    subCommands = [
        ("build", None, Build, Build.__doc__),
        ]

    def opt_version(self):
        print 'SupperFeed server v???'
        return usage.Options.opt_version(self)

    def postOptions(self):
        """Recommended if there are subcommands:"""
        if self.subCommand is None:
            self.synopsis = "spoon <subcommand>"
            raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")


run = runner(Options)
