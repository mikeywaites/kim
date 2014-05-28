from ..types import String, Integer, Nested, Collection, Date
from ..serializers import Serializer, Field
from ..exceptions import ValidationError


class MySerializer(Serializer):
    a = Field(Integer)

    def validate_a(self, value):
        if value != 420:
            raise ValidationError('need to chill out more')
        return True


print MySerializer().marshal({"a": 420})
print MySerializer().marshal({"a": 50})