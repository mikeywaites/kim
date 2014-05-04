from ..serializers import Serializer


class DjangoSerializer(Serializer):
    pass
    # def serialize(self, data, **kwargs):
    #     return super(SQASerializer, self).serialize(data, **kwargs)

    # def get_model(self):
    #     return self.__model__()

    # def get_new_model(self):
    #     return self.get_model()

    # def marshal(self, data, instance=None, **kwargs):
    #     result_dict = super(SQASerializer, self).marshal(data, **kwargs)
    #     model_instance = instance or self.get_model()
    #     marshal_sqa(model_instance, result_dict)
    #     return model_instance
