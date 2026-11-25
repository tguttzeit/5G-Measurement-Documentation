# Runs and campaigns

A run is a measurement drive or measurement flight of a unit, from the start of measuring to its completion. The unit assigns every run its own identifier and sends it up with the measurement data. The backend creates the run on the first upload.

Campaigns group several runs, e.g. all drives of a measurement deployment. The public map always shows exactly one campaign, see [Map and export](map.md).

## Checking that the data has arrived

After an upload, superusers see a notification with the number of datapoints. `View in Runs` opens the list.

Without a notification: under `Measurement Runs`, filter by device ID and sort by `Start`. The newest run is at the top. If start time, duration and number of points match the deployment, the data has arrived completely. If the run is missing, [Mission Status](mission-status.md) shows under `Pending Files` whether the unit is still holding back data.

## The list

`Measurement Runs` is visible to all logged-in users. Every row is a run with unit, mission (`ground` or `drone`), start, end, duration, number of points, the means of RSRP, RSRQ and SINR and the campaign.

- **Filters:** device ID, mission type, campaign (also `Unassigned`) and start period
- **Sorting:** by `Start`, `Duration` or `Points`
- **`Show on map`:** opens the map with only this run

If a run has a name, the name is in the `Run` column and the unit's identifier is small below it.

Runs marked `legacy` come from data uploaded before runs were introduced. The backend subsequently grouped them per unit, mission type and day. A legacy run can therefore contain several real drives of a day.

## Editing and deleting runs

Superusers can edit and delete runs.

- **`Edit`:** change name, mission type and campaign. Device ID and run ID are assigned by the unit and cannot be changed. Later uploads to the same run do not overwrite the changes.
- **Several runs at once:** select runs via the checkboxes and choose `Edit selected`. Only the fields that are filled in are changed; everything on `Keep current` stays as it is.
- **`Delete`:** moves the run with all measurements and latency results to the trash. It is then hidden everywhere, including on the map.

### Trash

Deleted runs are kept with all their data in the `Trash`, reachable via the `Trash` button under `Measurement Runs`. There, each run shows when and by whom it was deleted.

- **`Restore`:** brings the run back into the list with all its data.
- **`Delete permanently`:** permanently removes the run with all measurements and latency results.

If a unit still uploads data to a run in the trash, it is kept and also ends up in the trash.

!!! warning "Permanent deletion cannot be undone"

    A permanently deleted run is gone with all its measurement data. If the unit uploads data to this run afterwards, the backend creates it anew, but only with this new data.

## Managing campaigns

Superusers manage campaigns under `Campaign Management`.

- **Creating:** just assign a name, e.g. `summer-2026`. There is no period to set; it results from the campaign's runs.
- **Assigning runs:** at the campaign, open `Manage runs`. At the top are the campaign's runs, below them the runs that can be added. By default these are only runs without a campaign. With `Include runs of other campaigns`, runs from another campaign can also be pulled over.
- **Renaming and deleting:** via `Edit` and `Delete`. When a campaign is deleted, its runs are kept and are `Unassigned` afterwards.

A run belongs to at most one campaign. New runs are initially not assigned to any campaign. Assignment is also possible directly in the list via `Edit` or `Edit selected`.

!!! info "Effect on the public map"

    Without login, the map shows the campaign with the most recent datapoint. Assigning a new run to a campaign can therefore change which campaign guests see first. Runs without a campaign do not appear on the public map at all.
