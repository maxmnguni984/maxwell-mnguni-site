# Source reachability check (do once on your own machine, Phase 0.5)

Open `claude` in this folder and ask the Lead to WebFetch each URL below, then fill in the table. This tells the agents which sources are direct-fetchable from your machine and which must go through `inputs/` manual pastes. Do not attempt to bypass any block.

| Source | Test URL | Result (readable / thin / blocked) | Date | Note |
|---|---|---|---|---|
| Reddit search JSON | https://old.reddit.com/r/BuyItForLife/search.json?q=spice+rack&restrict_sr=1&sort=top&t=year | | | |
| Reddit thread HTML | https://old.reddit.com/r/BuyItForLife/top/?t=month | | | |
| Amazon search | https://www.amazon.com/s?k=magnetic+spice+rack | | | expect bot wall |
| AliExpress search | https://www.aliexpress.us/w/wholesale-magnetic-spice-rack.html | | | expect JS shell |
| Shopify products.json (example store) | https://www.allbirds.com/products.json?limit=3 | | | if readable, use for Shopify competitors |
| CPSC recall API | https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallTitle=spice | | | official, no key |
| Google Patents (search) | https://patents.google.com/?q=magnetic+spice+rack | | | likely JS; use WebSearch site:patents.google.com |
| YouTube search | https://www.youtube.com/results?search_query=magnetic+spice+rack | | | |
| Wayback availability | https://archive.org/wayback/available?url=example.com | | | official, no key |

Sandbox note (2026-09-16): from the remote Claude environment all of Reddit, Amazon, AliExpress, Shopify stores, CPSC, and archive.org were blocked by its egress proxy, so this table must be filled from your own machine.
