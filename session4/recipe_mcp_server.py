"""
=============================================================================
  Session 4: Recipe MCP Server
  University of Hertfordshire AI Workshop
  Time: 14:30 - 16:00
=============================================================================

  This MCP (Model Context Protocol) server exposes culinary analysis tools
  that the Recipe Agent can discover and call.  It provides:

    1. analyse_dish       -- structured breakdown of a dish
    2. get_cooking_techniques -- detailed technique analysis with robotic feasibility
    3. get_equipment_specs    -- kitchen equipment specifications
    4. get_safety_requirements -- food and kitchen safety considerations

  The server uses FastMCP for a clean, decorator-based API.  Data is stored
  in Python dictionaries rather than an external database to keep things
  simple and self-contained for the workshop.

  Run directly:
      python recipe_mcp_server.py

  Or let the Recipe Agent start it automatically via stdio.
=============================================================================
"""

import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Recipe Agent")

# ---------------------------------------------------------------------------
# Dish Database
# ---------------------------------------------------------------------------
# Each entry contains realistic culinary data with enough detail about
# physical tasks (forces, temperatures, timing, precision) to make the
# Session 5 robot-design challenge interesting.

DISH_DATABASE = {
    "pasta carbonara": {
        "dish_name": "Pasta Carbonara",
        "cuisine_type": "Italian",
        "difficulty": "medium",
        "estimated_time_minutes": 30,
        "key_ingredients": [
            "spaghetti (400g)",
            "guanciale or pancetta (200g)",
            "egg yolks (6)",
            "whole eggs (2)",
            "Pecorino Romano cheese (100g, finely grated)",
            "Parmigiano-Reggiano cheese (50g, finely grated)",
            "black pepper (freshly ground)",
            "salt (for pasta water)",
        ],
        "cooking_techniques": [
            "boiling",
            "chopping",
            "frying",
            "whisking",
            "tossing",
            "grating",
            "timing",
            "temperature control",
        ],
        "required_equipment": [
            "large pot",
            "frying pan",
            "mixing bowl",
            "tongs",
            "cheese grater",
            "knife",
            "chopping board",
            "colander",
        ],
        "temperature_requirements": {
            "pasta_water": "100C (rolling boil)",
            "guanciale_render": "130-150C (medium heat to render fat slowly)",
            "sauce_emulsion": "65-75C (must NOT exceed 80C or eggs scramble)",
            "serving_temperature": "70-75C",
        },
        "steps": [
            {
                "step": 1,
                "description": "Bring a large pot of salted water to a rolling boil (about 6 litres).",
                "technique": "boiling",
                "duration_minutes": 10,
                "precision_notes": "Water must reach 100C before adding pasta. Salt at roughly 10g per litre.",
            },
            {
                "step": 2,
                "description": "Cut guanciale into strips approximately 5mm x 30mm.",
                "technique": "chopping",
                "duration_minutes": 3,
                "precision_notes": "Even strip size ensures uniform rendering. Requires firm, controlled knife cuts through dense meat.",
            },
            {
                "step": 3,
                "description": "Finely grate Pecorino Romano and Parmigiano-Reggiano cheeses.",
                "technique": "grating",
                "duration_minutes": 3,
                "precision_notes": "Must be very finely grated to melt smoothly into sauce. Apply moderate downward pressure ~5N against grater.",
            },
            {
                "step": 4,
                "description": "Whisk egg yolks, whole eggs, and grated cheese together in a mixing bowl until smooth.",
                "technique": "whisking",
                "duration_minutes": 2,
                "precision_notes": "Circular whisking motion at ~120 RPM. Mixture should be homogeneous with no lumps.",
            },
            {
                "step": 5,
                "description": "Cook guanciale in a cold frying pan, slowly rendering the fat over medium heat.",
                "technique": "frying",
                "duration_minutes": 8,
                "precision_notes": "Start from cold pan. Heat slowly to 130-150C. Stir occasionally every 60-90 seconds. Fat should become translucent and meat crispy.",
            },
            {
                "step": 6,
                "description": "Cook spaghetti in boiling water until al dente (typically 1 minute less than package directions).",
                "technique": "boiling",
                "duration_minutes": 10,
                "precision_notes": "Must run in parallel with step 5. Reserve 200ml pasta water before draining.",
            },
            {
                "step": 7,
                "description": "Remove pan from heat. Add drained pasta to the guanciale pan and toss vigorously.",
                "technique": "tossing",
                "duration_minutes": 1,
                "precision_notes": "Pan must be OFF heat or below 80C. Toss with wrist-flick motion to coat pasta in rendered fat.",
            },
            {
                "step": 8,
                "description": "Pour egg-cheese mixture over pasta, tossing continuously to create a creamy emulsion. Add splashes of pasta water as needed.",
                "technique": "tossing",
                "duration_minutes": 2,
                "precision_notes": "CRITICAL: temperature must stay between 65-75C. Too hot (>80C) scrambles eggs. Too cold (<60C) leaves raw egg. Continuous tossing motion is essential.",
            },
            {
                "step": 9,
                "description": "Plate immediately and finish with freshly ground black pepper.",
                "technique": "plating",
                "duration_minutes": 1,
                "precision_notes": "Serve quickly before sauce thickens. Twist pepper mill 5-8 times per portion.",
            },
        ],
    },
    "souffle": {
        "dish_name": "Chocolate Souffle",
        "cuisine_type": "French",
        "difficulty": "hard",
        "estimated_time_minutes": 45,
        "key_ingredients": [
            "dark chocolate (200g, 70% cocoa)",
            "unsalted butter (60g, plus extra for ramekins)",
            "egg yolks (4)",
            "egg whites (6)",
            "caster sugar (100g)",
            "cream of tartar (1/4 tsp)",
            "cocoa powder (for dusting ramekins)",
            "vanilla extract (1 tsp)",
        ],
        "cooking_techniques": [
            "melting",
            "whisking",
            "folding",
            "baking",
            "tempering",
            "greasing",
            "timing",
        ],
        "required_equipment": [
            "oven",
            "ramekins (6 x 200ml)",
            "double boiler or bain-marie",
            "stand mixer or electric whisk",
            "rubber spatula",
            "mixing bowls (3)",
            "pastry brush",
            "baking tray",
        ],
        "temperature_requirements": {
            "oven_preheat": "190C (fan-assisted) or 200C (conventional)",
            "chocolate_melting": "45-50C (via bain-marie, never direct heat)",
            "egg_whites": "room temperature (20-22C) for maximum volume",
            "serving": "immediately upon removal from oven",
        },
        "steps": [
            {
                "step": 1,
                "description": "Preheat oven to 190C. Brush ramekins with soft butter using upward strokes, then dust with cocoa powder.",
                "technique": "greasing",
                "duration_minutes": 5,
                "precision_notes": "Upward brush strokes help the souffle rise evenly. Even butter coating ~1mm thick.",
            },
            {
                "step": 2,
                "description": "Melt chocolate and butter together in a bain-marie, stirring until smooth.",
                "technique": "melting",
                "duration_minutes": 8,
                "precision_notes": "Water must simmer, not boil. Chocolate temperature 45-50C max. Stir gently at ~30 RPM to avoid incorporating air.",
            },
            {
                "step": 3,
                "description": "Whisk egg yolks with 50g sugar until pale and thick (ribbon stage).",
                "technique": "whisking",
                "duration_minutes": 4,
                "precision_notes": "High-speed whisking ~300 RPM. Mixture should triple in volume and leave a ribbon trail lasting 3 seconds.",
            },
            {
                "step": 4,
                "description": "Fold melted chocolate into egg yolk mixture gently.",
                "technique": "folding",
                "duration_minutes": 2,
                "precision_notes": "Use figure-of-eight folding motion. Maximum 15-20 strokes. Over-mixing deflates the mixture.",
            },
            {
                "step": 5,
                "description": "Whisk egg whites with cream of tartar to soft peaks, then gradually add remaining 50g sugar, whisking to stiff glossy peaks.",
                "technique": "whisking",
                "duration_minutes": 6,
                "precision_notes": "Bowl must be spotlessly clean and grease-free. Start at medium speed, increase to high. Stiff peaks should hold shape when whisk is lifted.",
            },
            {
                "step": 6,
                "description": "Fold one-third of egg whites into chocolate mixture to lighten it, then gently fold in the remaining whites.",
                "technique": "folding",
                "duration_minutes": 3,
                "precision_notes": "CRITICAL: fold gently with rubber spatula using cut-and-fold motion. Do NOT stir. Some white streaks are acceptable -- over-folding loses volume.",
            },
            {
                "step": 7,
                "description": "Fill ramekins to the top and level with a palette knife. Run thumb around inside rim to create a shallow groove.",
                "technique": "filling",
                "duration_minutes": 2,
                "precision_notes": "Fill precisely to top edge. The groove helps the souffle rise with a 'top hat' shape. Handle ramekins gently.",
            },
            {
                "step": 8,
                "description": "Bake immediately for 12-14 minutes until risen and slightly wobbly in the centre.",
                "technique": "baking",
                "duration_minutes": 13,
                "precision_notes": "Do NOT open oven door during baking. Souffle should rise 3-4cm above ramekin. Centre should wobble slightly when gently shaken.",
            },
            {
                "step": 9,
                "description": "Serve immediately -- souffle begins to deflate within 60 seconds of leaving the oven.",
                "technique": "plating",
                "duration_minutes": 1,
                "precision_notes": "Speed is critical. Transport ramekins carefully -- sudden jolts cause collapse.",
            },
        ],
    },
    "sushi rolls": {
        "dish_name": "Sushi Rolls (Maki)",
        "cuisine_type": "Japanese",
        "difficulty": "hard",
        "estimated_time_minutes": 60,
        "key_ingredients": [
            "sushi rice (500g, short-grain Japanese rice)",
            "rice vinegar (80ml)",
            "sugar (30g)",
            "salt (10g)",
            "nori sheets (10)",
            "fresh salmon or tuna (300g, sashimi-grade)",
            "cucumber (1, deseeded)",
            "avocado (2, ripe)",
            "wasabi paste",
            "soy sauce",
            "pickled ginger",
        ],
        "cooking_techniques": [
            "washing",
            "boiling",
            "seasoning",
            "slicing",
            "spreading",
            "rolling",
            "cutting",
            "precision knife work",
        ],
        "required_equipment": [
            "rice cooker or heavy-bottomed pot with lid",
            "hangiri (wooden sushi bowl) or large flat bowl",
            "bamboo rolling mat (makisu)",
            "sharp knife (yanagiba or chef's knife)",
            "rice paddle (shamoji)",
            "plastic wrap",
            "cutting board",
            "small bowl of vinegar-water (for wetting hands)",
        ],
        "temperature_requirements": {
            "rice_cooking": "100C (bring to boil then reduce to low simmer)",
            "rice_seasoning": "body temperature (~37C) when handling",
            "fish_storage": "0-4C until ready to use",
            "serving": "room temperature (20-22C)",
        },
        "steps": [
            {
                "step": 1,
                "description": "Wash rice in cold water 4-5 times until water runs mostly clear.",
                "technique": "washing",
                "duration_minutes": 5,
                "precision_notes": "Gentle swirling motions to avoid breaking grains. Water should change from milky-white to nearly clear.",
            },
            {
                "step": 2,
                "description": "Cook rice with equal volume of water. Bring to boil, reduce to lowest heat, cook 15 minutes, rest 10 minutes.",
                "technique": "boiling",
                "duration_minutes": 25,
                "precision_notes": "Do NOT lift lid during cooking. Precise water ratio (1:1 by volume) is critical for texture.",
            },
            {
                "step": 3,
                "description": "Transfer rice to hangiri. Season with vinegar mixture while fanning and folding with shamoji.",
                "technique": "seasoning",
                "duration_minutes": 5,
                "precision_notes": "Use cutting and folding motions (not stirring) to coat grains without crushing. Fan simultaneously to cool rice and create glossy finish.",
            },
            {
                "step": 4,
                "description": "Slice fish into strips approximately 1cm x 1cm x 10cm with single, smooth pulling cuts.",
                "technique": "precision knife work",
                "duration_minutes": 10,
                "precision_notes": "CRITICAL: use a single drawing stroke per cut, pulling knife towards you. Never saw back and forth. Knife must be extremely sharp. Consistent strip dimensions within 2mm tolerance.",
            },
            {
                "step": 5,
                "description": "Slice cucumber and avocado into thin, uniform strips.",
                "technique": "slicing",
                "duration_minutes": 5,
                "precision_notes": "Cucumber: 5mm x 5mm batons. Avocado: 5mm thick slices. Uniformity matters for even rolling.",
            },
            {
                "step": 6,
                "description": "Place nori sheet on bamboo mat. Spread rice evenly in a thin layer (5mm), leaving 2cm bare strip at the far edge.",
                "technique": "spreading",
                "duration_minutes": 3,
                "precision_notes": "Wet hands frequently to prevent sticking. Rice layer must be uniform ~5mm thick. Apply gentle, even pressure ~2-3N.",
            },
            {
                "step": 7,
                "description": "Arrange fillings in a line across the centre of the rice.",
                "technique": "placing",
                "duration_minutes": 1,
                "precision_notes": "Place fillings in a single neat line. Do not overfill -- total filling diameter should be ~2cm.",
            },
            {
                "step": 8,
                "description": "Roll using the bamboo mat: lift edge, tuck over filling, compress gently, then continue rolling forward.",
                "technique": "rolling",
                "duration_minutes": 2,
                "precision_notes": "Apply even, gentle compression ~3-5N along the full length. Roll must be cylindrical and tight but not crushed. Moisten bare nori strip to seal.",
            },
            {
                "step": 9,
                "description": "Cut each roll into 6-8 pieces with a wet, sharp knife using a single smooth stroke.",
                "technique": "cutting",
                "duration_minutes": 2,
                "precision_notes": "Wet knife between every cut. Single drawing stroke -- do not press down and crush. Even piece width within 3mm tolerance.",
            },
        ],
    },
    "pizza margherita": {
        "dish_name": "Pizza Margherita",
        "cuisine_type": "Italian",
        "difficulty": "medium",
        "estimated_time_minutes": 90,
        "key_ingredients": [
            "type 00 flour (500g)",
            "water (325ml, lukewarm at 35C)",
            "fresh yeast (10g) or dry yeast (5g)",
            "salt (10g)",
            "olive oil (15ml)",
            "San Marzano tomatoes (400g tin, crushed by hand)",
            "fresh mozzarella (250g, torn into pieces)",
            "fresh basil leaves (handful)",
            "extra virgin olive oil (for finishing)",
        ],
        "cooking_techniques": [
            "kneading",
            "proofing",
            "crushing",
            "stretching",
            "spreading",
            "baking",
            "slicing",
        ],
        "required_equipment": [
            "oven (ideally 250C+ or pizza oven)",
            "pizza stone or steel",
            "large mixing bowl",
            "work surface (floured)",
            "pizza peel or flat baking tray",
            "knife",
            "bench scraper",
        ],
        "temperature_requirements": {
            "water_for_yeast": "35C (lukewarm -- too hot kills yeast)",
            "proofing_environment": "24-28C (warm, draft-free)",
            "oven": "250-300C (as hot as domestic oven allows; 450C+ for pizza oven)",
            "pizza_stone_preheat": "at least 30 minutes at max temperature",
        },
        "steps": [
            {
                "step": 1,
                "description": "Dissolve yeast in lukewarm water (35C). Let sit for 5 minutes until slightly foamy.",
                "technique": "mixing",
                "duration_minutes": 5,
                "precision_notes": "Water temperature critical: 30-37C activates yeast, above 45C kills it.",
            },
            {
                "step": 2,
                "description": "Combine flour and salt, make a well, add yeast-water and olive oil. Mix until a shaggy dough forms.",
                "technique": "mixing",
                "duration_minutes": 3,
                "precision_notes": "Stir with a fork initially, then hands. Dough will be rough and sticky at this stage.",
            },
            {
                "step": 3,
                "description": "Knead dough on a floured surface for 10 minutes until smooth, elastic, and passes the windowpane test.",
                "technique": "kneading",
                "duration_minutes": 10,
                "precision_notes": "Push-fold-rotate rhythm at ~60 cycles per minute. Apply ~10-15N of force. Dough should stretch thin enough to see light through without tearing.",
            },
            {
                "step": 4,
                "description": "Place dough in oiled bowl, cover, and let rise in a warm place until doubled in size.",
                "technique": "proofing",
                "duration_minutes": 45,
                "precision_notes": "Environment should be 24-28C. Dough is ready when poked with a finger and the indent springs back slowly.",
            },
            {
                "step": 5,
                "description": "Preheat oven to maximum temperature (250-300C) with pizza stone inside for at least 30 minutes.",
                "technique": "preheating",
                "duration_minutes": 30,
                "precision_notes": "Stone must be thoroughly preheated to prevent soggy base.",
            },
            {
                "step": 6,
                "description": "Divide dough into 3 balls. Stretch each into a 30cm round using hands (not a rolling pin).",
                "technique": "stretching",
                "duration_minutes": 5,
                "precision_notes": "Press centre outward with fingertips, then drape over knuckles and stretch by gravity. Leave a slightly thicker rim (~1cm). Thickness ~3mm in centre.",
            },
            {
                "step": 7,
                "description": "Spread crushed tomatoes over the base, leaving 2cm border. Add torn mozzarella and a drizzle of olive oil.",
                "technique": "spreading",
                "duration_minutes": 3,
                "precision_notes": "Use the back of a spoon in a spiral motion. Sauce layer should be thin (~2mm). Do not overload.",
            },
            {
                "step": 8,
                "description": "Slide pizza onto preheated stone and bake for 8-12 minutes until crust is golden and cheese bubbles.",
                "technique": "baking",
                "duration_minutes": 10,
                "precision_notes": "Quick, confident sliding motion onto stone. Rotate pizza 180 degrees halfway through if oven has hot spots.",
            },
            {
                "step": 9,
                "description": "Remove from oven, add fresh basil leaves and a final drizzle of olive oil. Slice and serve.",
                "technique": "slicing",
                "duration_minutes": 2,
                "precision_notes": "Use a pizza wheel or sharp knife. Cut through in one rolling motion to avoid dragging toppings.",
            },
        ],
    },
    "beef stir-fry": {
        "dish_name": "Beef Stir-Fry",
        "cuisine_type": "Chinese",
        "difficulty": "medium",
        "estimated_time_minutes": 25,
        "key_ingredients": [
            "beef sirloin or flank steak (400g)",
            "soy sauce (3 tbsp)",
            "oyster sauce (2 tbsp)",
            "sesame oil (1 tbsp)",
            "cornstarch (1 tbsp)",
            "vegetable oil (3 tbsp, high smoke point)",
            "garlic (4 cloves, minced)",
            "fresh ginger (2cm piece, julienned)",
            "bell peppers (2, mixed colours, sliced)",
            "broccoli florets (200g)",
            "spring onions (4, cut into 3cm lengths)",
            "rice or noodles (for serving)",
        ],
        "cooking_techniques": [
            "slicing",
            "marinating",
            "stir-frying",
            "tossing",
            "high-heat searing",
            "deglazing",
            "timing",
        ],
        "required_equipment": [
            "wok (carbon steel preferred)",
            "wok spatula or large spoon",
            "sharp knife",
            "chopping board",
            "mixing bowl",
            "high-power burner (ideally 15,000+ BTU)",
        ],
        "temperature_requirements": {
            "wok_temperature": "250-300C (wok must be smoking hot before adding oil)",
            "oil_addition": "oil should shimmer and ripple within 5 seconds",
            "beef_searing": "high heat, 260-300C, to achieve wok hei (breath of the wok)",
            "vegetable_cooking": "high heat but brief, 30-90 seconds per batch",
        },
        "steps": [
            {
                "step": 1,
                "description": "Slice beef against the grain into 3mm thin strips. Marinate with soy sauce, cornstarch, and sesame oil for 15 minutes.",
                "technique": "slicing",
                "duration_minutes": 18,
                "precision_notes": "Cut AGAINST the grain for tenderness. Uniform 3mm thickness ensures even cooking. Partially freezing beef (15 min) makes slicing easier.",
            },
            {
                "step": 2,
                "description": "Prepare all vegetables: slice peppers, cut broccoli into florets, mince garlic, julienne ginger, cut spring onions.",
                "technique": "chopping",
                "duration_minutes": 5,
                "precision_notes": "ALL ingredients must be prepped before cooking starts (mise en place). Stir-fry cooking is too fast to prep during.",
            },
            {
                "step": 3,
                "description": "Heat wok over maximum flame until smoking. Add oil, swirl to coat.",
                "technique": "high-heat searing",
                "duration_minutes": 2,
                "precision_notes": "Wok must reach 250-300C before adding any food. Oil should shimmer immediately. This is dangerous -- handle with care.",
            },
            {
                "step": 4,
                "description": "Add beef in a single layer. Do NOT move for 30 seconds to develop sear. Then toss for 60 seconds. Remove and set aside.",
                "technique": "stir-frying",
                "duration_minutes": 2,
                "precision_notes": "Cook in batches if needed -- overcrowding drops temperature and steams instead of sears. Wrist-flick tossing motion, 2-3 tosses per second.",
            },
            {
                "step": 5,
                "description": "Add more oil if needed. Stir-fry broccoli for 90 seconds, then peppers for 60 seconds.",
                "technique": "stir-frying",
                "duration_minutes": 3,
                "precision_notes": "Hard vegetables first, soft vegetables after. Keep tossing continuously. Vegetables should be crisp-tender, not soft.",
            },
            {
                "step": 6,
                "description": "Add garlic and ginger, stir-fry for 15 seconds until fragrant. Return beef to wok.",
                "technique": "tossing",
                "duration_minutes": 1,
                "precision_notes": "Garlic burns in seconds at wok temperatures -- add late and keep moving. 15 seconds maximum.",
            },
            {
                "step": 7,
                "description": "Add oyster sauce and a splash of water. Toss everything together for 30 seconds. Finish with spring onions.",
                "technique": "deglazing",
                "duration_minutes": 1,
                "precision_notes": "Quick toss to combine. Total time from first oil to plating should be under 5 minutes of active cooking.",
            },
        ],
    },
    "chocolate cake": {
        "dish_name": "Chocolate Cake",
        "cuisine_type": "Western/International",
        "difficulty": "easy",
        "estimated_time_minutes": 75,
        "key_ingredients": [
            "plain flour (250g)",
            "cocoa powder (80g)",
            "caster sugar (350g)",
            "eggs (3, room temperature)",
            "buttermilk (240ml)",
            "vegetable oil (120ml)",
            "vanilla extract (2 tsp)",
            "baking powder (2 tsp)",
            "bicarbonate of soda (1 tsp)",
            "salt (1/2 tsp)",
            "hot water or coffee (240ml)",
            "dark chocolate (200g, for ganache)",
            "double cream (200ml, for ganache)",
        ],
        "cooking_techniques": [
            "sifting",
            "mixing",
            "whisking",
            "pouring",
            "baking",
            "melting",
            "spreading",
            "levelling",
        ],
        "required_equipment": [
            "oven",
            "two 23cm round cake tins",
            "baking paper",
            "large mixing bowl",
            "electric mixer or whisk",
            "sieve",
            "spatula",
            "wire cooling rack",
            "saucepan",
            "palette knife or offset spatula",
        ],
        "temperature_requirements": {
            "oven": "170C (fan-assisted) or 180C (conventional)",
            "ingredients": "all at room temperature (20-22C) before mixing",
            "hot_water_addition": "just-boiled water (~95C) activates cocoa",
            "ganache_cream": "heat cream to 80C, pour over chopped chocolate",
            "ganache_application": "apply at 28-32C (pourable but not runny)",
        },
        "steps": [
            {
                "step": 1,
                "description": "Preheat oven to 170C. Line two 23cm cake tins with baking paper and grease sides.",
                "technique": "greasing",
                "duration_minutes": 5,
                "precision_notes": "Even grease coating prevents sticking. Cut baking paper circles to fit tin base exactly.",
            },
            {
                "step": 2,
                "description": "Sift together flour, cocoa powder, baking powder, bicarbonate of soda, sugar, and salt.",
                "technique": "sifting",
                "duration_minutes": 3,
                "precision_notes": "Sifting aerates dry ingredients and removes lumps. Hold sieve 15-20cm above bowl.",
            },
            {
                "step": 3,
                "description": "In a separate bowl, whisk eggs, buttermilk, oil, and vanilla until combined.",
                "technique": "whisking",
                "duration_minutes": 2,
                "precision_notes": "Medium-speed whisking. All wet ingredients should be at room temperature to prevent curdling.",
            },
            {
                "step": 4,
                "description": "Add wet ingredients to dry and mix until just combined. Add hot water and stir -- batter will be thin.",
                "technique": "mixing",
                "duration_minutes": 3,
                "precision_notes": "Do NOT overmix -- stop as soon as no dry streaks remain. Overmixing develops gluten and makes cake tough.",
            },
            {
                "step": 5,
                "description": "Divide batter equally between the two tins. Bake for 30-35 minutes until a skewer inserted in the centre comes out clean.",
                "technique": "baking",
                "duration_minutes": 33,
                "precision_notes": "Fill tins equally (weigh for accuracy). Do not open oven door in first 20 minutes. Skewer test is the definitive doneness check.",
            },
            {
                "step": 6,
                "description": "Cool in tins for 10 minutes, then turn out onto wire racks to cool completely.",
                "technique": "cooling",
                "duration_minutes": 30,
                "precision_notes": "Cakes must be COMPLETELY cool before frosting (below 25C) or ganache will melt and slide off.",
            },
            {
                "step": 7,
                "description": "Make ganache: heat cream to 80C, pour over finely chopped chocolate, let sit 2 minutes, then stir until smooth.",
                "technique": "melting",
                "duration_minutes": 5,
                "precision_notes": "Chop chocolate to uniform 5mm pieces for even melting. Stir from centre outward in concentric circles.",
            },
            {
                "step": 8,
                "description": "Let ganache cool to 28-32C (spreadable consistency). Place first cake layer, spread ganache, add second layer, coat top and sides.",
                "technique": "spreading",
                "duration_minutes": 10,
                "precision_notes": "Use offset spatula with smooth, even strokes. Apply crumb coat first (thin layer), chill 15 min, then final coat.",
            },
        ],
    },
    "fish and chips": {
        "dish_name": "Fish and Chips",
        "cuisine_type": "British",
        "difficulty": "medium",
        "estimated_time_minutes": 45,
        "key_ingredients": [
            "cod or haddock fillets (4 x 200g, skinless)",
            "plain flour (200g, plus extra for dusting)",
            "cornflour (50g)",
            "baking powder (1 tsp)",
            "cold sparkling water or beer (300ml)",
            "salt and white pepper",
            "large potatoes (1kg, Maris Piper or King Edward)",
            "vegetable oil or beef dripping (2 litres, for deep frying)",
            "lemon wedges and malt vinegar (for serving)",
        ],
        "cooking_techniques": [
            "peeling",
            "cutting",
            "deep frying",
            "battering",
            "double frying",
            "draining",
            "temperature monitoring",
        ],
        "required_equipment": [
            "deep fryer or large heavy pot (at least 4 litre capacity)",
            "cooking thermometer",
            "spider strainer or slotted spoon",
            "wire rack over baking tray",
            "sharp knife",
            "chopping board",
            "mixing bowls",
            "whisk",
            "kitchen paper",
        ],
        "temperature_requirements": {
            "first_chip_fry": "130-140C (blanching stage, 6-8 minutes)",
            "second_chip_fry": "180-190C (crisping stage, 2-3 minutes)",
            "fish_frying": "180C (must be accurate -- too low = greasy, too high = burns batter before fish cooks)",
            "oil_danger": "NEVER exceed 200C. Flash point of most oils is 300-330C. NEVER leave unattended.",
            "holding_temperature": "keep cooked items warm in oven at 120C",
        },
        "steps": [
            {
                "step": 1,
                "description": "Peel potatoes and cut into chips approximately 1.5cm x 1.5cm x 8cm. Soak in cold water for 30 minutes to remove excess starch.",
                "technique": "cutting",
                "duration_minutes": 15,
                "precision_notes": "Uniform chip size is critical for even cooking. 1.5cm thickness is ideal for crispy outside, fluffy inside.",
            },
            {
                "step": 2,
                "description": "Make batter: whisk flour, cornflour, baking powder, salt together. Add ice-cold sparkling water and whisk briefly (lumps are fine).",
                "technique": "battering",
                "duration_minutes": 3,
                "precision_notes": "Batter must be ICE COLD for maximum crispness. Do NOT overmix -- a few lumps are desirable. Make just before use.",
            },
            {
                "step": 3,
                "description": "Heat oil to 130-140C. Drain and thoroughly dry chips. Fry in batches for 6-8 minutes until cooked through but NOT coloured.",
                "technique": "deep frying",
                "duration_minutes": 20,
                "precision_notes": "CRITICAL SAFETY: lower chips slowly into oil to prevent splashing. Cook in small batches (200g max) to maintain temperature. Chips should be soft and pale.",
            },
            {
                "step": 4,
                "description": "Remove chips to wire rack. Increase oil temperature to 180C.",
                "technique": "draining",
                "duration_minutes": 5,
                "precision_notes": "Chips can rest at this stage for up to 2 hours. Second fry is what creates the crunch.",
            },
            {
                "step": 5,
                "description": "Pat fish fillets dry. Dust with seasoned flour, shaking off excess, then dip in batter.",
                "technique": "battering",
                "duration_minutes": 3,
                "precision_notes": "Fish MUST be dry or batter will not adhere. Flour dusting creates a bonding layer. Dip and lift in one smooth motion.",
            },
            {
                "step": 6,
                "description": "Carefully lower battered fish into 180C oil. Fry for 6-8 minutes until golden and cooked through.",
                "technique": "deep frying",
                "duration_minutes": 8,
                "precision_notes": "Lower fish AWAY from you into oil to prevent splash burns. Do not move fish for first 2 minutes while batter sets. Flip once halfway through.",
            },
            {
                "step": 7,
                "description": "While fish is frying, return chips to 180C oil for 2-3 minutes until golden and crispy.",
                "technique": "deep frying",
                "duration_minutes": 3,
                "precision_notes": "This second fry is quick. Chips should be deep golden. Drain on wire rack, season with salt immediately.",
            },
            {
                "step": 8,
                "description": "Drain everything on wire rack (not kitchen paper, which traps steam). Season and serve with lemon and vinegar.",
                "technique": "draining",
                "duration_minutes": 2,
                "precision_notes": "Serve immediately. Wire rack allows air circulation for maintained crispness.",
            },
        ],
    },
    "pad thai": {
        "dish_name": "Pad Thai",
        "cuisine_type": "Thai",
        "difficulty": "medium",
        "estimated_time_minutes": 30,
        "key_ingredients": [
            "flat rice noodles (200g, dried)",
            "prawns or chicken (200g)",
            "firm tofu (100g, pressed and cubed)",
            "eggs (2)",
            "bean sprouts (100g)",
            "garlic chives or spring onions (50g)",
            "roasted peanuts (50g, crushed)",
            "garlic (3 cloves, minced)",
            "tamarind paste (3 tbsp)",
            "fish sauce (3 tbsp)",
            "palm sugar or brown sugar (2 tbsp)",
            "lime (2, cut into wedges)",
            "dried chilli flakes (1 tsp)",
            "vegetable oil (3 tbsp)",
        ],
        "cooking_techniques": [
            "soaking",
            "stir-frying",
            "tossing",
            "scrambling",
            "crushing",
            "sauce mixing",
            "high-heat cooking",
        ],
        "required_equipment": [
            "wok",
            "wok spatula",
            "large bowl (for soaking noodles)",
            "small saucepan",
            "knife and chopping board",
            "mortar and pestle (for peanuts)",
        ],
        "temperature_requirements": {
            "noodle_soak": "room temperature water, 20-25C, for 30 minutes",
            "wok": "very high heat, 250-280C",
            "sauce_mixing": "room temperature",
        },
        "steps": [
            {
                "step": 1,
                "description": "Soak rice noodles in room temperature water for 30 minutes until pliable but still firm.",
                "technique": "soaking",
                "duration_minutes": 30,
                "precision_notes": "Do NOT use hot water -- noodles will become mushy. They should be bendy but still have a white core.",
            },
            {
                "step": 2,
                "description": "Mix tamarind paste, fish sauce, and palm sugar in a small bowl to create the pad thai sauce.",
                "technique": "sauce mixing",
                "duration_minutes": 2,
                "precision_notes": "Stir until sugar is dissolved. Taste and adjust: should be a balance of sour, salty, and sweet.",
            },
            {
                "step": 3,
                "description": "Heat wok until smoking. Add oil, then cook protein (prawns/chicken/tofu) until done. Remove and set aside.",
                "technique": "stir-frying",
                "duration_minutes": 3,
                "precision_notes": "High heat, quick cooking. Prawns: 2 min per side. Chicken: 3-4 min total. Remove promptly to avoid overcooking.",
            },
            {
                "step": 4,
                "description": "Push contents aside, crack eggs into wok, scramble quickly, then break into small pieces.",
                "technique": "scrambling",
                "duration_minutes": 1,
                "precision_notes": "Eggs cook in 20-30 seconds at wok temperature. Break into small bits with spatula edge.",
            },
            {
                "step": 5,
                "description": "Add drained noodles and pad thai sauce. Toss and stir-fry for 2-3 minutes until noodles absorb sauce.",
                "technique": "tossing",
                "duration_minutes": 3,
                "precision_notes": "Use lifting and tossing motions to prevent noodles clumping. Noodles should be tender and coated in sauce.",
            },
            {
                "step": 6,
                "description": "Return protein, add bean sprouts and garlic chives. Toss for 30 seconds.",
                "technique": "tossing",
                "duration_minutes": 1,
                "precision_notes": "Brief toss only -- bean sprouts should remain crunchy. Total wok time should not exceed 5 minutes.",
            },
            {
                "step": 7,
                "description": "Plate and garnish with crushed peanuts, lime wedges, and chilli flakes.",
                "technique": "plating",
                "duration_minutes": 2,
                "precision_notes": "Crush peanuts to roughly 2-3mm pieces. Arrange lime wedges on the side.",
            },
        ],
    },
    "french omelette": {
        "dish_name": "French Omelette",
        "cuisine_type": "French",
        "difficulty": "hard",
        "estimated_time_minutes": 10,
        "key_ingredients": [
            "eggs (3, room temperature)",
            "unsalted butter (15g)",
            "salt (pinch)",
            "white pepper (pinch)",
            "fresh chives (1 tbsp, finely snipped, optional)",
        ],
        "cooking_techniques": [
            "whisking",
            "swirling",
            "shaking",
            "tilting",
            "rolling",
            "butter foaming",
            "precise heat control",
        ],
        "required_equipment": [
            "non-stick frying pan (20cm)",
            "fork or chopsticks",
            "plate (warmed)",
        ],
        "temperature_requirements": {
            "butter_foaming": "150-160C (butter should foam but NOT brown)",
            "cooking": "medium-low heat, 140-160C pan surface",
            "eggs_when_folded": "centre should be slightly underdone (baveuse) at ~65-70C",
        },
        "steps": [
            {
                "step": 1,
                "description": "Crack eggs into a bowl. Season with salt and white pepper. Beat with a fork until yolks and whites are just combined (no streaks).",
                "technique": "whisking",
                "duration_minutes": 1,
                "precision_notes": "Do NOT overbeat -- you do not want foam or bubbles. Just break the yolks and combine. About 30-40 fork strokes.",
            },
            {
                "step": 2,
                "description": "Heat non-stick pan over medium-low heat. Add butter and swirl until it foams, coats the pan, and the foam just begins to subside.",
                "technique": "butter foaming",
                "duration_minutes": 1,
                "precision_notes": "CRITICAL window: butter should foam vigorously then foam starts to die down. This indicates 150-160C. If butter browns, pan is too hot -- start over.",
            },
            {
                "step": 3,
                "description": "Pour in beaten eggs. Immediately stir rapidly with a fork or chopsticks in small circular motions while shaking the pan back and forth.",
                "technique": "swirling",
                "duration_minutes": 1,
                "precision_notes": "Simultaneous fork-stirring (~3 circles/sec) and pan-shaking (~2 shakes/sec). This creates small, creamy curds. Continue for 30-45 seconds until eggs are 70% set.",
            },
            {
                "step": 4,
                "description": "Stop stirring. Let the omelette sit for 10-15 seconds to form a very thin skin on the bottom.",
                "technique": "precise heat control",
                "duration_minutes": 0.25,
                "precision_notes": "Bottom should set into a pale (NOT browned) skin. Interior remains creamy (baveuse). Timing is critical: too long and it dries out.",
            },
            {
                "step": 5,
                "description": "Tilt the pan to 45 degrees. Use the fork to fold the near third of the omelette to the centre, then roll/slide it onto a warmed plate, folding it into a neat oval.",
                "technique": "rolling",
                "duration_minutes": 0.5,
                "precision_notes": "Requires precise wrist control. Tap the pan handle with your fist to help release the omelette. The final shape should be a smooth, pale oval with no colour.",
            },
        ],
    },
    "bread": {
        "dish_name": "Artisan Bread (White Loaf)",
        "cuisine_type": "International",
        "difficulty": "medium",
        "estimated_time_minutes": 180,
        "key_ingredients": [
            "strong white bread flour (500g)",
            "water (340ml, at 35C)",
            "instant yeast (7g, one sachet)",
            "salt (10g)",
            "olive oil (1 tbsp, optional)",
        ],
        "cooking_techniques": [
            "mixing",
            "kneading",
            "proofing",
            "shaping",
            "scoring",
            "baking",
            "steam creation",
        ],
        "required_equipment": [
            "oven",
            "large mixing bowl",
            "work surface",
            "bench scraper",
            "sharp blade or lame (for scoring)",
            "baking tray or Dutch oven",
            "spray bottle (for steam)",
            "wire cooling rack",
            "kitchen thermometer",
        ],
        "temperature_requirements": {
            "water": "35C for activating yeast",
            "first_rise_environment": "24-28C, draft-free",
            "second_rise_environment": "24-28C",
            "oven": "230C with steam for first 15 minutes, then 210C without steam",
            "internal_done_temperature": "90-95C (measured with probe thermometer)",
        },
        "steps": [
            {
                "step": 1,
                "description": "Combine flour, yeast, and salt in a large bowl. Add water and mix until a shaggy dough forms.",
                "technique": "mixing",
                "duration_minutes": 3,
                "precision_notes": "Keep yeast and salt separate initially (salt inhibits yeast). Mix until no dry flour remains.",
            },
            {
                "step": 2,
                "description": "Turn out onto a clean surface and knead for 10-12 minutes until smooth, elastic, and passes the windowpane test.",
                "technique": "kneading",
                "duration_minutes": 11,
                "precision_notes": "Push forward with heel of hand, fold back, rotate 90 degrees, repeat. ~60 cycles per minute. Force: 10-20N. Dough should become smooth and spring back when poked.",
            },
            {
                "step": 3,
                "description": "Place dough in a lightly oiled bowl, cover with damp cloth. Let rise for 60-90 minutes until doubled in size.",
                "technique": "proofing",
                "duration_minutes": 75,
                "precision_notes": "Ideal temperature 24-28C. Poke test: finger dent should fill back slowly. If it springs back quickly, it needs more time.",
            },
            {
                "step": 4,
                "description": "Gently deflate dough, turn out, and shape into a round boule or oval batard by folding and tucking.",
                "technique": "shaping",
                "duration_minutes": 5,
                "precision_notes": "Handle gently to preserve gas bubbles. Create surface tension by tucking dough under itself and rotating. Final shape should be taut.",
            },
            {
                "step": 5,
                "description": "Place on floured baking tray or in a proofing basket. Cover and let rise for 45-60 minutes until nearly doubled.",
                "technique": "proofing",
                "duration_minutes": 50,
                "precision_notes": "Do not over-prove or bread will collapse in oven. Poke test: indent should fill back slowly with slight resistance.",
            },
            {
                "step": 6,
                "description": "Preheat oven to 230C. Score the top of the loaf with a sharp blade in a pattern of your choice, about 1cm deep.",
                "technique": "scoring",
                "duration_minutes": 1,
                "precision_notes": "Hold blade at 30-degree angle. Quick, confident slash in one motion (~5N force). Scoring controls expansion direction and creates the characteristic ear.",
            },
            {
                "step": 7,
                "description": "Place bread in oven. Spray water into oven or add ice cubes to a preheated tray for steam. Bake at 230C for 15 minutes with steam.",
                "technique": "baking",
                "duration_minutes": 15,
                "precision_notes": "Steam in the first phase creates a crispy crust. Open oven briefly to spray/add water, then close quickly.",
            },
            {
                "step": 8,
                "description": "Reduce temperature to 210C, remove steam source, and bake for a further 20-25 minutes until deep golden brown.",
                "technique": "baking",
                "duration_minutes": 22,
                "precision_notes": "Bread is done when internal temperature reaches 90-95C and it sounds hollow when tapped on the base.",
            },
            {
                "step": 9,
                "description": "Cool completely on a wire rack for at least 30 minutes before slicing.",
                "technique": "cooling",
                "duration_minutes": 30,
                "precision_notes": "Cutting hot bread compresses the crumb structure. Patience is essential. The crust will crackle as it cools.",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Cooking Techniques Database
# ---------------------------------------------------------------------------
# Detailed technique information with robotic feasibility assessments.

TECHNIQUE_DATABASE = {
    "boiling": {
        "technique": "boiling",
        "description": "Heating a liquid (usually water) to 100C and cooking food submerged in it. Requires monitoring water level and timing.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "low -- water self-regulates at 100C",
            "timing_sensitivity": "medium -- overcooking makes food mushy, undercooking leaves it raw",
            "force_control": "low -- just lowering items into water",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Simple to automate. Requires temperature sensor, timer, and a gripper or basket to lower/raise food. Main challenge is handling steam and draining.",
    },
    "chopping": {
        "technique": "chopping",
        "description": "Using a sharp knife to cut ingredients into pieces. Includes dicing (small cubes), mincing (very fine), julienning (matchstick strips), and rough chopping.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "none",
            "timing_sensitivity": "low",
            "force_control": "high -- must apply 5-30N of downward force through a blade with controlled motion to achieve consistent size without crushing",
        },
        "robotic_feasibility": "hard",
        "robotic_notes": "Requires a sharp tool end-effector, force feedback, computer vision for object positioning, and path planning. Consistent cut sizes are difficult. Different ingredients require different pressures and blade angles.",
    },
    "frying": {
        "technique": "frying",
        "description": "Cooking food in hot oil or fat in a pan. Includes shallow frying (2-3cm oil) and pan frying (thin layer of oil).",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "high -- oil temperature determines outcome (130-190C depending on task)",
            "timing_sensitivity": "high -- seconds matter, especially at high heat",
            "force_control": "medium -- flipping and moving food without splashing oil",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Temperature monitoring via IR sensor is straightforward. Main challenges: safely handling hot oil, flipping food, and managing splatter. Heat-resistant materials essential.",
    },
    "deep frying": {
        "technique": "deep frying",
        "description": "Fully submerging food in hot oil (160-190C). Used for chips, battered fish, doughnuts, etc.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "very high -- must maintain oil at precise temperature despite cold food lowering it",
            "timing_sensitivity": "high -- over-frying burns, under-frying leaves raw centres",
            "force_control": "medium -- lowering food slowly into hot oil, retrieving with strainer",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Significant safety hazard. Requires splash protection, precise temperature control, and careful lowering mechanism. Oil temperature recovery monitoring is essential.",
    },
    "baking": {
        "technique": "baking",
        "description": "Cooking food using dry heat in an enclosed oven, typically at 150-250C. Relies on even heat distribution.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "high -- oven must be at correct temperature before and during baking",
            "timing_sensitivity": "high -- a few minutes can make the difference between perfect and burnt",
            "force_control": "low -- mainly placing items in and removing from oven",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Straightforward to automate. Requires a gripper that can handle oven-safe containers, heat-resistant end-effector, oven door mechanism, temperature sensor, and precise timer.",
    },
    "whisking": {
        "technique": "whisking",
        "description": "Rapidly stirring or beating ingredients with a whisk to incorporate air, combine liquids, or create emulsions.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "low (varies by application)",
            "timing_sensitivity": "medium -- over-whisking can break emulsions or over-whip cream",
            "force_control": "medium -- speed and consistency matter more than force (100-300 RPM typical)",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Easily achieved with a rotary end-effector. Consistent speed and duration make this ideal for robots. Visual feedback for peak detection (e.g., stiff peaks) is the main challenge.",
    },
    "kneading": {
        "technique": "kneading",
        "description": "Working dough by repeatedly pushing, folding, and pressing with the heel of the hand to develop gluten structure.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "low -- dough temperature should stay around 24-28C",
            "timing_sensitivity": "medium -- under-kneading gives poor structure, over-kneading makes dough tough",
            "force_control": "high -- requires 10-20N of pushing force with specific push-fold-rotate rhythm at ~60 cycles/minute",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Commercial dough mixers already do this. For a humanoid approach, requires force-controlled dual-arm manipulation with compliance. Windowpane test assessment needs vision and stretch measurement.",
    },
    "stirring": {
        "technique": "stirring",
        "description": "Moving a utensil (spoon, spatula) in circular motions through food to mix, prevent sticking, or distribute heat evenly.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "varies by dish",
            "timing_sensitivity": "low to medium",
            "force_control": "low -- gentle circular motion, 2-5N",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Very simple to automate with a rotary or articulated arm holding a spoon. Consistent speed and path are easy for robots. Main consideration is utensil selection and immersion depth.",
    },
    "folding": {
        "technique": "folding",
        "description": "Gently incorporating light ingredients (e.g., whipped egg whites) into heavier mixtures using a slow, deliberate cut-and-fold motion to preserve air.",
        "difficulty": "hard",
        "precision_requirements": {
            "temperature_accuracy": "low",
            "timing_sensitivity": "medium -- too many folds deflates the mixture",
            "force_control": "very high -- must be extremely gentle (1-3N) with specific figure-of-eight or cut-and-fold motion. Over-mixing ruins the dish.",
        },
        "robotic_feasibility": "hard",
        "robotic_notes": "Requires precise force control and compliant motion. A stiff robot will deflate the mixture. Needs force/torque feedback on the end-effector and careful path planning for the fold pattern. Counting strokes and monitoring mixture volume change would help.",
    },
    "tossing": {
        "technique": "tossing",
        "description": "Lifting and flipping food in a pan or bowl using a quick wrist motion to mix and coat ingredients evenly.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "varies",
            "timing_sensitivity": "medium",
            "force_control": "high -- requires coordinated wrist-flick motion with the pan. Force and angle must be controlled to keep food in the pan.",
        },
        "robotic_feasibility": "hard",
        "robotic_notes": "Complex dynamic motion requiring wrist articulation and timing. Food trajectory is semi-predictable. Requires high-speed actuators and possibly vision feedback. Simpler alternative: use a stirring tool instead.",
    },
    "rolling": {
        "technique": "rolling",
        "description": "Using a rolling pin, bamboo mat, or hands to shape dough, sushi, or other foods into flat sheets or cylindrical forms.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "low",
            "timing_sensitivity": "low",
            "force_control": "high -- must apply even, consistent pressure (3-10N) across the full length. Uneven pressure creates inconsistent thickness.",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Flat rolling is achievable with a parallel-motion actuator and force control. Cylindrical rolling (e.g., sushi) is harder -- requires compliant, distributed pressure along a line. Thickness sensing via force feedback or vision helps.",
    },
    "slicing": {
        "technique": "slicing",
        "description": "Making thin, even cuts through ingredients using a sharp knife in a smooth drawing motion.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "none",
            "timing_sensitivity": "low",
            "force_control": "high -- must control blade angle, drawing speed, and downward force for even thickness. Sashimi slicing requires 1-2mm precision.",
        },
        "robotic_feasibility": "hard",
        "robotic_notes": "Requires sharp blade end-effector, force sensing, vision for positioning, and controlled drawing motion. Food fixturing (holding the item stable) is a separate challenge. Commercial food slicers handle this with fixed geometry.",
    },
    "spreading": {
        "technique": "spreading",
        "description": "Using a knife, spatula, or spoon to distribute a semi-liquid substance (sauce, frosting, butter) evenly over a surface.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "low (some spreads need specific temp for consistency)",
            "timing_sensitivity": "low",
            "force_control": "medium -- need consistent, gentle pressure (2-5N) and smooth motion to achieve even coverage without tearing the surface underneath.",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Achievable with a flat tool end-effector and force-controlled sweeping motion. Even coverage can be verified with vision. Compliant control helps avoid tearing delicate surfaces like bread or cake.",
    },
    "grating": {
        "technique": "grating",
        "description": "Rubbing food against a grater surface to produce fine shreds or powder. Used for cheese, citrus zest, nutmeg, etc.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "none (though cheese grates better cold)",
            "timing_sensitivity": "low",
            "force_control": "medium -- consistent downward pressure ~5N against grater while moving item in linear strokes. Must stop before reaching fingers/gripper.",
        },
        "robotic_feasibility": "easy",
        "robotic_notes": "Linear reciprocating motion against a fixed grater. Requires force feedback to maintain consistent pressure and a safe stopping distance. Gripper must hold irregularly shaped items securely.",
    },
    "scoring": {
        "technique": "scoring",
        "description": "Making shallow cuts on the surface of dough, meat, or fish for controlled expansion during cooking or for decoration.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "none",
            "timing_sensitivity": "low",
            "force_control": "high -- must cut to precise depth (5-10mm) without cutting through. Blade angle (30 degrees) and speed affect the result.",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Requires a sharp blade end-effector with precise depth control. Force/position hybrid control needed. Vision can help plan cut patterns. Consistent depth is the main challenge.",
    },
    "high-heat searing": {
        "technique": "high-heat searing",
        "description": "Cooking food very briefly at very high temperatures (250-300C) to create a caramelised crust via the Maillard reaction.",
        "difficulty": "medium",
        "precision_requirements": {
            "temperature_accuracy": "high -- surface must be 250-300C",
            "timing_sensitivity": "very high -- seconds matter. Sear for 30-90 seconds per side.",
            "force_control": "low -- mainly pressing food against hot surface",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Requires heat-resistant end-effector, fast timing, and IR temperature sensing. Smoke and splatter handling is important. Flipping requires coordinated tong or spatula manipulation.",
    },
    "stir-frying": {
        "technique": "stir-frying",
        "description": "Fast cooking in a very hot wok with small amounts of oil. Requires continuous tossing and rapid sequential addition of ingredients.",
        "difficulty": "hard",
        "precision_requirements": {
            "temperature_accuracy": "high -- wok must be 250-300C",
            "timing_sensitivity": "very high -- entire process takes 3-5 minutes with second-level precision",
            "force_control": "high -- rapid tossing at 2-3 motions per second, sequential ingredient addition",
        },
        "robotic_feasibility": "very_hard",
        "robotic_notes": "Extremely challenging due to combined requirements: very high temperature, rapid tossing dynamics, precise timing of ingredient additions, and smoke/splatter management. Would likely need a custom wok-flipping mechanism rather than a general-purpose arm.",
    },
    "plating": {
        "technique": "plating",
        "description": "Arranging finished food attractively on a plate for presentation.",
        "difficulty": "easy",
        "precision_requirements": {
            "temperature_accuracy": "low (warm plates for hot food)",
            "timing_sensitivity": "low",
            "force_control": "medium -- delicate placement of components without disturbing arrangement",
        },
        "robotic_feasibility": "medium",
        "robotic_notes": "Requires vision for placement accuracy, gentle gripping for delicate items, and some aesthetic sense (which could be template-driven). Saucing and garnishing add complexity.",
    },
}


# ---------------------------------------------------------------------------
# Equipment Specifications Database
# ---------------------------------------------------------------------------

EQUIPMENT_DATABASE = {
    "oven": {
        "name": "Conventional Oven",
        "type": "heating appliance",
        "typical_dimensions_cm": "60 x 60 x 60 (W x D x H)",
        "weight_range_kg": "30-60",
        "operating_temperature_range": "50-300C (some models up to 500C for pizza)",
        "power_requirements": "2000-3000W (electric) or gas supply",
        "key_features": [
            "thermostat with +/- 5C accuracy",
            "fan-assisted and conventional modes",
            "door with handle (pull force ~10N)",
            "internal light",
            "multiple shelf positions",
        ],
        "robotic_interaction_notes": "Robot needs heat-resistant end-effector to place/remove items. Oven door requires pull-open and push-close (10-15N). Interior is extremely hot -- keep non-heat-resistant parts clear.",
    },
    "pot": {
        "name": "Large Cooking Pot",
        "type": "cookware",
        "typical_dimensions_cm": "24cm diameter x 20cm height (6-8 litre capacity)",
        "weight_range_kg": "1.5-3.0 (empty), up to 10kg when full of liquid",
        "operating_temperature_range": "up to 100C for boiling water, 120-150C for oil",
        "power_requirements": "N/A (heated by hob)",
        "key_features": [
            "two side handles (grip span ~5cm)",
            "lid (with steam vent or knob handle)",
            "stainless steel or aluminium construction",
            "heat-conducting base",
        ],
        "robotic_interaction_notes": "Heavy when full -- requires high-payload gripper (10kg+). Two-handle lifting is safer and more stable. Hot surfaces require heat-resistant gripping. Pouring requires coordinated tilting with force feedback.",
    },
    "frying pan": {
        "name": "Frying Pan (Skillet)",
        "type": "cookware",
        "typical_dimensions_cm": "28cm diameter, 5cm depth, 40cm total length with handle",
        "weight_range_kg": "0.8-2.0 (cast iron up to 3.5kg)",
        "operating_temperature_range": "up to 300C (surface temperature for searing)",
        "power_requirements": "N/A (heated by hob)",
        "key_features": [
            "single long handle (18-22cm, for one-handed use)",
            "optional helper handle on opposite side",
            "non-stick, stainless, or cast-iron variants",
            "flat base for hob contact",
        ],
        "robotic_interaction_notes": "Single handle allows one-arm manipulation. Pan tossing requires wrist articulation and dynamic force control. Handle temperature may rise -- use heat-resistant gripper. Weight distribution is uneven (handle side is lighter).",
    },
    "knife": {
        "name": "Chef's Knife",
        "type": "cutting tool",
        "typical_dimensions_cm": "blade: 20cm length x 5cm height; total: 33cm with handle",
        "weight_range_kg": "0.15-0.30",
        "operating_temperature_range": "room temperature",
        "power_requirements": "N/A (manual tool)",
        "key_features": [
            "sharp blade with curved profile for rocking cuts",
            "ergonomic handle (grip diameter ~3cm)",
            "stainless or carbon steel blade",
            "blade angle typically 15-20 degrees per side",
        ],
        "robotic_interaction_notes": "SAFETY CRITICAL: extremely sharp. Requires secure grip (friction-enhanced gripper surface). Cutting force varies by ingredient (2-30N). Blade orientation and angle must be carefully controlled. Consider purpose-built cutting tools rather than mimicking human knife use.",
    },
    "wok": {
        "name": "Carbon Steel Wok",
        "type": "cookware",
        "typical_dimensions_cm": "36cm diameter, 12cm depth",
        "weight_range_kg": "1.0-2.0",
        "operating_temperature_range": "up to 350C+ (designed for very high heat)",
        "power_requirements": "requires high-BTU burner (ideally 15,000+ BTU / 4.5kW+)",
        "key_features": [
            "round bottom (or flat for domestic hobs)",
            "single long handle and optional ear handle",
            "thin carbon steel for rapid heat response",
            "naturally non-stick when properly seasoned",
        ],
        "robotic_interaction_notes": "Designed for dynamic cooking with tossing. Handle gets very hot. Extreme temperatures require heat-resistant materials. Wok tossing is one of the hardest motions to replicate robotically. Consider a fixed wok with mechanical stirrer instead.",
    },
    "mixer": {
        "name": "Stand Mixer",
        "type": "electric appliance",
        "typical_dimensions_cm": "35 x 25 x 35 (W x D x H)",
        "weight_range_kg": "5-12",
        "operating_temperature_range": "room temperature operation",
        "power_requirements": "300-1000W, standard mains electricity",
        "key_features": [
            "planetary mixing action",
            "multiple speed settings (typically 6-10)",
            "interchangeable attachments (whisk, paddle, dough hook)",
            "tilting head or bowl-lift design",
            "bowl capacity 4-7 litres",
        ],
        "robotic_interaction_notes": "Can operate semi-autonomously once set up. Robot interaction: loading/unloading bowl, changing attachments, setting speed dial. Head-tilt mechanism requires ~15N. A robot-controlled stand mixer is often simpler than trying to whisk with a robot arm.",
    },
    "chopping board": {
        "name": "Chopping Board",
        "type": "preparation surface",
        "typical_dimensions_cm": "45 x 30 x 3 (large)",
        "weight_range_kg": "0.5-3.0 (plastic to hardwood)",
        "operating_temperature_range": "room temperature",
        "power_requirements": "N/A",
        "key_features": [
            "flat, stable cutting surface",
            "non-slip base (or use a damp cloth underneath)",
            "colour-coded options for food safety (red=raw meat, green=vegetables, blue=fish)",
            "dishwasher safe (plastic) or hand-wash (wood)",
        ],
        "robotic_interaction_notes": "Must be rigidly fixed or clamped during cutting operations to prevent sliding. Non-slip mat underneath is essential. Provides a known, flat reference surface for robot path planning. Food positioning on the board is a vision task.",
    },
    "colander": {
        "name": "Colander / Strainer",
        "type": "draining tool",
        "typical_dimensions_cm": "24cm diameter x 14cm depth",
        "weight_range_kg": "0.3-0.8",
        "operating_temperature_range": "up to 100C (for draining boiling water)",
        "power_requirements": "N/A",
        "key_features": [
            "perforated bowl with multiple drainage holes",
            "two handles or a single long handle",
            "stands on a base or sits in a sink",
            "stainless steel, plastic, or silicone variants",
        ],
        "robotic_interaction_notes": "Used for transferring food + hot liquid from a pot. Requires coordinated two-arm operation: one arm holds colander, other pours pot. Hot steam rises when draining -- keep sensors and non-heat-resistant components clear.",
    },
    "rolling pin": {
        "name": "Rolling Pin",
        "type": "preparation tool",
        "typical_dimensions_cm": "45cm total length, 6cm diameter roller",
        "weight_range_kg": "0.5-1.5 (wood or marble)",
        "operating_temperature_range": "room temperature (marble pins can be chilled)",
        "power_requirements": "N/A",
        "key_features": [
            "cylindrical roller (fixed or free-spinning)",
            "handles on each end (or handleless French style)",
            "even weight distribution for consistent pressure",
            "wood, marble, or silicone variants",
        ],
        "robotic_interaction_notes": "Requires two-handed operation with even downward pressure (5-15N) while rolling forward and back. Consistent pressure across the full width is critical. A purpose-built flat press might be simpler for a robot than replicating human rolling pin technique.",
    },
    "cooking thermometer": {
        "name": "Digital Cooking Thermometer",
        "type": "measurement tool",
        "typical_dimensions_cm": "25cm probe length, small digital display",
        "weight_range_kg": "0.05-0.1",
        "operating_temperature_range": "measures -50C to 300C typically",
        "power_requirements": "battery (CR2032 or AAA)",
        "key_features": [
            "thin probe for insertion into food",
            "digital display with +/- 0.5C accuracy",
            "instant-read (2-3 second response)",
            "some models have wireless/Bluetooth connectivity",
        ],
        "robotic_interaction_notes": "Excellent robotic sensor. A temperature probe can be mounted directly on a robot arm end-effector for precise food temperature monitoring. Wireless models can transmit data directly to the robot's control system. Essential for safety-critical temperature checks.",
    },
}


# ===========================================================================
# MCP Tool Definitions
# ===========================================================================

@mcp.tool()
def analyse_dish(dish_name: str) -> str:
    """
    Analyse a dish and return a structured breakdown including ingredients,
    techniques, equipment, timing, and preparation steps.

    Parameters
    ----------
    dish_name : str
        The name of the dish to analyse (e.g., "pasta carbonara", "sushi rolls").

    Returns
    -------
    str
        A JSON-formatted string containing the full dish analysis, or a
        template for unknown dishes that the LLM can fill in.
    """
    # Normalise the input for lookup
    key = dish_name.strip().lower()

    # Try exact match first
    if key in DISH_DATABASE:
        dish = DISH_DATABASE[key]
        return json.dumps(dish, indent=2)

    # Try partial match (e.g., "carbonara" matches "pasta carbonara")
    for db_key, dish in DISH_DATABASE.items():
        if key in db_key or db_key in key:
            return json.dumps(dish, indent=2)

    # Unknown dish -- return a template
    template = {
        "dish_name": dish_name,
        "cuisine_type": "unknown -- please determine from dish name",
        "difficulty": "unknown",
        "estimated_time_minutes": "unknown",
        "key_ingredients": ["unknown -- please determine from your culinary knowledge"],
        "cooking_techniques": ["unknown -- please determine from your culinary knowledge"],
        "required_equipment": ["unknown -- please determine from your culinary knowledge"],
        "temperature_requirements": {
            "note": "unknown -- please determine appropriate temperatures"
        },
        "steps": [
            {
                "step": 1,
                "description": "unknown -- please break down the preparation into detailed steps",
                "technique": "unknown",
                "duration_minutes": "unknown",
                "precision_notes": "unknown",
            }
        ],
        "note": (
            f"'{dish_name}' is not in the pre-built database. Please use your "
            "culinary knowledge to fill in the details above, following the same "
            "structure as known dishes."
        ),
    }
    return json.dumps(template, indent=2)


@mcp.tool()
def get_cooking_techniques(dish_name: str) -> str:
    """
    Return a detailed breakdown of cooking techniques needed for a dish,
    including difficulty, precision requirements, and robotic feasibility.

    This is particularly useful for understanding what physical capabilities
    a robot would need to prepare the dish.

    Parameters
    ----------
    dish_name : str
        The name of the dish to look up techniques for.

    Returns
    -------
    str
        A JSON-formatted string listing each technique with its description,
        difficulty, precision requirements, and robotic feasibility rating.
    """
    # First, find the dish to get its technique list
    key = dish_name.strip().lower()
    dish = None

    if key in DISH_DATABASE:
        dish = DISH_DATABASE[key]
    else:
        for db_key, db_dish in DISH_DATABASE.items():
            if key in db_key or db_key in key:
                dish = db_dish
                break

    if dish is None:
        return json.dumps({
            "dish_name": dish_name,
            "error": f"Dish '{dish_name}' not found in database. Cannot retrieve technique details.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)

    # Gather technique details for this dish
    techniques_used = dish.get("cooking_techniques", [])
    result = {
        "dish_name": dish["dish_name"],
        "techniques": [],
    }

    for technique_name in techniques_used:
        normalised = technique_name.strip().lower().replace("-", " ")
        # Try to find in technique database
        # Check exact match, then variations with hyphens
        tech_info = None
        for tk, tv in TECHNIQUE_DATABASE.items():
            if normalised == tk or normalised in tk or tk in normalised:
                tech_info = tv
                break

        if tech_info:
            result["techniques"].append(tech_info)
        else:
            result["techniques"].append({
                "technique": technique_name,
                "description": f"No detailed data available for '{technique_name}'.",
                "difficulty": "unknown",
                "precision_requirements": {},
                "robotic_feasibility": "unknown",
                "robotic_notes": "No data available. Use culinary knowledge to assess.",
            })

    return json.dumps(result, indent=2)


@mcp.tool()
def get_equipment_specs(equipment_name: str) -> str:
    """
    Return specifications for a piece of kitchen equipment, including
    dimensions, weight, operating temperature, and notes for robotic
    interaction.

    Parameters
    ----------
    equipment_name : str
        The name of the equipment (e.g., "oven", "knife", "wok").

    Returns
    -------
    str
        A JSON-formatted string with the equipment specifications, or an
        error message if not found.
    """
    key = equipment_name.strip().lower()

    # Exact match
    if key in EQUIPMENT_DATABASE:
        return json.dumps(EQUIPMENT_DATABASE[key], indent=2)

    # Partial match
    for eq_key, eq_data in EQUIPMENT_DATABASE.items():
        if key in eq_key or eq_key in key:
            return json.dumps(eq_data, indent=2)

    # Also check against the 'name' field
    for eq_key, eq_data in EQUIPMENT_DATABASE.items():
        if key in eq_data["name"].lower():
            return json.dumps(eq_data, indent=2)

    return json.dumps({
        "error": f"Equipment '{equipment_name}' not found in database.",
        "available_equipment": list(EQUIPMENT_DATABASE.keys()),
        "hint": "Try one of the available equipment names listed above.",
    }, indent=2)


@mcp.tool()
def get_safety_requirements(dish_name: str) -> str:
    """
    Return food safety and kitchen safety considerations for preparing a dish.

    Covers temperature danger zones, allergen information, sharp tool
    handling, hot surface warnings, and timing requirements.

    Parameters
    ----------
    dish_name : str
        The name of the dish to get safety information for.

    Returns
    -------
    str
        A JSON-formatted string with comprehensive safety information.
    """
    key = dish_name.strip().lower()
    dish = None

    if key in DISH_DATABASE:
        dish = DISH_DATABASE[key]
    else:
        for db_key, db_dish in DISH_DATABASE.items():
            if key in db_key or db_key in key:
                dish = db_dish
                break

    if dish is None:
        return json.dumps({
            "dish_name": dish_name,
            "error": f"Dish '{dish_name}' not found in database.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)

    # Build safety analysis based on the dish's characteristics
    safety = {
        "dish_name": dish["dish_name"],
        "food_safety": {
            "temperature_danger_zone": (
                "Bacteria multiply rapidly between 5-63C. Cooked food should "
                "be kept above 63C or cooled below 5C within 2 hours."
            ),
            "specific_risks": [],
        },
        "kitchen_safety": {
            "sharp_tools": [],
            "hot_surfaces": [],
            "fire_and_burn_risks": [],
            "other_hazards": [],
        },
        "allergen_information": [],
        "timing_safety": [],
    }

    # Analyse ingredients for allergens
    ingredients_text = " ".join(dish["key_ingredients"]).lower()

    if "egg" in ingredients_text:
        safety["allergen_information"].append(
            "EGGS: Major allergen. Ensure eggs are fresh and properly cooked (>75C) unless recipe specifically calls for runny texture."
        )
    if "flour" in ingredients_text or "bread" in ingredients_text:
        safety["allergen_information"].append(
            "GLUTEN (WHEAT): Major allergen. Present in flour-based components. No substitution possible without altering the recipe significantly."
        )
    if "milk" in ingredients_text or "cream" in ingredients_text or "butter" in ingredients_text or "cheese" in ingredients_text or "buttermilk" in ingredients_text or "mozzarella" in ingredients_text:
        safety["allergen_information"].append(
            "DAIRY (MILK): Major allergen. Present in cheese, butter, cream, or milk-based ingredients."
        )
    if "prawn" in ingredients_text or "shrimp" in ingredients_text or "fish" in ingredients_text or "salmon" in ingredients_text or "tuna" in ingredients_text or "cod" in ingredients_text or "haddock" in ingredients_text:
        safety["allergen_information"].append(
            "FISH/SHELLFISH: Major allergen. Must be sashimi-grade if served raw. Store at 0-4C. Check for bones."
        )
        safety["food_safety"]["specific_risks"].append(
            "Raw fish must be sashimi-grade and stored at 0-4C. Histamine poisoning risk if fish is temperature-abused."
        )
    if "soy" in ingredients_text:
        safety["allergen_information"].append(
            "SOY: Major allergen. Present in soy sauce or soy-based ingredients."
        )
    if "peanut" in ingredients_text or "nut" in ingredients_text:
        safety["allergen_information"].append(
            "PEANUTS/TREE NUTS: Major allergen. Risk of anaphylaxis in sensitive individuals. Cross-contamination risk in shared kitchen."
        )

    # Analyse techniques for safety risks
    techniques = [t.lower() for t in dish["cooking_techniques"]]

    if any(t in techniques for t in ["chopping", "slicing", "cutting", "precision knife work", "scoring"]):
        safety["kitchen_safety"]["sharp_tools"].append(
            "Sharp knives in use. Keep fingers curled (claw grip). Cut away from body. Ensure knife is sharp (dull knives slip and cause more injuries). Secure chopping board with a damp cloth underneath."
        )

    if any(t in techniques for t in ["frying", "deep frying", "stir-frying", "high-heat searing"]):
        safety["kitchen_safety"]["hot_surfaces"].append(
            "Hot oil in use (130-300C depending on technique). Oil burns are severe. Never add water to hot oil. Keep a fire blanket nearby. Wear long sleeves."
        )
        safety["kitchen_safety"]["fire_and_burn_risks"].append(
            "Oil fire risk. NEVER use water on an oil fire. Smother with a fire blanket or lid. Keep pan handles turned inward to prevent knocking."
        )

    if any(t in techniques for t in ["boiling"]):
        safety["kitchen_safety"]["hot_surfaces"].append(
            "Boiling water (100C). Steam burns are as severe as contact burns. Lift lids away from face. Use oven gloves when handling hot pots."
        )

    if any(t in techniques for t in ["baking"]):
        safety["kitchen_safety"]["hot_surfaces"].append(
            "Oven at high temperature. Use oven gloves. Beware of steam when opening oven door. Keep children/pets away."
        )

    if "deep frying" in techniques or "deep frying" in " ".join(techniques):
        safety["kitchen_safety"]["fire_and_burn_risks"].append(
            "DEEP FRYING SPECIFIC: Never fill fryer more than one-third with oil. Lower food slowly to prevent splashing. "
            "Never leave hot oil unattended. Have a fire blanket within arm's reach. If oil smokes, turn off heat immediately."
        )

    # Check for raw meat/egg risks
    if "egg" in ingredients_text:
        if "raw" in ingredients_text or dish.get("difficulty") == "hard":
            safety["food_safety"]["specific_risks"].append(
                "Some preparations involve partially cooked eggs. Use pasteurised eggs if serving to vulnerable groups (elderly, pregnant, immunocompromised)."
            )

    if any(word in ingredients_text for word in ["beef", "chicken", "pork", "meat"]):
        safety["food_safety"]["specific_risks"].append(
            "Raw meat must be stored below 5C. Cook to safe internal temperatures: chicken 75C, beef 63C (medium), pork 71C. Prevent cross-contamination with separate chopping boards."
        )

    # Timing safety
    temps = dish.get("temperature_requirements", {})
    for temp_key, temp_value in temps.items():
        if any(word in str(temp_value).lower() for word in ["critical", "must", "never", "danger"]):
            safety["timing_safety"].append(f"{temp_key}: {temp_value}")

    # Add general timing warnings based on steps
    for step_data in dish.get("steps", []):
        notes = step_data.get("precision_notes", "")
        if any(word in notes.upper() for word in ["CRITICAL", "MUST NOT", "NEVER", "DANGER", "SAFETY"]):
            safety["timing_safety"].append(
                f"Step {step_data['step']}: {notes}"
            )

    # Add general safety note
    safety["general_notes"] = (
        "Always wash hands before and after handling food. Keep raw and cooked "
        "foods separate. Clean all surfaces and utensils between uses. Ensure "
        "adequate ventilation when cooking with high heat or strong-smelling "
        "ingredients."
    )

    return json.dumps(safety, indent=2)


# ===========================================================================
# Entry Point
# ===========================================================================

if __name__ == "__main__":
    mcp.run()
