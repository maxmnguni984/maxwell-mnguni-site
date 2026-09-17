# Evidence log — run 2026-09-17-r1

Shared across all five agents. One row per source actually seen. Nothing enters a report as a FACT without a row here.

Confidence: `fact` (page seen directly), `claim` (asserted by an interested party), `estimate` (derived, method stated).

| E-id | URL | Accessed | Type | What it shows (<=25 words) | Confidence | Agent |
|---|---|---|---|---|---|---|
| E-ENV-01 | n/a — direct network test from this session | 2026-09-17 | manual-input | amazon, aliexpress, etsy, walmart, temu, alibaba, cjdropshipping, reddit, google, trends, shopify all fail at the egress proxy | fact | lead |
| E-DISC-01 | https://www.tiktok.com/@melissametrano/video/6935916113406577925 | 2026-09-17 | video | Paw cleaner demo. Video ID decodes to post date 2021-03-04 | fact (date only) | discovery |
| E-DISC-02 | https://www.tiktok.com/@harrypupperofficial/video/7274276185138400558 | 2026-09-17 | video | Paw cleaner demo, different account. ID decodes to 2023-09-02 | fact (date only) | discovery |
| E-DISC-03 | https://caselaw.findlaw.com/court/us-federal-circuit/1979990.html | 2026-09-17 | policy-page | Drop Stop LLC v. Jian Qing Zhu, enforcement of US Patent 8,267,291 | claim | discovery |
| E-DISC-04 | https://www.securingindustry.com/brand-owner-praises-amazon-s-new-utility-patent-scheme/s112/a11171/ | 2026-09-17 | policy-page | ChomChom utility patent; 320+ counterfeit Amazon listings removed | claim | discovery |
| E-DISC-05 | https://patents.justia.com/patent/D1008759 | 2026-09-17 | policy-page | Live vegetable chopper design patent granted 2023-12-26 | claim | discovery |
| E-DISC-06 | https://dodropshipping.com/epacket-for-dropshipping/ | 2026-09-17 | forum | Claims ePacket China to US averages ~22 days in 2026 | claim | discovery |
| E-ECON-01 | local computation, scripts/econ.py | 2026-09-17 | manual-input | At $25 retail the paid-ads gates cannot be met even at zero cost of goods | fact | lead |
| E-ECON-02 | local computation, scripts/econ.py | 2026-09-17 | manual-input | Gates open at about $45 retail; above $49 the binding limit is landed cost at 38% of retail | fact | lead |
| E-COMP-01 | https://slickdeals.net/f/18388336-dexas-mudbuster-portable-pet-cleaning-kit-with-dog-paw-washer-pet-bathing-brush-microfiber-towel-large-green-24 | 2026-09-17 | marketplace-listing | Dexas sells washer + brush + microfibre towel as one kit at about $24 | fact | competitor |
| E-COMP-02 | https://www.mudbay.com/dog/supplies/grooming/dexas-popware-for-pets-mudbuster-portable-dog-paw-cleaner-blue-medium/1009616.html | 2026-09-17 | marketplace-listing | MudBuster Medium listed at $18.99 | fact | competitor |
| E-COMP-03 | https://www.walmart.com/c/kp/dog-paw-washer-cup | 2026-09-17 | marketplace-listing | Manual paw cleaner cups retail $7.50 to $12.99 at Walmart | claim | supplier |
| E-RISK-01 | https://patents.google.com/patent/USD799126S1/en | 2026-09-17 | policy-page | Design patent D799,126, Pet paw washer, granted 2017-10-03. Ornamental appearance only | claim | risk |
| E-RISK-02 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11696567 | 2026-09-17 | policy-page | US 11,696,567: soft cup body with inward soft spikes. Reads onto all-silicone cups | claim | risk |
| E-RISK-03 | https://rulings.cbp.gov/ruling/n325125 | 2026-09-17 | policy-page | CBP ruling: pet hair remover brush from China, HTS 9603.90.8050, MFN 2.8% base rate | fact | supplier |
| E-SUPP-01 | https://www.exfreight.com/de-minimis-rule-china-800-threshold-eliminated/ | 2026-09-17 | policy-page | US $800 de minimis eliminated; all imports from China now dutiable | claim | supplier |
| E-SUPP-02 | https://time.com/7285316/us-china-trump-tariff-rates-de-minimis-low-value-imports/ | 2026-09-17 | policy-page | Sub-$800 China shipments face 54% tariff or a $100 flat fee | claim | supplier |
| E-SUPP-03 | https://eightx.co/blog/average-ecommerce-3pl-pick-pack-cost-by-order-size-2026 | 2026-09-17 | policy-page | US 3PL pick and pack $2.75 first item, $0.50 each additional, 2026 | claim | supplier |
| E-ECON-03 | local computation, scripts/econ.py | 2026-09-17 | manual-input | $49 kit passes only at all-in delivered cost <= $18; at $29 contribution is negative | fact | lead |
| E-IP-01 | https://www.cpsc.gov/Recalls/2026/Coffeemakers-Recalled-Due-to-Risk-of-Serious-Injury-from-Burn-Hazard-Imported-by-Kidisle | 2026-09-17 | recall-db | 107 reports of hot liquid or steam release, 27 injuries, Amazon/Walmart/eBay, about $49 | fact | risk |
| E-IP-02 | https://patents.google.com/patent/US20160000253A1/en | 2026-09-17 | policy-page | US 9,918,582 B2, Wacaco Co Ltd, portable manually-operated coffee maker, granted 2018-03-20, active | claim | risk |
| E-IP-03 | https://espressosetupbuilder.com/news/kingrinder-lawsuit-2024 | 2026-09-17 | forum | Comandante initiated proceedings against Kingrinder April 2024 over burr design; holds US and EU design patents | claim | risk |
| E-IP-04 | https://trademarks.justia.com/858/43/comandante-85843350.html | 2026-09-17 | policy-page | COMANDANTE Reg. 4465016 registered 2014-01-14, covering hand-operated coffee grinders | fact | risk |
| E-IP-05 | https://trademarks.justia.com/873/82/nanopresso-87382120.html | 2026-09-17 | policy-page | NANOPRESSO Reg. 5373363 and MINIPRESSO Ser. 87034926, both Wacaco Company Limited | fact | risk |
| E-BULK-01 | https://www.help.cbp.gov/s/article/Article-1919 | 2026-09-17 | policy-page | Non-postal shipments file a normal ACE entry and pay ordinary duties; flat fee was postal-only | fact | supplier |
| E-BULK-02 | https://www.honigman.com/alert-3462 | 2026-09-17 | policy-page | Section 301 forced-labour 12.5% on China effective 2026-07-24, replacing the 10% Section 122 surcharge | fact | supplier |
| E-BULK-03 | https://gingercontrol.com/blog/section-301-tariff-rates-china | 2026-09-17 | policy-page | List 4A is 7.5% and covers kitchenware and household goods | claim | supplier |
| E-BULK-04 | https://www.sino-shipping.com/country-guides/shipping-from-china-to-usa/ | 2026-09-17 | policy-page | LCL China to USA quoted at $137.22 per CBM, September 2026. Single unverified snippet | claim | supplier |
| E-BULK-05 | https://idshipthat.app/shipping-rates/usps-ground-advantage/ | 2026-09-17 | policy-page | USPS Ground Advantage 2026 by weight and zone; 8% fuel surcharge to 2027-01-17 atop a 7.8% increase | claim | supplier |
| E-BULK-06 | https://www.fulfill.com/3pl-pricing | 2026-09-17 | policy-page | 3PL storage $18-25 per pallet monthly, pick and pack $2-3, average monthly minimum about $517 | claim | supplier |
| E-ECON-04 | local computation, scripts/econ.py | 2026-09-17 | manual-input | Weight-price frontier: max 1 kg at $79, 3 kg at $89, 5 kg at $99, 6.5 kg at $119 | fact | lead |
