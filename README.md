# Rentals Archetypes

Types, monikers and badges for short-term rental listings, hosts and markets: 1,705,895 listings in 124 markets
across 37 countries, from Inside Airbnb's public snapshots.

**The site:** https://plotbot2023.github.io/rentals-archetypes/

## What it shows

- **Types by machine learning.** Listings, hosts and markets are each clustered on what they do (price, nights
  booked, reviews, size, how the host operates) and each type is named and given a crest.
- **A map at every level.** The world, regions found by clustering the markets and cut by climate belt, one market's
  own listings. Any measure can be drawn as dots, as squares or as a surface over the land's real relief.
- **Where a listing stands.** Climate belt and hemisphere, climate group, elevation, distance to a shore (ocean or
  lake), an airport and a seaport, rural to metro.
- **Water access, Broward County.** Which canals and rivers reach the open ocean, and which listings stand beside them.

## How to read it honestly

- Nights booked are Inside Airbnb's estimates from reviews, not bookings.
- Inside Airbnb moves each listing's position by up to 150 m.
- Between markets, a map surface is an estimate carried from the markets nearby, and the page says so.
- A group with too few listings reads "not measured".

## Sources and credits

| Source | What it supplies | Licence |
|---|---|---|
| [Inside Airbnb](https://insideairbnb.com) | listings, hosts, review scores and counts; its estimate of nights booked | CC BY 4.0 |
| European Central Bank | daily reference exchange rates (prices in US dollars) | free reuse with the source named |
| [Natural Earth](https://www.naturalearthdata.com) | coastlines, borders, lakes, airports, seaports, shaded relief | public domain |
| [Open-Meteo](https://open-meteo.com) | each market's elevation and climate | CC BY 4.0 |
| Copernicus | the elevation model and ERA5 reanalysis behind Open-Meteo's figures | free reuse with the source named |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Broward County's water, weirs, dams and locks | ODbL, (c) OpenStreetMap contributors |
| Peel, Finlayson and McMahon, 2007 | the Koppen climate group thresholds | published method |

## This repository

`docs/` is the published site. `tools/publish.py` turns the built page into the site: it moves the heavy parts
(the relief image, the map's data, the water maps) into files of their own that load beside the page, adds the
data credit, and refuses to publish a page that carries a private path, an address, an email or a phone number.
The analysis itself is built in a private repository and republished here each data cycle.
