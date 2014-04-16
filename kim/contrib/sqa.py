from ..serializers import Serializer


def mapping_get(m, n):
    for tm in m:
        if tm.source == n:
            return tm

def marshal_sqa(serializer, instance, result):
    for k, v in result.iteritems():
        if type(v) == dict:
            # nested alert
            nested_typemapper = mapping_get(serializer.__mapping__, k)
            nested_serializer = nested_typemapper.base_type.original_mapping()
            exiting = getattr(instance, k)
            if exiting:
                marshal_sqa(nested_serializer, existing, v)
            else:
                new = nested_serializer.get_model()()
                marshal_sqa(nested_serializer, new, v)
                import ipdb; ipdb.set_trace()
        else:
            setattr(instance, k, v)

class SQASerializer(Serializer):
    def __init__(self, instance=None, input=None, **kwargs):
        super(SQASerializer, self).__init__(data=instance, input=input, **kwargs)

    def serialize(self, **kwargs):
        return super(SQASerializer, self).serialize(**kwargs)

    def get_model(self):
        return self.__model__

    def get_model_or_instance(self):
        return self.source_data or self.get_model()()

    def marshal(self, **kwargs):
        result_dict = super(SQASerializer, self).marshal(**kwargs)
        instance = self.get_model_or_instance()
        marshal_sqa(self, instance, result_dict)
        return instance
