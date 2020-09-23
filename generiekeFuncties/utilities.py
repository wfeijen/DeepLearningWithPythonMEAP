from datetime import datetime

def geeftVoortgangsInformatie(meldingsText, tijden):
    (startTijd, tijdVorigePunt) = tijden
    nu = datetime.now()
    print("tijd: ", str(nu), " - sinds start: ", str(nu - startTijd), " sinds vorige: ", str(nu - tijdVorigePunt),
          " - ", meldingsText)
    return (startTijd, nu)

def initializeerVoortgangsInformatie(meldingsText):
    startTijd = datetime.now()
    tijdVorigePunt = startTijd
    geeftVoortgangsInformatie(meldingsText, (startTijd, tijdVorigePunt))
    return (startTijd, startTijd)

def verwijderGecontroleerdeFiles(fileList):
    antwoord = []
    for file in fileList:
        if len(file)<-18:
            antwoord.append(file)
        elif file[-18:] != "_gecontroleerd.jpg":
            antwoord.append(file)
    return antwoord