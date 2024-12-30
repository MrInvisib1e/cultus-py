from enum import IntEnum

class TextType(IntEnum):
    System = 0
    Error = 20 #yes
    Dictionary = 40
    NextBirthday = 50
    NextBirthdayMulti = 51
    NoBirthdays = 52
    NextBirthdayError = 55 #yes
    SaveBirthday = 60 #yes
    SavedBirthday = 61 #yes
    SaveBirthdayError = 65 #yes
    DeleteBirthday = 70 #yes
    ScheduledOneBirthday = 80
    ScheduledMultiBirthdays = 81
    NoScheduledBirthdays = 82
    BirthdayToday = 90 #yes
    MultiBirthdayToday = 91 #yes
    ListOfBirthdays = 100 #yes
    Prophecy = 110
    Prophecy8Ball = 120
    JoinCongratulation = 130
    Rules = 140
    DracoWait = 150 #yes
    DracoCalc = 151 #yes
    DracoError = 155