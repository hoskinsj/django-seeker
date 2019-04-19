class FieldOptions(object):

    def __init__(self, field_id, suffix='', label=None, facet_class=None,
                 display=True, sort_order=None, initial=None,
                 column_sortable=False, column_sorted=True, facet_kwargs=None, highlight=False,
                 template=None, column=None, required_display_insertion_index=None,
                 exclude=False, searchable=True, custom_column_header=None, value_formatter=None,
                 definition=None):
        
        if facet_kwargs is None:
            facet_kwargs = {}
        
        # The id of the field, required.
        self.field_id = field_id
        # Human readable name
        self.label = label
        # Name that appears on the column
        self.custom_column_header = custom_column_header
        # Custom definition displayed in the header
        self.definition = definition
        # ES suffix
        self.suffix = suffix
        # Whether or not to display the field
        self.display = display
        # Initial values
        self.initial = initial
        # Horizontal sort order, between columns
        self.sort_order = sort_order
        # Whether or not the column should be sortable.
        self.column_sortable = column_sortable
        # Whether or not the column should be initially sorted.
        self.column_sorted = column_sorted
        # Whether or not the field should be searchable by
        self.searchable = searchable
        
        # Facet information, arguments necessary for instantiation
        self.facet_class = facet_class
        self.facet_kwargs = {}
        if self.label:
            self.facet_kwargs['label'] = self.label
        self.facet_kwargs.update(facet_kwargs)
        
        # Custom column
        self.column = column
        # Whether or not to highlight the field
        self.highlight = highlight
        # Custom field template
        self.template = template
        # Index at which to insert the required field
        self.required_display_insertion_index = required_display_insertion_index
        # Exclude from the page
        self.exclude = exclude
        # Value format
        self.value_formatter = value_formatter

    def initialize_facet(self):
        if self.facet_class:
            return self.facet_class(self.extended_field_id, **self.facet_kwargs)
        return None

    @property
    def extended_field_id(self):
        return self.field_id + self.suffix


class SeekerConfiguration(object):
    def __init__(self, field_options):
        self.field_options = field_options

    def extract_settings(self):
        options = self.field_options
        settings = {
            'display': [option.field_id for option in sorted(options, key=lambda option: option.sort_order) if option.display],
            'facets': [option.initialize_facet() for option in options if option.facet_class],
            'sort_fields': {option.field_id: option.extended_field_id for option in options if option.column_sortable},
            'initial_facets': {option.extended_field_id : option.initial for option in options if option.initial is not None},
            'field_columns': {option.field_id : option.column for option in options if option.column},
            'required_display': [(option.field_id, option.required_display_insertion_index) for option in options
                if option.required_display_insertion_index is not None],
            'exclude': [option.field_id for option in options if option.exclude],
            'field_columns': {option.field_id : option.column for option in options if option.column},
            'field_labels': {option.field_id : option.label for option in options if option.label},
            'highlight_fields': {option.field_id: option.extended_field_id for option in options if option.highlight},
            'field_templates': {option.template for option in options if option.template},
            'search': [option.field_id for option in options if option.searchable],
            #'sort': [option.field_id for option in options if option.column_sorted],
            'custom_column_headers': {option.field_id : option.custom_column_header for option in options if option.custom_column_header is not None},
            'field_definitions': {option.field_id: option.definition for option in options if option.definition is not None}
        }
        return settings

class AdvancedSeekerConfiguration(SeekerConfiguration):
    def extract_settings(self):
        settings = super(AdvancedSeekerConfiguration, self).extract_settings()
        settings['value_formats'] = {option.field_id : option.value_formatter for option in self.field_options if option.value_formatter}
        return settings

class FieldApi(type):

    def __new__(cls, clsname, bases, clsdict):
        if 'config' in clsdict:
            clsdict.update(clsdict['config'].extract_settings())
        return super(FieldApi, cls).__new__(cls, clsname, bases, clsdict)