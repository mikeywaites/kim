from kim.exceptions import ValidationError, MappingErrors


class Visitor(object):
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def visit(self, type, data):
        name = 'visit_%s' % type.__visit_name__
        return getattr(self, name)(type, data)

    def run(self):
       self.output = {}
       for field in self.mapping:
           data = self.get_data(field)
           result = self.visit(field.field_type, data)
           self.update_output(field, result)
       return self.output


class SerializeVisitor(Visitor):
    def get_data(self, field):
        return self.data[field.source]

    def update_output(self, field, result):
        self.output[field.name] = result

    def visit_default(self, type, data):
         return type.serialize_value(data)

    def visit_nested(self, type, data):
        return SerializeVisitor(type.mapping, data).run()

    def visit_collection(self, type, data):
        result = []
        for value in data:
            value = self.visit(type.inner_type, value)
            result.append(value)
        return result


def serialize(mapping, data):
    return SerializeVisitor(mapping, data).run()


class MarshalVisitor(Visitor):
    def __init__(self, *args, **kwargs):
        super(MarshalVisitor, self).__init__(*args, **kwargs)
        self.errors = {}

    def get_data(self, field):
        data = self.data[field.name]
        try:
            if field.is_valid(data):
                return data
        except ValidationError as e:
            self.errors[field.name] = e.message

    def update_output(self, field, result):
        self.output[field.source] = result

    def visit_default(self, type, data):
         return type.marshal_value(data)

    def visit_nested(self, type, data):
        return MarshalVisitor(type.mapping, data).run()

    def visit_collection(self, type, data):
        result = []
        for value in data:
            value = self.visit(type.inner_type, value)
            result.append(value)
        return result

    def run(self):
        output = super(MarshalVisitor, self).run()
        if self.errors:
            raise MappingErrors(self.errors)
        else:
            return output

def marshal(mapping, data):
    return MarshalVisitor(mapping, data).run()