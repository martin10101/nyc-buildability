# Example CAD files to open

These three files are here so you can check that our drawings open on your
computer. They all show the **same made-up example** - a simple rectangular lot
with one rectangular building on it.

**This is not a real property, and it is not an approved or allowed building.**
Every file is stamped "Example lot - not a real property" and "PROPOSED - NOT A
CITY RECORD". Opening the files only proves that the export works. It does not
mean any building is permitted or legal. A qualified person still has to review
any real design.

The example lot is 100 feet by 80 feet. The building is 60 feet by 40 feet and
about 42 feet tall (four floors). The measurements are in US survey feet, the
same units the City uses for New York.

---

## 1. `example-site-plan.dxf` - opens in AutoCAD

This is the CAD drawing.

1. Open AutoCAD.
2. Click **Open** (or File > Open).
3. In the "Files of type" box at the bottom, choose **DXF (*.dxf)**.
4. Pick `example-site-plan.dxf` and open it.

What you should see:

- A rectangle for the **lot** and a smaller rectangle inside it for the
  **building**, plus a simple 3D box for the building shape.
- Four named layers you can turn on and off: **LOT**, **BUILDING_OUTLINE**,
  **MASSING_3D**, and **ANNOTATION**.
- The drawing is in **US survey feet**.
- Text on the drawing that reads **"PROPOSED - NOT A CITY RECORD"**, the
  coordinate note, and **"Example lot - not a real property"**.

If AutoCAD opens the file and you can see the lot, the building and the layers,
the export works.

## 2. `example-site-plan.pdf` - opens in any PDF reader

This is the same site plan as a printable page.

1. Double-click `example-site-plan.pdf`, or open it in any PDF viewer (Adobe
   Reader, Edge, Chrome, Preview - anything).

What you should see:

- One landscape page with the lot and the building drawn on it, edge lengths in
  feet, a north arrow, a scale bar, and a title block.
- The title block says **"Example lot - not a real property"** and
  **"PROPOSED - NOT A CITY RECORD"**.

## 3. `example-massing.glb` - opens in a 3D viewer

This is the building shape in 3D.

1. On Windows, right-click `example-massing.glb` and open it with **3D Viewer**
   (search "3D Viewer" in the Start menu if it is not offered).
2. Any glTF viewer also works, including the free web viewer at
   `https://gltf-viewer.donmccurdy.com/` (drag the file onto the page).

What you should see:

- A grey 3D box (the building) sitting on a flat pad (the lot).
- You can rotate and zoom it. It is labelled "Proposed - not a city record".

---

## What to tell us back

Please reply with:

- Did each file open? (yes / no for the DXF, the PDF and the GLB)
- Which program did you use for each one?
- For the DXF: could you see the lot, the building and the four layers?
- Anything that looked wrong, a warning message, or a file that would not open.

That tells us the export is good on your setup.

---

## File fingerprints (sha256)

If you want to be sure a file was not changed in transit, these are its
fingerprints. They will not usually mean anything to you - they are here for our
records and for the review.

| File | sha256 |
|---|---|
| `example-site-plan.dxf` | `4e19c669ca00d8e71b529e81921f0d203ecfa3c6d4bb57988f9b78d70465c03e` |
| `example-site-plan.pdf` | `8f28f12d9b244c8d17876951dc11e73963f703110cc3ad5697a8b85a7fb0c726` |
| `example-massing.glb` | `0bc7a37d0f78feafe6440bf8636cd5b43b3d25259e76f36d3f9f3fc4fd5816bf` |

These files are rebuilt exactly, byte for byte, by the test
`services/api/tests/cad/test_cad_owner_samples.py`, so they always match the
drawing tools in the code.
