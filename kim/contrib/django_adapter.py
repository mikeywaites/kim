from ..serializers import Serializer
from django.core.exceptions import ObjectDoesNotExist

def marshal_django(instance, result):
    for k, v in result.iteritems():
        if type(v) == dict:
            # This is a nested serializer

            # First check if the relationship already exists
            try:
                existing = getattr(instance, k)
            except ObjectDoesNotExist:
                existing = None

            if existing:
                # Exists, just update it
                marshal_django(existing, v)
            else:
                # If it doesn't exist, we need to create it

                # Find what sort of model we require by introspection of
                # the relationship
                RemoteClass = instance._meta.get_field(k).rel.to

                # Now create a new instance of that model and set the relationship
                remote_instance = RemoteClass()
                setattr(instance, k, remote_instance)
                marshal_django(remote_instance, v)
        else:
            # This is a normal field, just update it on the model instance
            setattr(instance, k, v)

class DjangoSerializer(Serializer):
    def get_model(self):
        return self.__model__()

    def get_new_model(self):
        return self.get_model()

    def marshal(self, data, instance=None, **kwargs):
        result_dict = super(DjangoSerializer, self).marshal(data, **kwargs)
        model_instance = instance or self.get_model()
        marshal_django(model_instance, result_dict)
        return model_instance
