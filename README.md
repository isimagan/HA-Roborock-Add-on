# Roborock Add-ons

A Home Assistant custom integration that adds optional helper entities to devices from Home Assistant's built-in Roborock integration.

## Prerequisite

Set up Home Assistant's built-in **Roborock** integration first.

## Install with HACS

1. Open HACS and choose **Custom repositories**.
2. Add `https://github.com/isimagan/HA-Roborock-Add-on` as **Integration**.
3. Download **Roborock Add-ons** and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**.
5. Search for **Roborock Add-ons**.
6. Select the extra entities you want and complete setup.

No YAML configuration is required. The selected entities are created for every existing Roborock vacuum and attached to its existing device page.

You can change the selection later by opening **Roborock Add-ons → Configure**. The integration reloads automatically after the selection changes.

## Available entities

- **Fan speed** (`select`) — lists the speeds supported by the vacuum and converts names such as `max_plus` to `Max+`.
- **Off-peak** (`binary_sensor`) — on while the configured Roborock off-peak period is active.
- **Water equipment** (`binary_sensor`) — on when the water box or mop is not attached, or when the water tank is empty. Its `mop`, `waterbox`, and `water` attributes show which equipment is available.
- **Charging status** (`sensor`) — reports `Charged`, `Charge pending`, or `Charging`.

The Roborock off-peak switch and start/end time entities are disabled by default in some Home Assistant versions. Enable those source entities on the Roborock device page before using the off-peak or charging-status add-ons.

The original specifications are documented in [Sensors to add.md](Sensors%20to%20add.md).
