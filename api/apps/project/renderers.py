from api.apps.core.renderers import BaseJSONRenderer

class ProjectJSONRenderer(BaseJSONRenderer):
    object_label = 'project'
    pagination_object_label = 'projects'
    pagination_count_label = 'projectCount'
