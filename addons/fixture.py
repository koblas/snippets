import yaml

def load_data(mapping):
    print mapping

    with open("initial_data.yaml") as fd:
        data = yaml.load(fd.read())

        for item in data:
            if 'fields' not in item:
                continue

            model = item['model']

            cls = mapping.get(model)
            if not cls:
                continue

            fields = item['fields']
            obj = cls(**fields)
            obj.save()
