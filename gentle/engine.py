#!/usr/bin/env python

from sys import argv
from yaml import load
from re import match, findall, sub

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

ENTRY_TYPE = enum(HEADER = 0, SUB_HEADER = 1, PARAGRAPH = 2, UNKNOWN = 3)

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def input_checking(inputArgs):
        if check_length(inputArgs, 2) is False or \
           check_extension(inputArgs, ".md") is False:
            print "usage: render.py index.md"
            sys.exit()
        else:
                return inputArgs[1]

    @staticmethod
    def check_length(inputArgs, length):
        if len(inputArgs) == length:
            return True
        else:
            return False

    @staticmethod
    def check_extension(inputArgs, extension):
        extensionLength = len(extension)
        fileToCheck = inputArgs[1]
        if fileToCheck[-extensionLength:] == extension:
            return True
        else:
            return False

    class Identify:
        def __init__(self):
            pass

        @staticmethod
        def is_header(entry):
            matched = match('^[\#]{1}([a-z-A-Z-0-9- ._:)($\[\]!~@,-]{1,})$', entry)
            return matched is not None

        @staticmethod
        def is_sub_header(entry):
            matched = match('^[\#]{2}([a-z-A-Z-0-9- ._:)($\[\]!~@,-]{1,})$', entry)
            return matched is not None

        @staticmethod
        def is_paragraph(entry):
            matched = match('^[\-]{3}([a-z-A-Z-0-9- ._:)($\[\]!~@,-]{1,})[\-]{3}$', entry)
            return matched is not None

        @staticmethod
        def check_entry_type(entry):
            if Utils.Identify.is_header(entry) is True:
                return ENTRY_TYPE.HEADER
            elif Utils.Identify.is_sub_header(entry) is True:
                return ENTRY_TYPE.SUB_HEADER
            elif Utils.Identify.is_paragraph(entry) is True:
                return ENTRY_TYPE.PARAGRAPH
            else:
                return ENTRY_TYPE.UNKNOWN

class Configuration(object):
    def __init__(self, config="config.yaml"):
        self.CONFIG_FILE = config

    def load_configuration(self):
        config_data  = {}
        stream       = open(self.CONFIG_FILE, 'r')
        config_steam = load(stream)
        for key, value in config_steam.items():
            config_data.update({key : value})
        return config_data


class PreProcessing:
    def __init__(self, markdown_source):
        self.markdown_source = markdown_source

    def scan_source(self):
        processed_data = []
        with open(self.markdown_source) as stream:
            for block in stream:
                entry_type = Utils.Identify.check_entry_type(block)
                proc_entry = Processing.superstructure((entry_type, block))
                processed_data.append((proc_entry, entry_type))
                print processed_data
        return processed_data

    def scan_entry(self, preprocessed_data):
        processed_data = []
        for superstructure in preprocessed_data:
            entry_type, raw_entry = superstructure
            style_processed_entry = Processing.style(raw_entry)
            processed_entry = Processing.links(style_processed_entry)
            processed_data.append((entry_type, processed_entry))
            print processed_data
        return processed_data

class Processing:
    def __init__(self):
        self.configuration = Configuration().load_configuration()
        self.html_header = '<html><head><title>' + self.configuration["blog_name"]  + ' - ' \
        + self.configuration["blog_description"]  + '</title>\
        <link type="text/css" rel="stylesheet" href="' + self.configuration["theme"]  + '" />\
        </head><body>'
        self.html_footer = '</body></html>'

    @staticmethod
    def compile(fully_processed_data):
        Process = Processing()
        body = ""
        for structure in fully_processed_data:
            body += ' ' + structure
            return Process.header_html + body + Process.footer_html
    @staticmethod
    def superstructure(data):
        structure_type, structure = data
        Process = Processing()
        structure_catalog = [Process.header, Process.subheader, Process.title, Process.paragraph]
        return structure_catalog[structure_type](structure)

    def header(self, entry):
        if entry[0] == '#':
            entry = entry[1:]
        return '<h1>' + entry + '</h1>'

    def subheader(self, entry):
        if entry[:2] == '##':
            entry = entry[2:]
        return '<h2>' + entry + '</h2>'

    def title(self, entry):
        if entry[:3] == '###':
            entry = entry[3:]
        return '<h4>' + entry + '</h4>'

    def paragraph(self, entry):
        if entry[:3] == '---' and entry[-3:] == '---':
            entry = entry[3:-3]
        return '<p>' + entry + '</p>'

    @staticmethod
    def links(to_process):
        Process = Processing()
        link_catalog = [Process.regular_links, Process.youtube_links, Process.image]
        for type_link in link_catalog:
            processed = type_link(to_process)
        return processed

    def regular_links(self, data):
        pattern = "\[([a-zA-Z0-9\ \!\?\,\:\*\'\;\/\/\.\&\=\?\%]*)\]\((https?\:\/\/[a-zA-Z-0-9\/\.\&\=\?\%]*)\)"
        repl = '<a href="\\2">\\1</a>'
        processed = sub(pattern, repl, data)
        return processed

    def youtube_links(self, data):
        return data

    def image(data):
        pattern = "\[([a-zA-Z0-9\ \!\?\,\:\*\'\;\/\/\.\&\=\?\%]*)\]\((https?\:\/\/[a-zA-Z-0-9\/\.\&\=\?\%]*)\)"
        repl = '<img alt="\\1" href="\\2" />'
        processed = sub(pattern, repl, data)
        return processed

    @staticmethod
    def style(to_process):
        Process = Processing()
        style_format = [Process.bold, Process.italic, Process.underline]
        for formatting in style_format:
            processed = formatting(to_process)
        return processed

    def bold(self, data):
        pattern = "\*[a-z-A-Z-0-9\?\!\.\*\[\]\(\)\:\/\?\&\=\!\;\ ]*\*"
        repl    = "<b>\\1</b>"
        print type(pattern), type(repl), type(data)
        processed = sub(pattern, repl, data)
        return processed

    def italic(self, data):
        pattern = "\*\*[a-z-A-Z-0-9\?\!\.\*\[\]\(\)\:\/\?\&\=\!\;\ ]*\*\*"
        repl    = "<i>\\1</i>"
        processed = sub(pattern, repl, data)
        return processed

    def underline(self, data):
        pattern = "\_[a-z-A-Z-0-9\?\!\.\*\[\]\(\)\:\/\?\&\=\!\;\ ]*\_"
        repl    = "<u>\\1</u>"
        processed = sub(pattern, repl, data)
        return processed


class Main(object):
    def __init__(self, path_to_markdown=None):
        self.path_to_markdown = path_to_markdown

    def create_article(self):
        PreProcess = PreProcessing(self.path_to_markdown)
        unprocessed_data = PreProcess.scan_source()
        data = []
        for structure in unprocessed_data:
            data.append(PreProcess.scan_entry(unprocessed_data))
        print data
