class Export:
    def __init__(self, this=None):
        self.this = this

    def Export_Treatments(self):
        treatments = self.this.query.all()
        results = []
        for treatment in treatments:
            type_name = getattr(treatment.types, 'type', '') 
            treatment_name = getattr(treatment, 'treatment', '')
            benefit = getattr(treatment, 'benefit', '')
            skin = getattr(treatment, 'skin', '')
            information = getattr(treatment, 'information', '')
            data = [type_name, treatment_name, benefit, skin, information]
            results.append(data)
        return results