class RawTherapeeDefaults:
    def __init__(self):
        template_file = open('/home/willem/PycharmProjects/DeepLearningWithPythonMEAP/generiekeFuncties/rawtherapeeTemplate.pp3')
        self.template = template_file.read()
        template_file.close()

    def maak_specifiek(self, f_naam, size):
        breedte, hoogte = size
        factor = 16 / 9
        if breedte > hoogte * factor:
            breedte = hoogte * factor
        else:
            hoogte = int(breedte / factor)
        inhoud_pp3 = self.template.replace("teVervangenBreedte",
                                  str(breedte)).replace("teVervangenHoogte",
                                                        str(hoogte))
        pp3_file_naam = f_naam + ".pp3"
        pp3_file = open(pp3_file_naam, "w")
        pp3_file.write(inhoud_pp3)