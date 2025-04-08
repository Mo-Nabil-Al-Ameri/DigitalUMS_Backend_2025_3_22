from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class OrderField(models.PositiveIntegerField):
    """OrderField is an extension of the PositiveIntegerField that allows us to
         specify a field to order by.
    """
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def  pre_save(self,model_instance,add):
        if getattr(model_instance, self.attname) is None:
            # No current value
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # Filter by objects with the same field values
                    # for the fields in `for_fields`
                    query= {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                # Get the order of the last item
                latest_item =qs.latest(self.attname)
                value = getattr(latest_item,self.attname) + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance,self.attname,value)
            return value
        else:
            super().pre_save(model_instance,add)