from enum import IntEnum

class TextType(IntEnum):
    System = 0
    Dictionary = 10
    NextBirthday = 20
    NextBirthdayMulti = 21
    NextBirthdayError = 25
    SaveBirthday = 30
    SavedBirthday = 31
    SaveBirthdayError = 35
    DeleteBirthday = 40
    ScheduledOneBirthday = 50
    ScheduledMultiBirthdays = 60
    BirthdayToday = 70
    ListOfBirthdays = 80
    Prophecy = 90
    Prophecy8Ball = 100
    Error = 110