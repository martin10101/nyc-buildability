# D-094 visual-proof baseline: the before set (task M0-T194)

Orchestrator evidence, 2026-10-11 (session 0dfe2ecc). H0 of the D-094 before-and-after procedure (row R083): the report and the website as they were before any wave-24 product change. The images stay outside git (public repository; size) in `/root/project/lanes-runtime/owner-docs/session-2026-10-11d/visual-proof/before-set/` on the build server; this manifest pins each file by its sha256 so a later pair can prove which before image it used.

## What was captured, at which revision

- **Product revision:** main `b47041611747eaf0d310c4bf9eddc46907819061` (the preview's recorded revision; the task's contract head `fc96fd9c` on `task/wave24-report-v3` differs from main only in directive files, the owner's question-and-answer log, ledger files and the seam-1 placeholders (eight `docs/zoning-law-library/` documents and the test placeholder `services/api/tests/contracts/test_results_contract_1_5_0.py`); none of these is read by the running product, so the product is the same) [ORCH-CORRECTED per M0-T194 G3 A1].
- **How:** the owner's test preview on the build server (website on 127.0.0.1:3001 with the results and rule switches on for the preview only; the test harness answering for one recorded lot, 215-16 Northern Boulevard, BBL 4073340070, with the recorded city-register zoning-lot index; no production setting touched, nothing deployed). The preview was running at main before the capture and was not stopped (status after: `RUNNING (revision b47041611747eaf0d310c4bf9eddc46907819061)`).
- **Report request:** POST http://127.0.0.1:8000/api/v1/properties/4073340070/report?address=215-16%20NORTHERN%20BOULEVARD%2C%20Queens / status 200 / body {"housing_program":"standard_residence"}
- **Report HTML:** byte-identical to the print of 2026-10-11 10:56 UTC (`session-2026-10-11c/print-main23/report.html`, `cmp` equal).

## Commands (re-runnable)

```
WEB_DIR=/root/project/w-wave20/apps/web OUT_DIR=<folder> node capture_before.mjs      # website: six widths, strips, report preview, report.html
cd <checkout>/apps/web && node scripts/print-report-pdf.mjs <folder>/report.html <folder>/report.pdf
pdftoppm -r 110 -png report.pdf page; pdftoppm -r 110 -png -gray report.pdf grey
python3 metrics_before.py report.pdf report.html before-set > metrics-run1.json   # [ORCH-CORRECTED per G3 A2] then again into metrics-run2.json; cmp the two
```
Both scripts are kept beside the images (sha256 below). Before the capture, the preview must be running at the product revision [ORCH-CORRECTED per G3 A3]: `bash /root/project/lanes-runtime/owner-docs/session-2026-10-11c/preview_acris.sh status` (if it is not running: `... preview_acris.sh build <checkout>` then `... preview_acris.sh start <checkout>`; it serves the recorded lot BBL 4073340070 with the recorded zoning-lot index through `preview_harness_acris.py`, and the capture opens `/property/workspace?ruleeval=on&bbl=4073340070`). The Results window is a fixed-size panel that scrolls inside, so the website is captured as scrolled strips of the panel (each step = the visible height minus 40 px of overlap, top to end) rather than one long page.

## Metrics (G-9)

- **PDF:** 9 pages, A4. Words per page (`pdftotext -f N -l N report.pdf - | wc -w`, no -layout): 364 / 193 / 291 / 338 / 245 / 719 / 296 / 346 / 201 = **2993** (whole-file count 2993; sum of pages 2993).
- **Links:** `pdfinfo -url` prints 25 lines (a header plus 24 links); links by page: page 8: 24. Internal issue/item links in the HTML: 0.
- **Repeats** (sentences of 8 or more words printed at least twice): PDF 3 distinct sentences, 7 printings; HTML 3 distinct, 8 printings. The plan's figure 7 is the PDF printings count. The sentences:
  - 3x: "Map geometry only; tax boundaries do not establish the legal zoning lot; nothing is surveyed."
  - 2x: "No building is placed on this plan yet: the program does not yet work out where a building sits on the lot."
  - 2x: "A check not yet made against an independently worked example."
- **Report HTML visible words per section** (the same visible-text rule as `services/api/tests/drawings/report/test_report_pages.py:71-75`; the running header and footer are page-margin boxes inside the style block, so they are excluded): decision-summary 349, site-and-context 428, option-comparison 316, scenario-B 225, assumptions-open-items 948, calculations-evidence 505; total 2775.
- **Repeatability (S4):** a second run on the same PDF and HTML gave identical metrics (`metrics-run1.json` and `metrics-run2.json` are byte-identical).

## Website capture log

- w1440 1440x900: scroll 5287/610, strips 10, sections 2 [div, three-answers-completeness]
- w390 390x844: scroll 9354/727, strips 14, sections 3 [h2, div, three-answers-completeness]
- w320 320x700: scroll 12256/563, strips 24, sections 3 [h2, div, three-answers-completeness]
- w768 768x1024: scroll 5518/610, strips 10, sections 2 [div, three-answers-completeness]
- w1024 1024x768: scroll 4866/610, strips 9, sections 2 [div, three-answers-completeness]
- w1920 1920x1080: scroll 5287/610, strips 10, sections 2 [div, three-answers-completeness]

## Files and sha256

| File | sha256 |
|---|---|
| `capture-log.txt` | `60b6a0c8734936cbfa9d001fb5c157ac41ab2cd95dff8e008ccdd9bd701de584` |
| `capture_before.mjs` | `bce7d1a7259cdd84e478d6c32e9bbd0528bf6faef11beba1fbffe97d085c614b` |
| `metrics-run1.json` | `569c2feebd08bfcb7db8091761bac1ff0c0cd095cbe9de250efa4db681ed3d67` |
| `metrics-run2.json` | `569c2feebd08bfcb7db8091761bac1ff0c0cd095cbe9de250efa4db681ed3d67` |
| `metrics_before.py` | `5d42b368ce9b2d52751996eabeadcb51f670640e595a211da60eeab996eb29b1` |
| `report-request.txt` | `254fcae515ed18bafc40c90e686073d78b31cfd9871bee0fca24c77986aa78e1` |
| `report.html` | `d2359b16bd1f196306c3b55a894ef453c6a472467ad445cbbbfaf22e47bcf13e` |
| `report.pdf` | `20238a207ec943c8a84245fe6e0de9fb6578d35f958b0b9c6b3d764af3815f51` |
| `grey-1.png` | `f7bf582057ef517f8bbfab4577e91e7225d6d7019fd56b85b515f83325168364` |
| `grey-2.png` | `b6ce8270bdef0ab2464f1a6448495e5021b0e88801317c9fe5bd2790724a6ed3` |
| `grey-3.png` | `01bb9d118910e257d946ed9892b3f3f6e781e6fd209ddf8ad4477ec00f844d77` |
| `grey-4.png` | `28e0359e0a3f52a0f6c70681e00803b4269b2be52e3ece101578835f294d1148` |
| `grey-5.png` | `0055f054d42223e5b4b6eddfc6e6c4debe6f04d5b53480f4cd85bf730bb3644c` |
| `grey-6.png` | `6331f48222b44ebe27c008fdb3ef29ad4f38c5c8f7092b91f636315565ae93b9` |
| `grey-7.png` | `d71d1cf2584f7390fd73d4e684aff6944744ff2ffcf49c96d2ab6523f43ea7f6` |
| `grey-8.png` | `2c9232ca833ed02c62b714407e4922ec04d0a7817e1816e5d507d62450c06fc4` |
| `grey-9.png` | `fd01e6d6ac48aeea722c3ae09eb8590df5ae718588d5a3ff33de3a3636cd8b48` |
| `page-1.png` | `5d630fca4bb64e8825cb9606ca911d232d4c62625ecd90d1b3f631bfb77adccc` |
| `page-2.png` | `4374c9066f36e8a7cc05e74f22e1d983411f10b2cf385955cecdf10aec664811` |
| `page-3.png` | `084c5a4d371f4dd50cf39c71a3352297b61ea680c8c0954ba4d4c38d40a3de73` |
| `page-4.png` | `2c4ad2f6badf6c1708f350fad766a392e14b60fe9291c573f01f1848ed9f4502` |
| `page-5.png` | `392568aa44c72bd73c461ad4517b223e9fd4abd37215a54f4b417bf1805e9cc3` |
| `page-6.png` | `21050b5c1ca0da3d32ae72051b820d7367c0d5297e7f36e39324c3fad774017f` |
| `page-7.png` | `c27d91056ba390672ded6cf2d6f104a8d9fd5572eb2253cacb656c8bfdba4fe6` |
| `page-8.png` | `ddfcacfea13fbfa24506730971786559ca59ea8bd86913a4acdd293a99cd0b7c` |
| `page-9.png` | `19444fcfed4d9cb9c779ed28f77bcf4cfbd9792ef6dedb95de329992fc586001` |
| `w1024-report-preview.png` | `a2d315ea677fd90a6d88f3f4996c145577b2f3a957632c16d70a2bfebc2c31f4` |
| `w1024-results-viewport.png` | `0489cd8a453d846e32e1e8e978783577460013e59a3f0b0e67e1d5dd3306d236` |
| `w1024-strip-00.png` | `06efbb789fee00f59a7c6d3aa986a3529e4cdb0945975a7d878b38bc20c11411` |
| `w1024-strip-01.png` | `42d69d2a58fa65c6700af4becc5d2db1ddc8e40e83c8f1f60f79b5f46476f143` |
| `w1024-strip-02.png` | `1a73279312eb26bd3128ccb43d35cfebaaba6a5f7871bdce3d84057281b46d23` |
| `w1024-strip-03.png` | `f0a59066cad50bd22d1d2fe5ca1235e519a01ded60e77007d2c8b70b9196ebc1` |
| `w1024-strip-04.png` | `7ab7595b5fd4389e9435fa09d6ba8105839b9b9e78977cf019f73a2be646ac19` |
| `w1024-strip-05.png` | `30431730d276fb2b0f16cc3c03640978807e0a9de60883bece78ba026ad9219d` |
| `w1024-strip-06.png` | `947f5699208058f043fc92cf27fc20660e9c01a0974c89f4a8b485308cbf2580` |
| `w1024-strip-07.png` | `f2a09bb03e9557d6c3a6210f69b0b4676bf005b7eb1b3083482a27967d55bd1f` |
| `w1024-strip-08.png` | `3e35ab1459e25c7ee228a0f72e23a887748011985fc5af1b0cb4c9681f3f80b7` |
| `w1440-report-preview.png` | `07de1cdf236ffc6d909241473fd9e0a204fb9c569d443c8c72876a948d1af041` |
| `w1440-results-viewport.png` | `660cb1f0048fed76d0456d00b3d3bec292ef001f4e9827cf3c3178349eeb738f` |
| `w1440-strip-00.png` | `e717895cf20368d17dc6e108a3ba44c2f814dba23429faaa245cac924278c17b` |
| `w1440-strip-01.png` | `b903d7d50d1529284da6cefcfb9e4f459af197ecde251f3da31d01aaa6616e75` |
| `w1440-strip-02.png` | `de19a91f4a3dfe8b0fa1b4f8e78d2501f16c001ff55caa853e46ac618bf7bc2a` |
| `w1440-strip-03.png` | `0516f268d8415c768ec2226a7c903e03928989de88a6767e52b7a4362a683703` |
| `w1440-strip-04.png` | `80cdfd54ade77a368c1d4d2431fdd6ed474d5294fd7aa0c5c020b8d34b813022` |
| `w1440-strip-05.png` | `5e034cf5cdc5d25fcb4bc81c4563cf64f407946bd72ea0280df3fdd120b10217` |
| `w1440-strip-06.png` | `16b49ae4e148cd6124bec71982b0f02fb08f8feb7e9fd931a7bc0c873595a381` |
| `w1440-strip-07.png` | `adec0ac157c07b15c6fbf4263995a908fd05a434a2b87672f4475c1e8fd0c72b` |
| `w1440-strip-08.png` | `c92c6c52370d0277726961cb9c9afce2af486e6b9a473a962d732f2075a18587` |
| `w1440-strip-09.png` | `8cd8009db4b0bd383f71c5bc6595c1085e398b353c9d50eac7a50341dfd7cc0b` |
| `w1920-report-preview.png` | `8bfc7b7a417fb7d70a23bde2ee21195bd4b5007b26d464f0043127caad6ff46a` |
| `w1920-results-viewport.png` | `6634413b7329af1607bb6edd63962c8f0dab387ed913f0b0a3028c669dfd99b1` |
| `w1920-strip-00.png` | `cfb2ea32549a6424e4a62b8112340fe664a90b285f56b6cbb4b8483667e33e0d` |
| `w1920-strip-01.png` | `0172f1c504a29ac70be9eee0ab5efba5c0c9ec529d6119e03360174ddd1c3529` |
| `w1920-strip-02.png` | `6c4b83b8e6576b292724ad29522f5d77e0a62b9c799d0bb0a4833722666aeb5a` |
| `w1920-strip-03.png` | `b072ebc89064bc270aecef46f60730da769bbe18e0b5b19b46c9d4e2bece36c2` |
| `w1920-strip-04.png` | `3b54b38f6ff49eb096e1a30778c2d0d497aa002d89578464ed5323e83af75096` |
| `w1920-strip-05.png` | `39cc82352a6bba1c52a61f48845a36b5218694dfe3ade8fe438570978a67ee81` |
| `w1920-strip-06.png` | `8489b5029f99b722ad2008bbdbd9ce09fbe07a1ddb6e23918c127eedc3b24454` |
| `w1920-strip-07.png` | `0ee2cb6762fb61f7299b3c193bf8083cbe0c4f6d02a9c2d137ee42ded6e74edf` |
| `w1920-strip-08.png` | `423349e6351768a571a556903a2c3ed9e9f4c776fb2db8984f282cccf874878c` |
| `w1920-strip-09.png` | `8c4e08c3d6e17a4d250ff31f2aa17d9ead28366a78d0094cc2c08075cf7e04de` |
| `w320-report-preview.png` | `9061ec0beea2aa7b7b3476e98e6d1eff57ae3d6405957bce91cc7dcf9c86f006` |
| `w320-results-viewport.png` | `0ca56e1fc8736433d374abba6f302069c962c865f7c7b5f298c9946ea87c21a6` |
| `w320-strip-00.png` | `1a1d68f175304731f0a2d0631c56f4706f39cd9524203e2317b999463fc799f0` |
| `w320-strip-01.png` | `a04c165d8258db44fb4b07a2a8e5080b835bcbcb7c63c4ced57e689c41deeb29` |
| `w320-strip-02.png` | `4405a9d726ff9da6ed41215507b3f695d56fbb68ee3158dd90e7acca238db28e` |
| `w320-strip-03.png` | `12b1ce55a6f173b659b0e2308a088744082f567ccd49b331f635e3385a78268a` |
| `w320-strip-04.png` | `51df5e027b029cbc06aa39792e7394f7699b3d516e979f25fc67dfe505b79a29` |
| `w320-strip-05.png` | `a8184ecff86c66c17606ec50f023eb271e1341165674bc7034802de9f84bb260` |
| `w320-strip-06.png` | `7e6159312d9e85d5fa57418d975de52b445790ebc1a4f15def3176072cdb5a91` |
| `w320-strip-07.png` | `23a4bdf9117a1301626b55b068dbed74c7e0448a1ce52fe9f0af3199942725df` |
| `w320-strip-08.png` | `cb0e022535131b5eac9ca246d2798e76b0e44be50b306930d60ce206f3df729f` |
| `w320-strip-09.png` | `3ca913e6bde86996c1e00c191b418c19f3fc9f4f807eb1288772fb0d1b1f0fb0` |
| `w320-strip-10.png` | `814c26ddb822ccb98b745e16fc0f39fadc97b2349b35f6f1832998de0c7036d6` |
| `w320-strip-11.png` | `14f118f5034141813c3718252c55c4fc49aa6d4eb9815270aae7813c56221f1e` |
| `w320-strip-12.png` | `4c4dd859f35919f47fe6f8a3b2727b23bd2bf5fdbe58377a1e581058beb1ac83` |
| `w320-strip-13.png` | `c1b01f02542c28ae6a5b60ead252104f299ba6e6036ed1f0a10dc917f605deca` |
| `w320-strip-14.png` | `05d6193f96a408d7078bca124ccb4c96bfe995f9b0ac8145f822510450e3baca` |
| `w320-strip-15.png` | `89e36267f2a48ca4896f369d52fce112f8a2eb68d9569cb9eb337b32996a480c` |
| `w320-strip-16.png` | `07e2a90436482f7c40664d369cdb84d0b9b9074abd0f21a222dd10e52094fc4e` |
| `w320-strip-17.png` | `fec2a089eebe44c4f591f43b14f47742d6755377628020fba4f5356e774c2d77` |
| `w320-strip-18.png` | `a0552111d464d9f95dee2a24d5854884038f8c92ac5afd0a46204cd50e028c0f` |
| `w320-strip-19.png` | `ed99e217d1bdb7d6cdabfd77da37a1965a8b89ff60554592ea97ca32d7e4767d` |
| `w320-strip-20.png` | `94809072ea06ba8e8bfa28a088603ba66ad3e44de5285a552c78998c206dcbb4` |
| `w320-strip-21.png` | `1871db9b0097a8339e3bdb9edcd87b34163dad4cad888e2e93eae9e0e7236974` |
| `w320-strip-22.png` | `4a4cc1a67ffb4b49eb606b17393f6f00392e5c4191efabe1198301e189ef80fa` |
| `w320-strip-23.png` | `d024c8a4cc638527ab273700a6da339d68548ffd6611f935d024cfad3551bdff` |
| `w390-report-preview.png` | `e6c02ddf1f0a0abaa114daa1d4290e23ea139cb51518c393c849d30ee60ce4fb` |
| `w390-results-viewport.png` | `1d3138621e5a2bb6083c767979e1ac09dd5a37d9639d06fc42196411312a85f5` |
| `w390-strip-00.png` | `45e0628414f0ceb484ae4b80d3ca3705e63013747795ca816d92314ac5803904` |
| `w390-strip-01.png` | `61922fbdd1a109066c112825c1c7901cca5faaecc73abb0faf18092da3dc33fd` |
| `w390-strip-02.png` | `0fdd4dfe4eb7007bdce9ee5367e68dc078bc5e20c88e0612a93234c6cbbf78e2` |
| `w390-strip-03.png` | `2f9213cd3c74e7e39284bb993c2e6adbd09251fa5ebd6f9fb07d19c0f0a3ab04` |
| `w390-strip-04.png` | `7ef6c069b937b65fcf9e24e3dbb9713bea3d29db85062dc0a09448102819dc1e` |
| `w390-strip-05.png` | `707298ff2e358e6460d944379a8cd73088c6ae3241befa49c9309be7bee3774b` |
| `w390-strip-06.png` | `54960ead4627601f60c08c07be10b336a6965ec16db87e6388dff2997a418284` |
| `w390-strip-07.png` | `53f620029ca918d545d8e711be7d69b4d67355a6450229a5023b2a0229dc6ed2` |
| `w390-strip-08.png` | `777e983825dbc4614137f9d84e6567e5d32894ada4b74144c0e66d068cdac6c8` |
| `w390-strip-09.png` | `9005f547be4247692df11eb197d3af340b63aaa3cfd778a203483d012c18580a` |
| `w390-strip-10.png` | `2485de676dac99b56dc97ee1335827d4494afe2dcf92395e2603b694b7f03b55` |
| `w390-strip-11.png` | `56a0152cbe584aa2398b0eb984e95e52a0b6d72f08f3797a8f2be6e166d28775` |
| `w390-strip-12.png` | `48cdf81e77ba313b9f2dd0bab81969f5f8be759527fa4a0f76fa1708e6efec34` |
| `w390-strip-13.png` | `63d87f9c40e9a04c5362b6424396666956def4867565945fb8b91f2a9723cfc2` |
| `w768-report-preview.png` | `afc54888fc4c3d8525a5c21317855a7cbe8894c1c0b0a9a6e13faebf25fe8c6c` |
| `w768-results-viewport.png` | `499c3bcc86f73ab5e732dd987b3afb788e1668981934fb14ce34bacb265d8e68` |
| `w768-strip-00.png` | `124c5d7fbe3016551321e15446eeb11c31dac333a7fce5cb4868aeed599f0777` |
| `w768-strip-01.png` | `4b17bf14a5979ec08f60df907761cbbbe19dfdc8aa5b0cc60d70f3dc7bafe3b1` |
| `w768-strip-02.png` | `2aa68550b168cfc6a709806fd81aeead0d181f9bc4e7bc9148cce39994b8e162` |
| `w768-strip-03.png` | `677184c333d96054282f8fdd5a311310cc64af5afb1a39c6499cc4e3e1f79d48` |
| `w768-strip-04.png` | `16dbcb5108b79fd4e957be19fd5b82c8464b1104d16bc48c15ff8772c7a3ad0f` |
| `w768-strip-05.png` | `503351cbb3ab34b043c7fa7c5f3bb85f05b9305da07bfa839b1770f197c815d1` |
| `w768-strip-06.png` | `61ba7efab6ca3548978d93c36a35e661776b9b08b1c83b2d769d4d630f00a4d2` |
| `w768-strip-07.png` | `878fba1855d37d4ed83c5f70be90878b0bbb7a4600918a8e8bf6b3735ce93c71` |
| `w768-strip-08.png` | `3590cda193d4692c245009318a7cf7b206c9c973c54d1c3c28cb758b48710870` |
| `w768-strip-09.png` | `72694ae80f7c8174e3fe0ba2941ae885d3f47812ae5fd55c58df2cbaf20f0193` |

115 files. Report pages: `page-N.png` (colour) and `grey-N.png` (grey), 110 dpi, N = 1 to 9. Website: `w<width>-results-viewport.png`, `w<width>-strip-NN.png`, `w<width>-report-preview.png` at 320, 390, 768, 1,024, 1,440 and 1,920 px.

## Scenarios

- S1 PASS: nine pages at 110 dpi in colour and grey, each pinned above.
- S2 PASS: the Results view at six widths (viewport, the full panel as strips) and the report preview, each pinned above.
- S3 PASS: the metrics above match the plan's expected figures (364/193/291/338/245/719/296/346/201 = 2,993; 25 link lines, 24 on page 8; 0 internal links).
- S4 PASS: a second metrics run is identical.
- S5 PASS: the owner's preview was running at main before and after; it was never stopped.

Not claimed: nothing here checks correctness or design quality; it fixes the before state only. A first trial capture in `visual-proof/before/` used one long screenshot, which the fixed-size Results panel defeats; it is superseded by this set and not used.
