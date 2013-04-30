# nrcif_fields.py

'''nrcif_fields - Definition of the CIF format fields

This module defines the field types found in most National Rail CIF format files
containing UK rail timetable data.'''

import datetime

class CIFField(object):
    '''A base class for fields in a record of a fixed-format CIF file'''

    sql_type = None
    py_type = None

    def __init__(self, name, width):
        self.name = name
        self.width = width

    @classmethod
    def read(cls, text):
        '''Convert the text of a field into the appropriate Python type'''
        return cls.py_type(text)

class TextField(CIFField):
    '''Represents a CIF field simply stored as text'''

    py_type = str

    def __init__(self, name, width):
        self.name = name
        self.width = width
        self.sql_type = "CHAR({})".format(width)


class IntegerField(CIFField):
    '''Represents a CIF field simply stored as an integer'''

    sql_type = "INTEGER"
    py_type = int

class EnforceField(CIFField):
    '''Represents a CIF field that must match a template exactly'''

    sql_type = None
    py_type = None

    def __init__(self, name, template):
        self.name = name
        self.width = len(template)
        self.template = template

    def read(self, text):
        if text != self.template:
            raise ValueError("{} does not match required field {}".format(text, self.template))
        return None

class SpareField(CIFField):
    '''Represents a reserved or unused field in a CIF record'''

    sql_type = None
    py_type = None

    @classmethod
    def read(cls, text):
        return None

class FlagField(CIFField):
    '''Represents a 1-char wide CIF field that must be one of a set of flags'''

    sql_type = "CHAR(1)"
    py_type = str

    def __init__(self, name, flags):
        self.name = name
        self.width = 1
        self.flags = flags

    def read(self, text):
        if len(text) != 1 or not (text in self.flags):
            raise ValueError("'{}' is not one of the allowed flags '{}' for field '{}'".format(text, self.flags, self.name))
        return text

class TimeField(CIFField):
    '''Represents a time in HHMM format'''

    sql_type = "TIME WITHOUT TIME ZONE"
    py_type = datetime.time

    def __init__(self, name):
        self.name = name
        self.width = 4

    @classmethod
    def read(cls, text):
        if len(text)!= 4 or not text.isdecimal():
            raise ValueError(text + " is not a 4-digit HHMM time")

        h, m = int(text[0:2]), int(text[2:4])
        return datetime.time(hour = h, minute = m)

class TimeHField(CIFField):
    '''Represents a time in HHMM format with optional additional H for a half-minute'''

    sql_type = "TIME WITHOUT TIME ZONE"
    py_type = datetime.time

    def __init__(self, name):
        self.name = name
        self.width = 5

    @classmethod
    def read(cls, text):
        if len(text)!= 5 or not text[0:4].isdecimal():
            raise ValueError(text + " is not a 5-digit HHMM time with optional H")

        h, m = int(text[0:2]), int(text[2:4])
        if text[4] == 'H':
            return datetime.time(hour = h, minute = m, second = 30)
        else:
            return datetime.time(hour = h, minute = m, second = 0)

class DDMMYYDateField(CIFField):
    '''Represents a date in the DDMMYY format with Y2K munging'''

    sql_type = "DATE"
    py_type = datetime.date

    def __init__(self, name):
        self.name = name
        self.width = 6

    @classmethod
    def read(cls, text):
        if len(text)!= 6 or not text.isdecimal():
            raise ValueError(text + " is not a 6-digit DDMMYY date")
        if text == "999999":
            return datetime.date.max
        d, m, y = int(text[0:2]), int(text[2:4]), int(text[4:6])
        if y >= 60:
            y += 1900
        else:
            y += 2000
        return datetime.date(y, m, d)

class YYMMDDDateField(CIFField):
    '''Represents a date in the YYMMDD format with Y2K munging'''

    sql_type = "DATE"
    py_type = datetime.date

    def __init__(self, name):
        self.name = name
        self.width = 6

    @classmethod
    def read(cls, text):
        if len(text)!= 6 or not text.isdecimal():
            raise ValueError(text + " is not a 6-digit YYMMDD date")
        if text == "999999":
            return datetime.date.max
        y, m, d = int(text[0:2]), int(text[2:4]), int(text[4:6])
        if y >= 60:
            y += 1900
        else:
            y += 2000
        return datetime.date(y, m, d)

class DaysField(CIFField):
    '''Represents the Days Run field, giving the days a train runs'''

    sql_type = "BOOLEAN ARRAY[7]"
    py_type = list

    def __init__(self, name):
        self.name = name
        self.width = 7

    @classmethod
    def read(cls, text):
        if len(text)!= 7 or not text.isdecimal():
            raise ValueError(text + " is not a 7-digit 'days run' field")
        result = []
        for i in text:
            if i == '1':
                result.append(True)
            elif i == '0':
                result.append(False)
            else:
                raise ValueError(text + " contains values other than 1 and 0")
        return result

class ActivityField(CIFField):
    '''Represents the Activity field, showing what things happen at a stop'''

    sql_type = "CHARACTER(2) ARRAY[6]"
    py_type = list

    def __init__(self, name):
        self.name = name
        self.width = 12

    @classmethod
    def read(cls, text):
        if len(text)!= 12:
            raise ValueError(text + " is not a 12 char Activity field")
        result = []
        for i in range(0,12,2):
            result.append(text[i:i+2])
        return result