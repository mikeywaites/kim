from ..types import String, Integer, Nested, Collection, Date
from ..serializers import Serializer, Field


class InnerNestedSerializer(Serializer):
    e = Field(String)
