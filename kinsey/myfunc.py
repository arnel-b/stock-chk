import os
from .stock_checker import Scraper
import json


class Initializer:

    return_val = {}
    resume = False

    def __init__(self):
        if len(os.listdir("media/from_chino")) == 1:
            self.return_val.update({"file": os.listdir("media/from_chino")[0]})
            self.resume = True
            # print(self.return_val)

class Resume(Initializer):
    def __init__(self):
        super(Resume, self).__init__()
        # stock_checker.main()


class NewScrape(Initializer):
    def __init__(self):
        super(NewScrape, self).__init__()
        scraper = Scraper()


class Progress:

    has_existing = False
    xl_file = ""
    json_file = ""
    completed = 0
    target = 0

    def __init__(self):
        self.files = os.listdir('media/to_chino')
        progfile = [x for x in self.files if "progress" in x]
        progfile = progfile[0] if len(progfile) > 0 else ""

        if progfile != "":
            self.has_existing = True
            with open('media/to_chino/{}'.format(progfile)) as pr:
                prog_obj = json.load(pr)
                self.completed = prog_obj['completed']
                self.target = prog_obj['total']

        if self.has_existing:
            xl_file = [x for x in self.files if '.xlsx' in x]
            self.xl_file = xl_file[0] if len(xl_file) > 0 else ""

            json_file = [x for x in self.files if '.json' in x and 'progress' not in x]
            self.json_file = json_file[0] if len(json_file) > 0 else ""




























