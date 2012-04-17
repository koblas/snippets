class Page(object):
    def __init__(self, number, paginator):
        self.paginator = paginator
        self.number    = number

    def __iter__(self):
        for o in self.paginator.objects[self.start_index():self.end_index()]:
            yield o

    def has_next(self):
        return self.number <= self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def start_index(self):
        return (self.number - 1) * self.paginator.per_page

    def end_index(self):
        return (self.number * self.paginator.per_page) - 1

    @property
    def per_page(self):
        return self.paginator.per_page

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1

    @property
    def object_list(self):
        for o in self.paginator.objects[self.start_index():self.end_index()+1]:
            yield o

class Paginator(object):
    """Paginator for mongo objects"""

    def __init__(self, objs, per_page=10):
        self.count = len(objs)
        self.objects  = objs
        self.per_page = per_page
        self.num_pages = self.count / self.per_page

    def page(self, idx):
        """Return a Page object with the given 1 based index"""
        return Page(idx, self)
