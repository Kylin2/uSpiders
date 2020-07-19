import os
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerRunner
from scrapy.utils.conf import arglist_to_dict
from scrapy.utils.python import without_none_values
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return "[options] <spider>"

    def short_desc(self):
        return "Run a spider"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")
        parser.add_option("-k", "--keyword", metavar="KEYWORD",type="str",dest="keyword",default="",
                          help="set keyword")
        parser.add_option("-p", "--price", metavar="PRICE",nargs = 2, type="int", dest="price", default=[],
                          help="set the range of price")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
        if opts.output:
            if opts.output == '-':
                self.settings.set('FEED_URI', 'stdout:', priority='cmdline')
            else:
                self.settings.set('FEED_URI', opts.output, priority='cmdline')
            feed_exporters = without_none_values(
                self.settings.getwithbase('FEED_EXPORTERS'))
            valid_output_formats = feed_exporters.keys()
            if not opts.output_format:
                opts.output_format = os.path.splitext(opts.output)[1].replace(".", "")
            if opts.output_format not in valid_output_formats:
                raise UsageError("Unrecognized output format '%s', set one"
                                 " using the '-t' switch or as a file extension"
                                 " from the supported list %s" % (opts.output_format,
                                                                  tuple(valid_output_formats)))
            self.settings.set('FEED_FORMAT', opts.output_format, priority='cmdline')

    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError("running 'scrapy crawl' with more than one spider is no longer supported")
        spname = args[0]

        self.settings.set('KEYWORD',opts.keyword)
        '''
        if len(opts.price) != 2:
            raise UsageError("the range of price is wrong")
        else:
            lprice = opts.price[0]
            hprice = opts.price[1]
        if lprice < 0:
            raise UsageError("the low price must not be less 0")
        if lprice > hprice:
            raise UsageError("the high price must not be less than that of low price")
        self.settings.set('LPRICE', lprice)
        self.settings.set('HPRICE', hprice)
        '''

        self.crawler_process.crawl(spname, **opts.spargs)
        self.crawler_process.start()

        #if self.crawler_process.bootstrap_failed:
            #self.exitcode = 1