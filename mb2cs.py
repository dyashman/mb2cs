#!/usr/bin/env python

"""
Python script to convert a Manabox csv export into one importable by Cardsphere.

MIT License

Copyright (c) 2024 David Ashman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import csv
import json
import time
import re
import unicodedata
import urllib.request

languages = {"en":"English","ja":"Japanese","ru":"Russian","ko":"Korean","it":"Italian"}

if len(sys.argv) == 1:
    print("Syntax: mb2cs.py <manabox_export_file.csv>")
    exit()

infile = sys.argv[1]

cs = open('cardsphere.csv', 'w')
err = open('error.log', 'w')

# Expected Cardsphere CSV import fields
cs.write("Count,Tradelist Count,Name,Edition,Condition,Language,Foil,Tags\n")

# Names and Editions that are different between Manabox and Cardsphere have csv files with mappings.
#   names.csv contains a list of set code+collector number to explicity set a card's name.
#   editions.csv contains a list of set code+collector number range to explicity set a card's edition.
#     Most of these are for all the various Booster Fun treatments.
names = {}
with open('names.csv', "r") as file:
    data = csv.reader(file)
    for row in data:
        if not row[0] in names:
            names[row[0]] = []
        names[row[0]] += ([[row[1],row[2],row[3]]])
editions = {}
with open('editions.csv', "r") as file:
    data = csv.reader(file)
    for row in data:
        if not row[0] in editions:
            editions[row[0]] = []
        editions[row[0]] += ([[row[1],row[2],row[3]]])

with open(infile, "r", encoding="utf-8") as file:
    data = csv.reader(file)
    next(data, None)
    row = 0
    mvbcount = 0;
    for mb in data:
        row = row + 1

        # ManaBox CSV export format:
        # Name,Set code,Set name,Collector number,Foil,Rarity,Quantity,ManaBox ID,Scryfall ID,Purchase price,Misprint,Altered,Condition,Language,Purchase price currency
        # TODO: check other app/site exports and see if it's easy to read the header to determine format and create a mapping for each
        name = mb[0]
        setcode = mb[1]
        edition = mb[2]
        collectornumber = mb[3]
        foil = "normal" if mb[4] == "normal" else "foil"
        count = mb[6]
        scryfallid = mb[8]
        condition = mb[12]
        language = languages[mb[13]]

        # Convert unicode letters to ascii
        name = unicodedata.normalize('NFKD', mb[0]).encode('ascii','ignore').decode('ascii')

        # Sets with different names on Manabox vs Cardsphere
        set_replace = {
            "The List (Unfinity Foil Edition)":"The List - Unfinity",
            "30th Anniversary Play Promos":"30th Anniversary Promos",
            "Kaldheim Commander":"Kaldheim Commander Decks",
            "Forgotten Realms Commander":"Adventures in the Forgotten Realms Commander Decks",
            "Midnight Hunt Commander":"Innistrad: Midnight Hunt Commander Decks",
            "Crimson Vow Commander":"Innistrad: Crimson Vow Commander Decks",
            "Neon Dynasty Commander":"Kamigawa: Neon Dynasty Commander Decks",
            "New Capenna Commander":"Streets of New Capenna Commander",
            "The Brothers' War Retro Artifacts":"The Brothers' War - Retro Artifacts",
            "Multiverse Legends":"March of the Machine - Multiverse Legends",
            "Tales of Middle-earth Commander":"Lord of the Rings: Tales of Middle-earth - Commander",
            "The Lost Caverns of Ixalan Commander":"The Lost Caverns of Ixalan - Commander",
            "Secret Lair Drop":"Secret Lair Drop Series",
            "DCI Promos":"WPN and Gateway Promos",
            "Duels of the Planeswalkers 2015 Promos":"Duels of the Planeswalkers Game Promos",
            "Love Your LGS":"Love Your Local Game Store Promos",
            "Legends Italian":"Legends" 
        }
        if edition in set_replace.keys():
            edition = set_replace[edition]
        if "Convention Promo" in edition:
            edition = "Convention"
        if "Friday Night Magic" in edition:
            edition = "FNM Promos"
        if "Wizards Play Network" in edition:
            # TODO: Some of these are "WPN and Gateway Promos", others are "Miscellaneous Promos", possibly more?
            edition = "Miscellaneous Promos"
        # Sets with very minor variations
        if "Theros Beyond Death" in edition:
            edition = edition.replace("Theros Beyond Death","Theros: Beyond Death")
        if "The Lord of the Rings" in edition:
            edition = edition.replace("The Lord of the Rings","Lord of the Rings")

        # Multiverse Bridge lookup for List cards and some cards with a/b/c/etc versions in Manabox
        if "-" in collectornumber or setcode == "PLST" or edition == "The List" or collectornumber[len(collectornumber)-1] in "abcdef":
            mvbcount = mvbcount + 1
            mvb_json = urllib.request.urlopen("https://www.multiversebridge.com/api/v1/cards/scryfall/"+scryfallid).read()
            mvb_array = json.loads(mvb_json)

            if len(mvb_array) > 0:
                # Not sure if we even need to set the name from MVB at all, but seems like Scryfall strips split cards?
                if not "//" in name:
                    name = mvb_array[0]["name"]
                edition = mvb_array[0]["edition"]
                collectornumber = mvb_array[0]["collector_number"]
                if "-" in collectornumber:
                    setcode = setcode[:3]
            else:
                err.write("MVB lookup FAILED - Line #"+str(row)+": "+name+" - "+edition+" - "+scryfallid+"\n")
            if mvbcount % 100 == 0:
                print("Hit 100 Multiverse Bridge lookups, sleeping 60s to avoid throttling.")
                time.sleep(60)
                print("...resuming")

        # Lookups for special cards like promos and old foils that either use "P[SET]" or a letter after the collector number
        if not collectornumber.isnumeric():
            lastchar = collectornumber[len(collectornumber)-1]
            if setcode[0] == "P" or lastchar == "★":
                if lastchar == "p": # Most LGS promo packs use this naming for the planeswalker stamped cards
                    collectornumber = collectornumber[0:len(collectornumber)-1]
                    edition = edition.replace(" Promos","")
                    edition += " - Promo Pack"
                elif lastchar == "s": # These should be the year-stamped cards in prerelease kits
                    collectornumber = collectornumber[0:len(collectornumber)-1]
                    edition = edition.replace(" Promos","")
                    edition += " - Prerelease Promos"
                elif lastchar == "★": # Some old foils use a star after their number
                    collectornumber = collectornumber[0:len(collectornumber)-1]
                elif lastchar == "F": # 30th Anniversary 'F'estival cards
                    collectornumber = collectornumber[0:len(collectornumber)-1]
                    edition = "30th Anniversary"
                elif collectornumber[0] == "A" and not "-" in collectornumber: # Think these are all resale promos
                    collectornumber = collectornumber[1:]
                else:
                    err.write("Unknown promo with set code: '"+collectornumber+"' for "+name+"\n")
                    continue
                setcode = setcode[1:]
            elif lastchar in "abcdef":
                if setcode == "BFZ":
                    collectornumber = collectornumber[0:len(collectornumber)-1]
                    name += " (Full Art)"
                elif setcode == "UNF":
                    # TODO: Attractions
                    err.write("Unfinity Attractions not supported yet: ["+setcode+"] "+name)
                    continue
                elif setcode in {"FEM","HML","ALL","CHR"}:
                    err.write("Alternate art old cards not supported yet: ["+setcode+"] "+name)
                    # TODO: Fallen Empires, Homelands, Alliances, Chronicles variants
                    continue
                else:
                    err.write("Unknown promo with set code: '"+collectornumber+"' for "+name+"\n")
                    continue
            else:
                err.write("Unknown promo with set code: '"+collectornumber+"' for "+name+"\n")
                continue
        elif setcode[0] == "P":
            edition = edition.replace(" Promos","")
            collectornumber = re.sub("[^0-9]","",collectornumber)

        # Process list of cards with different names, mostly lands
        #   Old sets have A/B/C versions
        #   Newer sets use collector numbers in their names to differentiate them
        if name.lower() in ["plains","island","swamp","mountain","forest","wastes"]:
            # Sets with only 1 version don't use the collector number
            if setcode not in {"BBD","IXL","RIX","RNA","GRN","UNF","REX","UNH","UNG"}:
                if int(collectornumber) < 100 and setcode not in {"UND","JMP"}:
                    collectornumber = "0"+collectornumber
                if not (collectornumber == "262" and name == "Plains"):
                    name += " (#"+collectornumber+")"
        # Other sets with collector numbers in names
        if (name in {"Command Tower","Sonic Screwdriver"} and setcode == "WHO") or \
                (name in {"Arcane Signet","Mind Stone","Command Tower","Commander's Sphere","Sol Ring","Talisman of Dominance","Wayfarer's Bauble"} and setcode == "40K") or \
                ("Guildgate" in name and setcode == "GRN") or \
                ("Snow-Covered" in name and setcode == "KHM") or \
                (name == "Sol Ring" and setcode == "LTC"):
            name += " (#"+collectornumber+")"

        # Check for MDFCs/Split/Adventure/etc
        # According to the Discord, the end goal is to only use the // for split cards, and to
        #   only use the front/primary name on adventures/mdfcs. Until then, only newer cards
        #   strip off the second name. This will also likely be an issue if sets do both MDFCs
        #   alongside split cards.
        if "//" in name and setcode in {"DKA","SOI","XLN","BOT","NEO","AFC","VOW","MID","DBL","CLB","MOM","MOC","CMM","WOE","WOC","WHO","LCI","LCC"}:
            name = name.split("//")[0].strip()
        # Strip double quotes
        name = name.replace("\"","")
        # Unfinity fill-in-the-blanks are different sizes
        if "_____" in name:
            name = name.replace("_____","________")

        # Check if card is explicitly overridden in names.csv
        if setcode in names.keys():
            for cn in names[setcode]:
                if collectornumber == cn[0]:
                    name = cn[1]
                    edition = cn[2]

        # Edition lookup for booster fun treatments
        # Replacement lookup based on set code and collector number loaded from editions.csv file
        if setcode in editions.keys():
            for ed in editions[setcode]:
                if int(collectornumber) >= int(ed[0]) and int(collectornumber) <= int(ed[1]):
                    edition = ed[2]

        # TODO: Tokens
        if not "Token" in name and not "Tokens" in edition and not "Unfinity Sticker Sheets" in edition:
            cs.write(count+","+count+",\""+name+"\",\""+edition+"\",\"Near Mint\",\""+language+"\","+foil+",\"\"\n")

print("Done")