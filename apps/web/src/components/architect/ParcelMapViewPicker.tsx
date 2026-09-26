import "./parcel-map-view.css";

interface ParcelMapChoice {
  bbl: string;
  number: number;
  lot: number | null;
  color: string;
}

/** Camera/display focus only; never changes the study's parcel membership. */
export function ParcelMapViewPicker({ parcels, selectedBbl, onSelect }: {
  parcels: ParcelMapChoice[];
  selectedBbl: string | null;
  onSelect: (bbl: string | null) => void;
}) {
  if (parcels.length < 2) return null;
  return <fieldset className="parcel-map-view">
    <legend>Map view</legend>
    <div className="parcel-map-view__choices">
      <button type="button" aria-label="View all parcels" aria-pressed={selectedBbl === null}
        onClick={() => onSelect(null)}>All parcels ({parcels.length})</button>
      {parcels.map(parcel => <button type="button" key={`${parcel.bbl}-${parcel.number}`}
        aria-label={`View Parcel ${parcel.number}${parcel.lot === null ? "" : `, Lot ${parcel.lot}`}`}
        aria-pressed={selectedBbl === parcel.bbl} onClick={() => onSelect(parcel.bbl)}>
        <span className="parcel-map-view__number" style={{ backgroundColor: parcel.color }} aria-hidden="true">{parcel.number}</span>
        {parcel.lot === null ? `Parcel ${parcel.number}` : `Lot ${parcel.lot}`}
      </button>)}
    </div>
  </fieldset>;
}
