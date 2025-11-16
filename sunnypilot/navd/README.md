# Navigation

Navigation daemon with Mapbox integration for semi-offline navigation. This module handles route planning, geocoding, and turn-by-turn instructions to support autonomous driving features.

- `navigation_helpers/`: Mapbox API integration and navigation instructions processing.
- `navigationd`: Navigation service which uses mapbox integration to generate a route and keep it up to date. This service runs at three hz, using keep time to ensure the while loop only updates three times a second rather than every time sm updates, which in this case would be twenty hz (LLK).
- `nav raylib`: Raylib UI for navigation. This may take a hot minute to make, maybe 1-2 weeks.
