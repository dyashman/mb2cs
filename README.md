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
