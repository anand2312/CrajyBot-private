import json
horoscopes=[
    {
        "day_low" : 80,
        "day_high" : 110,
        "Zodiac" : "Aries",

    },
    {
        "day_low" : 111,
        "day_high" : 141,
        "Zodiac" : "Taurus",

    },
    {
        "day_low" : 142,
        "day_high" : 172,
        "Zodiac" : "Gemini",

    },
    {
        "day_low" : 173,
        "day_high" : 204,
        "Zodiac" : "Cancer",

    },
    {
        "day_low" : 205,
        "day_high" : 235,
        "Zodiac" : "Leo",

    },
    {
        "day_low" : 236,
        "day_high" : 266,
        "Zodiac" : "Virgo",

    },
    {
        "day_low" : 267,
        "day_high" : 296,
        "Zodiac" : "Libra",

    },
    {
        "day_low" : 297,
        "day_high" : 326,
        "Zodiac" : "Scorpio",

    },
        
    {
        "day_low" : 327,
        "day_high" : 356,
        "Zodiac" : "Sagittarius",

    },
    {
        "day_low" : 357,
        "day_high" : 385,
        "Zodiac" : "Capricorn",


    },
    {
        "day_low" : 20,
        "day_high" : 49,
        "Zodiac" : "Aquarius",

    },
    {
        "day_low" : 50,
        "day_high" : 79,
        "Zodiac" : "Pisces",

    }
    
]

with open("horo-data.json","w+") as data:
    json.dump(horoscopes,data)