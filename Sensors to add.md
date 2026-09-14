# Entiteter å legge til
I denne filen brukes `sensor.roborock_[navn]`. Vanligvis er roborock navnet på entiteten (i mitt tilfelle Bob, så eks `sensor.bob_battery`).

## `select.roborock_fan_speed`
| Variabel | Innhold | Merknad |
|---|---|---|
| options | `{{ state_attr('vacuum.roborock','fan_speed_list') }}` | Bør gjøres om til å begynne med stor bokstav. Hvis et valg ender på _plus så byttes det med plusstegn (Eks. Max+) |
| select_option | (1) | |
| state | `{{ state_attr('vacuum.roborock','fan_speed') }}` | |

### (1)
```yaml
action: vacuum.set_fan_speed
data:
  fan_speed: '{{ option }}'
target:
  entity_id: vacuum.roborock
```

## `binary_sensor.roborock_off_peak`
| Variabel | Innhold |
|---|---|
| device_class | Lader |
| Availability | `{{ is_state('switch.roborock_off_peak_charging', 'on') }}` |

### State
```yaml
{% set now_time = now().time() %}
{% set start = states('time.bob_off_peak_start') %}
{% set end = states('time.bob_off_peak_end') %}
{% set t_start = strptime(start, "%H:%M:%S").time() %}
{% set t_end = strptime(end, "%H:%M:%S").time() %}
{% if t_start < t_end %}
  {{ t_start <= now_time < t_end }}
{% else %}
  {{ now_time >= t_start or now_time < t_end }}
{% endif %}
```
*Kode som er brukt i eget template. Du må gjerne forenkle eller gjøre dette annerledes.*

## `binary_sensor.roborock_water_equipment`
*Bruk riktig engelsk ord hvis equipment er skrevet feil*

| Variabel | Innhold |
|---|---|
| state | `{{ is_state('binary_sensor.roborock_water_box_attached','off') or is_state('binary_sensor.roborock_mop_attached','off') }}` |
| device_class | Problem |
| Availability | `{{ not is_state('vacuum.bob','unavailable') }}` |

## `sensor.roborock_charging_status`
| Variabel | Innhold |
|---|---|
| Availabilty | `{{ not is_state("vacuum.bob", "unavailable") }}` |

### State hvis `binary_sensor.roborock_off_peak` er installert
```yaml
{% if is_state("sensor.roborock_batteri", "100") %}
  Charged
{% elif is_state("binary_sensor.roborock_off_peak", "off") %}
  Charge Pending
{% else %}
  Charging
{% endif %}
```

### State hvis ikke
| Hvis... | ...er... | ...så |
|---|---|---|
| `sensor.roborock_batteri` | `100` | Charged |
| `switch.roborock_off_peak_charging` | `on` | (1) |
| ellers | | Charging |

#### (1)
Hvis **nå** er på eller etter `time.roborock_off_peak_start` og på eller før `time.roborock_off_peak_stop`: Charge Pending
