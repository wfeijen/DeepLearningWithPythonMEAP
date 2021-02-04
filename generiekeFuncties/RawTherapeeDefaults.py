import os
class RawTherapeeDefaults:
    def __init__(self, file_format):
        if file_format == '.jpg':
            template_pad = os.path.expanduser('~/PycharmProjects/DeepLearningWithPythonMEAP/generiekeFuncties/rawtherapeeJPGtemplate.pp3')
        else:
            template_pad = os.path.expanduser('~/PycharmProjects/DeepLearningWithPythonMEAP/generiekeFuncties/rawtherapeeNEFtemplate.pp3')
        template_file = open(template_pad)
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