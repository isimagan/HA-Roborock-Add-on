## v0.2.x
### `binary_sensor.roborock_add_ons_water_equipment_problem`
Nytt navn: Water equipment ~~problem~~

Kan få sensorene den sjekker som attributter. Vi legger til om det er vann i beholder.
| Attributt | State from sensor |
|---|:---|
| mop | `binary_sensor.roborock_mop_attached` |
| waterbox | `binary_sensor.roborock_water_box_attached` |
| water | `binary_sensor.roborock_water_shotage` (hvis `off` så er det vann i beholder) |

### `binary_sensor.roborock_add_ons_off_peak_charging_window`
Nytt navn: Off-peak ~~charging window~~

### Annet
Alt må inn på enhetssiden til Roborock. Da må også navn på entiteter endres slik at de havner der. 
Se hvordan det er gjort i Nordpool-repo.

## v0.3.0
Spør meg om dette

## v0.4.0
Ny entitet: `switch.roborock_stop_before_dock`

Hvis på så stopper støvsuger når den endrer til returning to dock. Når den har stoppet så slås den av. Den slås også av når støvsuger er dokket. 

| Vacuum's state becomes... | Switch |
|---|---|
| Returning to dock | 1. Stop vacuum. 2. Turn off switch |
| Docked | Turn off switch |

## v1.0.0
1. Liten forklaringstekst under hver sensor i konfigurasjonsveiviser, og tettere mellom valgene. Teksten kan være kursiv og litt mindre.
2. Legg tekstene inn i `en.json`
3. Lag PR, og gi meg link til `en.json` som jeg kan endre i samme PR.
4. Oppdater `README.md`
5. Merge PR, lag tag og release.
