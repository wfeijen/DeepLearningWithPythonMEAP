from datetime import datetime
import sys


def geeft_voortgangs_informatie(meldingsText, tijden):
    (start_tijd, tijdVorigePunt) = tijden
    nu = datetime.now()
    print("tijd: ", str(nu), " - sinds start: ", str(nu - start_tijd), " sinds vorige: ", str(nu - tijdVorigePunt),
          " - ", meldingsText)
    return start_tijd, nu


def initializeer_voortgangs_informatie(meldingstext):
    start_tijd = datetime.now()
    tijd_vorige_punt = start_tijd
    geeft_voortgangs_informatie(meldingstext, (start_tijd, tijd_vorige_punt))
    return start_tijd, start_tijd


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size
