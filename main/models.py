from django.db import models
from richtext.fields import AdminRichTextField

class TruthNode(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    content = AdminRichTextField(max_length=20000, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title
    
class NodeRelationship(models.Model):
    PRO, CON, PREMISE = range(3)
    RELATIONSHIP_CHOICES = (
        (PRO, u'Pro'),
        (CON, u'Con'),
        (PREMISE, u'Premise'),
    )
    parent_node = models.ForeignKey(TruthNode,
        related_name="noderelationship_parent_set")
    child_node = models.ForeignKey(TruthNode,
        related_name="noderelationship_child_set")
    # child's relationship to parent
    relationship = models.IntegerField(choices=RELATIONSHIP_CHOICES)

