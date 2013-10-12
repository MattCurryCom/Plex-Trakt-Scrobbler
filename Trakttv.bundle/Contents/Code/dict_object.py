class DictObject(object):
    root_key = None

    def __init__(self, key):
        self.key = key

    def save(self):
        if not self.root_key:
            raise ValueError()

        Dict[self.root_key][self.key] = self.to_json()

    @classmethod
    def load(cls, key):
        if not cls.root_key:
            raise ValueError()

        if key not in Dict[cls.root_key]:
            return None

        return cls.from_json(Dict[cls.root_key][key])

    def delete(self):
        if not self.root_key:
            raise ValueError()

        if self.key in Dict[self.root_key]:
            del Dict[self.root_key][self.key]


    @classmethod
    def object_from_json(cls, key, value):
        raise NotImplementedError()

    @classmethod
    def from_json(cls, data):
        obj = cls()

        for key, value in data.items():
            #Log('[DataObject.from_json] "%s" = %s' % (key, value))

            if not hasattr(obj, key):
                continue

            if isinstance(value, dict):
                value = cls.object_from_json(key, value)

            setattr(obj, key, value)

        return obj

    def to_json(self):
        data = {}

        items = [
            (key, value)
            for (key, value) in getattr(self, '__dict__').items()
            if not key.startswith('_')
        ]

        for key, value in items:
            if isinstance(value, DictObject):
                value = value.to_json()

            data[key] = value

        return data
