from datetime import datetime

def geeftVoortgangsInformatie(meldingsText, startTijd, tijdVorigePunt):
    nu = datetime.now()
    print("tijd: ", str(nu), " - sinds start: ", str(nu - startTijd), " sinds vorige: ", str(nu - tijdVorigePunt),
          " - ", meldingsText)
    return nu

def initializeerVoortgangsInformatie():
    startTijd = datetime.now()
    tijdVorigePunt = startTijd
    geeftVoortgangsInformatie("Start", startTijd, tijdVorigePunt)
    return startTijd, startTijd

def verwijderGecontroleerdeFiles(fileList):
    antwoord = []
    for file in fileList:
        if len(file)<-18:
            antwoord.append(file)
        elif file[-18:] != "_gecontroleerd.jpg":
            antwoord.append(file)
    return antwoord