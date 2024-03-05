# mb2cs.py
Convert a Manabox csv export into one importable by Cardsphere.

There are lots of missing pieces still, but this covers many of the main issues:
- Booster Fun treatments (Showcase, Borderless, Extended, etc)
- Lands (Cardsphere typically adds the collector number to the name to differentiate them)
- List cards
- Several Commander sets that use different set namings
- Most split/mdfc cards

There are two csv files included for lookups you can add to if you find additional cards not covered.
- names.csv contains set code + collector number lookups to override card name + edition
- editions.csv contains set code + collector number ranges to override editions (mostly for Booster Fun)

As an example, with my collection of 25,319 cards, a direct import into Cardsphere gives:
```
From 13282 entries 11816 unique cards were added (21635 total). 1000 or more entries could not be matched
```

After running it through mb2cs:
```
From 12840 entries 12788 unique cards were added (23894 total). 52 entries could not be matched.
```

Not perfect yet, but that also doesn't count all the cards that imported successfully as the wrong card.

# Requirements

Manabox csv exported from the Manabox App - https://www.manabox.app/

Cardsphere account to import your list of Haves to - https://www.cardsphere.com/
- If you'd like to sign up, feel free to use my referral link: https://www.cardsphere.com/ref/47027/7092e8

# Parameters

Invoke the script with the name of the csv file to convert.

Input file isn't overwritten, a new file 'cardsphere.csv' is written in the Cardsphere format for you to upload.

```
$ python mb2cs.py manaboxfile.csv
```

# Example
```
> python mb2cs.py All_Cards.csv
Hit 100 Multiverse Bridge lookups, sleeping 60s to avoid throttling.
...resuming
Hit 100 Multiverse Bridge lookups, sleeping 60s to avoid throttling.
...resuming
Done
```

# Known Issues / Limitations
There's still a lot to do - the main areas that have issues are:
- Various Promos
- Unfinity Attractions
- Tokens
- Old cards with alt art (Homelands/Fallen Empires/etc)
- Some lands and mdfc/split cards that are inconsistent on Cardsphere