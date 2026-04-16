"""
Industrial uses data module.

Provides common industrial and commercial applications for all elements.
Organized by use category and relevance.
"""

__all__ = ["get_industrial_uses", "INDUSTRIAL_USES"]

# Industrial uses data: symbol -> list of use dicts with category and description
INDUSTRIAL_USES = {
    "H": [
        {"category": "Chemical synthesis", "use": "Ammonia production (Haber process)"},
        {"category": "Energy", "use": "Fuel for rockets and clean energy applications"},
        {"category": "Metallurgy", "use": "Steel and metal welding, reducing metal ores"},
    ],
    "He": [
        {"category": "Cryogenics", "use": "Cooling superconducting magnets in MRI machines"},
        {"category": "Aerospace", "use": "Pressurization of spacecraft and rocket fuel tanks"},
        {"category": "Medical", "use": "Breathing mixtures for deep-sea diving"},
    ],
    "Li": [
        {"category": "Batteries", "use": "Lithium-ion rechargeable batteries for electronics"},
        {"category": "Ceramics", "use": "Glass and ceramics manufacturing"},
        {"category": "Pharmaceuticals", "use": "Treatment for bipolar disorder"},
    ],
    "Be": [
        {"category": "Aerospace", "use": "Aircraft components due to high strength-to-weight ratio"},
        {"category": "X-ray equipment", "use": "Windows for X-ray tubes"},
        {"category": "Nuclear", "use": "Neutron moderator in nuclear reactors"},
    ],
    "B": [
        {"category": "Glass", "use": "Borosilicate glass for laboratory and kitchenware"},
        {"category": "Detergents", "use": "Borax in laundry products"},
        {"category": "Composites", "use": "Boron fibers in aerospace materials"},
    ],
    "C": [
        {"category": "Steel", "use": "Carbon steel production (90% of all steel)"},
        {"category": "Energy", "use": "Coal for power generation and heating"},
        {"category": "Diamonds", "use": "Cutting tools, jewelry, high-pressure research"},
    ],
    "N": [
        {"category": "Fertilizers", "use": "Ammonia and nitrate-based agricultural fertilizers"},
        {"category": "Explosives", "use": "TNT, dynamite, ammonium nitrate explosives"},
        {"category": "Chemical synthesis", "use": "Nylon and other nitrogen-containing polymers"},
    ],
    "O": [
        {"category": "Medical", "use": "Oxygen therapy for respiratory patients"},
        {"category": "Chemical synthesis", "use": "Oxidation reactions in chemical industry"},
        {"category": "Combustion", "use": "Essential for all fuel burning and welding"},
    ],
    "Na": [
        {"category": "Chemicals", "use": "Sodium hydroxide (caustic soda) in paper and textile production"},
        {"category": "Food", "use": "Sodium chloride for salt production and food preservation"},
        {"category": "Glass", "use": "Soda ash (sodium carbonate) in glass manufacturing"},
    ],
    "Mg": [
        {"category": "Alloys", "use": "Lightweight aluminum-magnesium alloys for aerospace"},
        {"category": "Metallurgy", "use": "Reduction of heavy metal ores"},
        {"category": "Medical", "use": "Magnesium sulfate (Epsom salt) for healthcare"},
    ],
    "Al": [
        {"category": "Aerospace", "use": "Aircraft and spacecraft structural materials"},
        {"category": "Packaging", "use": "Aluminum foil and beverage cans"},
        {"category": "Electrical", "use": "Electrical transmission cables due to high conductivity"},
    ],
    "Si": [
        {"category": "Electronics", "use": "Semiconductor material for computer chips and solar cells"},
        {"category": "Glass", "use": "Silicon dioxide (silica) in glass production"},
        {"category": "Construction", "use": "Concrete and brick production"},
    ],
    "P": [
        {"category": "Fertilizers", "use": "Phosphate fertilizers (phosphoric acid)"},
        {"category": "Chemicals", "use": "Phosphorus compounds in detergents and flame retardants"},
        {"category": "Military", "use": "Incendiary ammunition and smoke screens"},
    ],
    "S": [
        {"category": "Chemicals", "use": "Sulfuric acid production (largest industrial chemical)"},
        {"category": "Rubber", "use": "Vulcanization of rubber for tires and gaskets"},
        {"category": "Medicine", "use": "Sulfur-based compounds for skin treatments"},
    ],
    "Cl": [
        {"category": "Water treatment", "use": "Disinfection of drinking water and swimming pools"},
        {"category": "PVC", "use": "Production of polyvinyl chloride plastic"},
        {"category": "Chemicals", "use": "Hydrochloric acid and other industrial chemicals"},
    ],
    "K": [
        {"category": "Fertilizers", "use": "Potassium compounds as essential plant nutrients"},
        {"category": "Chemicals", "use": "Potassium hydroxide in soap and detergent production"},
        {"category": "Medical", "use": "Potassium salts for treating potassium deficiency"},
    ],
    "Ca": [
        {"category": "Construction", "use": "Limestone and calcium carbonate in cement and concrete"},
        {"category": "Steel", "use": "Calcium additives in steelmaking"},
        {"category": "Medical", "use": "Calcium supplements for bone health"},
    ],
    "Fe": [
        {"category": "Steel", "use": "Primary component of steel (about 99% of global metal production)"},
        {"category": "Construction", "use": "Reinforced concrete and structural components"},
        {"category": "Medical", "use": "Iron supplements for treating anemia"},
    ],
    "Cu": [
        {"category": "Electrical", "use": "Electrical wiring and power distribution cables"},
        {"category": "Plumbing", "use": "Water and heating pipes in buildings"},
        {"category": "Electronics", "use": "Circuit boards and electronic components"},
    ],
    "Zn": [
        {"category": "Galvanization", "use": "Coating steel to prevent rust"},
        {"category": "Brass", "use": "Brass alloy for decorative and functional items"},
        {"category": "Medical", "use": "Zinc supplements for immune system support"},
    ],
    "Ag": [
        {"category": "Electronics", "use": "Silver contacts in switches and circuit boards"},
        {"category": "Photography", "use": "Silver halide in photographic film (legacy use)"},
        {"category": "Jewelry", "use": "Sterling silver for decorative and valuable items"},
    ],
    "Sn": [
        {"category": "Solder", "use": "Tin-lead solder for joining electronic components"},
        {"category": "Plating", "use": "Tin plating to prevent corrosion of steel"},
        {"category": "Bronze", "use": "Bronze alloys for decorative objects and bells"},
    ],
    "I": [
        {"category": "Medical", "use": "Iodine disinfectant for wounds and skin sterilization"},
        {"category": "Nutrition", "use": "Iodized salt for preventing iodine deficiency diseases"},
        {"category": "Photography", "use": "Silver iodide in photographic and cloud seeding"},
    ],
    "Pb": [
        {"category": "Batteries", "use": "Lead-acid batteries in vehicles"},
        {"category": "Radiation shielding", "use": "Lead barriers in X-ray and nuclear facilities"},
        {"category": "Paints", "use": "Lead compounds as pigments (restricted in modern use)"},
    ],
    "U": [
        {"category": "Nuclear energy", "use": "Fuel for nuclear power plants"},
        {"category": "Military", "use": "Nuclear weapons (fissile material)"},
        {"category": "Industrial", "use": "Uranium enrichment for research and medical isotopes"},
    ],
    "Co": [
        {"category": "Alloys", "use": "Cobalt in high-strength super-alloys for jet engines"},
        {"category": "Magnets", "use": "Cobalt in powerful permanent magnets"},
        {"category": "Medical", "use": "Cobalt-60 for cancer radiotherapy"},
    ],
    "Ni": [
        {"category": "Stainless steel", "use": "Nickel in corrosion-resistant stainless steel"},
        {"category": "Batteries", "use": "Nickel-cadmium and nickel-metal hydride batteries"},
        {"category": "Plating", "use": "Nickel plating for protective and decorative coating"},
    ],
    "Cr": [
        {"category": "Stainless steel", "use": "Chromium for corrosion resistance in steel"},
        {"category": "Leather tanning", "use": "Chromium salts in leather manufacturing"},
        {"category": "Paints", "use": "Chromium compounds as pigments and dyes"},
    ],
    "Th": [
        {"category": "Nuclear", "use": "Thorium-232 fuel in next-generation nuclear reactors"},
        {"category": "Welding", "use": "Thoriated tungsten electrodes for TIG welding"},
        {"category": "Industrial", "use": "Thorium compounds in catalysts and refractories"},
    ],
    "Br": [
        {"category": "Flame retardants", "use": "Bromine compounds in fire-resistant textiles and foams"},
        {"category": "Pharmaceuticals", "use": "Bromine in various medicinal compounds"},
        {"category": "Photography", "use": "Silver bromide in photographic emulsions"},
    ],
    "Au": [
        {"category": "Jewelry", "use": "Gold for luxury and decorative items"},
        {"category": "Electronics", "use": "Gold plating on circuit boards and connectors"},
        {"category": "Medicine", "use": "Gold salts in arthritis treatment"},
    ],
    "Pt": [
        {"category": "Catalysis", "use": "Platinum catalysts in chemical industry and vehicles"},
        {"category": "Jewelry", "use": "Platinum for luxury items and watches"},
        {"category": "Electronics", "use": "Platinum electrodes in various applications"},
    ],
    "W": [
        {"category": "Light bulbs", "use": "Tungsten filaments in incandescent bulbs"},
        {"category": "Alloys", "use": "High-strength tungsten in aerospace and military"},
        {"category": "Electronics", "use": "Tungsten contacts and electrodes"},
    ],
    "Mo": [
        {"category": "Steel", "use": "Molybdenum alloys for high-temperature and corrosion resistance"},
        {"category": "Catalysts", "use": "Molybdenum catalysts in petroleum refining"},
        {"category": "Lubricants", "use": "Molybdenum disulfide as dry lubricant"},
    ],
}


def get_industrial_uses(symbol):
    """
    Get list of industrial and commercial uses for an element.

    Args:
        symbol: Chemical symbol (e.g., 'Fe', 'Cu', 'Al')

    Returns:
        List of use dicts with keys: category, use. Empty list if element not found.
    """
    return INDUSTRIAL_USES.get(symbol, [])
