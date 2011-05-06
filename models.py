from google.appengine.ext import db

class TruthNode(db.Model):
    content = db.TextProperty()
    create_date = db.DateProperty()
    edit_date = db.DateProperty()
    
class NodeRelationship(db.Model):
    parent_node = db.ReferenceProperty(TruthNode,
        collection_name="noderelationship_parent_set")
    child_node = db.ReferenceProperty(TruthNode,
        collection_name="noderelationship_child_set")
    # child's relationship to parent
    relationship = db.StringProperty(required=True, choices=set(['Pro', 'Con']))
