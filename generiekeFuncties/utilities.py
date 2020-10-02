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

def checkGecontroleerd(str_in):
    return "gecontroleerd" in str_in

def verwijderGecontroleerdeFilesFromList(fileList):
    antwoord = []
    for file in fileList:
        if not checkGecontroleerd(file):
            antwoord.append(file)
    return antwoord

def combine_lists(a, b):
    c = []
    c.extend(a)
    c.extend(b)
    return c