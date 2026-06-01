SCENARIO_PACKS = {
    "vietnam_pilot": {
        "label": "Vietnam Pilot (Default)",
        "description": "Three-year arc with tightening allocation, sector-specific abatement, and limited offsets aligned with Vietnam's pilot ETS posture.",
        "num_years": 3,
        "penalty_rate": 301.0,
        "offset_usage_cap": 0.1,
        "offset_price": 25.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 80.0,
        "auction_price_ceiling": 300.0,
        "auction_share_of_cap": 0.12,
        "trade_expiry_seconds": 20,
        "allocation_factors": {1: 0.92, 2: 0.88, 3: 0.84},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.030,
                "cash": 1_500_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.022,
                "cash": 1_250_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.018,
                "cash": 1_050_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 10.0,
                    "cost": 90000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 7.0,
                    "cost": 65000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 8.0,
                    "cost": 72000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 5.0,
                    "cost": 50000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 6.0,
                    "cost": 46000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 4.0,
                    "cost": 38000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
    "high_pressure": {
        "label": "High Pressure",
        "description": "Sharper cap decline and higher penalty rate forces aggressive abatement and trading.",
        "num_years": 3,
        "penalty_rate": 401.0,
        "offset_usage_cap": 0.05,
        "offset_price": 40.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 100.0,
        "auction_price_ceiling": 400.0,
        "auction_share_of_cap": 0.15,
        "trade_expiry_seconds": 20,
        "allocation_factors": {1: 0.90, 2: 0.82, 3: 0.74},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.035,
                "cash": 1_400_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.025,
                "cash": 1_150_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.020,
                "cash": 950_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 10.0,
                    "cost": 90000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 7.0,
                    "cost": 65000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 8.0,
                    "cost": 72000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 5.0,
                    "cost": 50000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 6.0,
                    "cost": 46000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 4.0,
                    "cost": 38000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
    "generous": {
        "label": "Generous Allocation",
        "description": "Gentler cap decline with lower penalties, suitable for introductory workshops where the learning focus is on market mechanics.",
        "num_years": 3,
        "penalty_rate": 251.0,
        "offset_usage_cap": 0.15,
        "offset_price": 18.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 50.0,
        "auction_price_ceiling": 250.0,
        "auction_share_of_cap": 0.10,
        "trade_expiry_seconds": 25,
        "allocation_factors": {1: 0.95, 2: 0.92, 3: 0.89},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.025,
                "cash": 1_600_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.018,
                "cash": 1_350_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.015,
                "cash": 1_150_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 12.0,
                    "cost": 85000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 8.0,
                    "cost": 55000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 9.0,
                    "cost": 68000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 6.0,
                    "cost": 42000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 7.0,
                    "cost": 38000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 5.0,
                    "cost": 32000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
    "solo_easy": {
        "label": "Solo Easy (Generous)",
        "description": "20-year solo game with gentle allocation decline, low penalty, and generous offsets. Suitable for first-time players.",
        "num_years": 20,
        "penalty_rate": 201.0,
        "offset_usage_cap": 0.18,
        "offset_price": 18.0,
        "auction_count_per_year": 1,
        "auction_price_floor": 50.0,
        "auction_price_ceiling": 200.0,
        "auction_share_of_cap": 0.08,
        "trade_expiry_seconds": 60,
        "allocation_factors": {y: round(max(0.68, 1.0 - (y - 1) * 0.0175), 4) for y in range(1, 21)},
        "company_library": [
            {"company_name": "Red River Thermal", "sector": "thermal_power", "baseline_emissions": 120.0, "growth_rate": 0.020, "cash": 1_800_000.0},
            {"company_name": "Hai Phong Steel", "sector": "steel", "baseline_emissions": 95.0, "growth_rate": 0.015, "cash": 1_500_000.0},
            {"company_name": "Da Nang Cement", "sector": "cement", "baseline_emissions": 88.0, "growth_rate": 0.012, "cash": 1_300_000.0},
            {"company_name": "Binh Duong Textiles", "sector": "thermal_power", "baseline_emissions": 45.0, "growth_rate": 0.018, "cash": 900_000.0},
            {"company_name": "Vung Tau Refinery", "sector": "steel", "baseline_emissions": 65.0, "growth_rate": 0.020, "cash": 1_100_000.0},
        ],
        "abatement_catalog": {
            "thermal_power": [
                {"measure_id": "tp_heat_rate_upgrade", "label": "Heat-rate upgrade", "abatement_amount": 12.0, "cost": 80000.0, "activation_timing": "immediate"},
                {"measure_id": "tp_cofiring_preparation", "label": "Biomass cofiring", "abatement_amount": 10.0, "cost": 55000.0, "activation_timing": "next_year"},
                {"measure_id": "tp_solar_hybrid", "label": "Solar hybrid integration", "abatement_amount": 8.0, "cost": 70000.0, "activation_timing": "next_year"},
            ],
            "steel": [
                {"measure_id": "st_waste_heat_recovery", "label": "Waste heat recovery", "abatement_amount": 10.0, "cost": 65000.0, "activation_timing": "immediate"},
                {"measure_id": "st_scrap_optimization", "label": "Scrap ratio optimization", "abatement_amount": 6.0, "cost": 45000.0, "activation_timing": "next_year"},
            ],
            "cement": [
                {"measure_id": "ce_blended_clinker_shift", "label": "Blended clinker shift", "abatement_amount": 8.0, "cost": 42000.0, "activation_timing": "immediate"},
                {"measure_id": "ce_kiln_control_upgrade", "label": "Kiln control upgrade", "abatement_amount": 5.0, "cost": 35000.0, "activation_timing": "next_year"},
            ],
        },
    },
    "solo_standard": {
        "label": "Solo Standard",
        "description": "15-year solo game with moderate cap decline and standard penalties. Balanced challenge for experienced workshop participants.",
        "num_years": 15,
        "penalty_rate": 325.0,
        "offset_usage_cap": 0.10,
        "offset_price": 28.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 80.0,
        "auction_price_ceiling": 300.0,
        "auction_share_of_cap": 0.12,
        "trade_expiry_seconds": 45,
        "allocation_factors": {y: round(max(0.42, 1.0 - (y - 1) * 0.031), 4) for y in range(1, 16)},
        "company_library": [
            {"company_name": "Red River Thermal", "sector": "thermal_power", "baseline_emissions": 120.0, "growth_rate": 0.025, "cash": 1_500_000.0},
            {"company_name": "Hai Phong Steel", "sector": "steel", "baseline_emissions": 95.0, "growth_rate": 0.020, "cash": 1_250_000.0},
            {"company_name": "Da Nang Cement", "sector": "cement", "baseline_emissions": 88.0, "growth_rate": 0.016, "cash": 1_050_000.0},
            {"company_name": "Quang Ninh Mining", "sector": "thermal_power", "baseline_emissions": 55.0, "growth_rate": 0.022, "cash": 950_000.0},
        ],
        "abatement_catalog": {
            "thermal_power": [
                {"measure_id": "tp_heat_rate_upgrade", "label": "Heat-rate upgrade", "abatement_amount": 10.0, "cost": 90000.0, "activation_timing": "immediate"},
                {"measure_id": "tp_cofiring_preparation", "label": "Biomass cofiring", "abatement_amount": 7.0, "cost": 65000.0, "activation_timing": "next_year"},
            ],
            "steel": [
                {"measure_id": "st_waste_heat_recovery", "label": "Waste heat recovery", "abatement_amount": 8.0, "cost": 72000.0, "activation_timing": "immediate"},
                {"measure_id": "st_scrap_optimization", "label": "Scrap ratio optimization", "abatement_amount": 5.0, "cost": 50000.0, "activation_timing": "next_year"},
            ],
            "cement": [
                {"measure_id": "ce_blended_clinker_shift", "label": "Blended clinker shift", "abatement_amount": 6.0, "cost": 46000.0, "activation_timing": "immediate"},
                {"measure_id": "ce_kiln_control_upgrade", "label": "Kiln control upgrade", "abatement_amount": 4.0, "cost": 38000.0, "activation_timing": "next_year"},
            ],
        },
    },
    "solo_hard": {
        "label": "Solo Hard (Aggressive)",
        "description": "10-year solo game with steep cap decline, high penalty, and tight offset access. Designed for experienced ETS players.",
        "num_years": 10,
        "penalty_rate": 520.0,
        "offset_usage_cap": 0.03,
        "offset_price": 48.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 100.0,
        "auction_price_ceiling": 450.0,
        "auction_share_of_cap": 0.18,
        "trade_expiry_seconds": 30,
        "allocation_factors": {y: round(max(0.22, 1.0 - (y - 1) * 0.062), 4) for y in range(1, 11)},
        "company_library": [
            {"company_name": "Red River Thermal", "sector": "thermal_power", "baseline_emissions": 120.0, "growth_rate": 0.035, "cash": 1_400_000.0},
            {"company_name": "Hai Phong Steel", "sector": "steel", "baseline_emissions": 95.0, "growth_rate": 0.028, "cash": 1_150_000.0},
            {"company_name": "Da Nang Cement", "sector": "cement", "baseline_emissions": 88.0, "growth_rate": 0.024, "cash": 950_000.0},
            {"company_name": "Quang Ninh Mining", "sector": "thermal_power", "baseline_emissions": 55.0, "growth_rate": 0.030, "cash": 850_000.0},
            {"company_name": "Dong Nai Chemicals", "sector": "cement", "baseline_emissions": 40.0, "growth_rate": 0.025, "cash": 750_000.0},
        ],
        "abatement_catalog": {
            "thermal_power": [
                {"measure_id": "tp_heat_rate_upgrade", "label": "Heat-rate upgrade", "abatement_amount": 10.0, "cost": 95000.0, "activation_timing": "immediate"},
                {"measure_id": "tp_cofiring_preparation", "label": "Biomass cofiring", "abatement_amount": 6.0, "cost": 70000.0, "activation_timing": "next_year"},
            ],
            "steel": [
                {"measure_id": "st_waste_heat_recovery", "label": "Waste heat recovery", "abatement_amount": 7.0, "cost": 78000.0, "activation_timing": "immediate"},
                {"measure_id": "st_scrap_optimization", "label": "Scrap ratio optimization", "abatement_amount": 4.0, "cost": 55000.0, "activation_timing": "next_year"},
            ],
            "cement": [
                {"measure_id": "ce_blended_clinker_shift", "label": "Blended clinker shift", "abatement_amount": 5.0, "cost": 50000.0, "activation_timing": "immediate"},
                {"measure_id": "ce_kiln_control_upgrade", "label": "Kiln control upgrade", "abatement_amount": 3.0, "cost": 42000.0, "activation_timing": "next_year"},
            ],
        },
    },
    "solo_tutorial": {
        "label": "Solo Tutorial",
        "description": "Three-year guided tutorial with generous allocation and fixed teaching moments.",
        "num_years": 3,
        "penalty_rate": 150.0,
        "offset_usage_cap": 0.20,
        "offset_price": 15.0,
        "auction_count_per_year": 0,
        "auction_price_floor": 40.0,
        "auction_price_ceiling": 120.0,
        "auction_share_of_cap": 0.0,
        "trade_expiry_seconds": 120,
        "allocation_factors": {1: 1.02, 2: 0.98, 3: 0.94},
        "company_library": [
            {"company_name": "Tutorial Thermal", "sector": "thermal_power", "baseline_emissions": 90.0, "growth_rate": 0.01, "cash": 900000.0},
            {"company_name": "Tutorial Steel", "sector": "steel", "baseline_emissions": 70.0, "growth_rate": 0.01, "cash": 850000.0},
            {"company_name": "Tutorial Cement", "sector": "cement", "baseline_emissions": 65.0, "growth_rate": 0.01, "cash": 820000.0}
        ],
        "abatement_catalog": {
            "thermal_power": [
                {"measure_id": "tp_tutorial_efficiency", "label": "Boiler efficiency tune-up", "abatement_amount": 9.0, "cost": 30000.0, "activation_timing": "immediate"},
                {"measure_id": "tp_tutorial_cofire", "label": "Small biomass cofiring pilot", "abatement_amount": 5.0, "cost": 22000.0, "activation_timing": "next_year"}
            ],
            "steel": [
                {"measure_id": "st_tutorial_recovery", "label": "Waste heat capture", "abatement_amount": 7.0, "cost": 26000.0, "activation_timing": "immediate"}
            ],
            "cement": [
                {"measure_id": "ce_tutorial_blend", "label": "Higher blended clinker", "abatement_amount": 6.0, "cost": 24000.0, "activation_timing": "immediate"}
            ]
        }
    },
}

TECH_UNLOCK_TEMPLATES = {
    "default": {
        "measure_label": "Process Optimization",
        "abatement_amount": 5.0,
        "cost": 40000.0,
        "activation_timing": "immediate",
    },
    "solar_subsidy": {
        "measure_label": "Rooftop Solar Installation",
        "abatement_amount": 8.0,
        "cost": 60000.0,
        "activation_timing": "immediate",
    },
    "heat_recovery": {
        "measure_label": "Heat Recovery Optimizer",
        "abatement_amount": 6.0,
        "cost": 40000.0,
        "activation_timing": "immediate",
    },
    "carbon_capture": {
        "measure_label": "Carbon Capture Pilot",
        "abatement_amount": 15.0,
        "cost": 150000.0,
        "activation_timing": "next_year",
    },
    "green_hydrogen": {
        "measure_label": "Green Hydrogen Steelmaking",
        "abatement_amount": 20.0,
        "cost": 200000.0,
        "activation_timing": "next_year",
    },
    "offshore_wind": {
        "measure_label": "Offshore Wind PPA",
        "abatement_amount": 12.0,
        "cost": 100000.0,
        "activation_timing": "next_year",
    },
    "smart_grid": {
        "measure_label": "Smart Grid Connection",
        "abatement_amount": 4.0,
        "cost": 30000.0,
        "activation_timing": "next_year",
    },
    "waste_to_energy": {
        "measure_label": "Waste Heat Recovery",
        "abatement_amount": 5.0,
        "cost": 35000.0,
        "activation_timing": "immediate",
    },
    "circular_materials": {
        "measure_label": "Circular Material Inputs",
        "abatement_amount": 5.0,
        "cost": 25000.0,
        "activation_timing": "immediate",
    },
    "renewable_compliance": {
        "measure_label": "Renewable Energy Compliance",
        "abatement_amount": 7.0,
        "cost": 55000.0,
        "activation_timing": "immediate",
    },
    "industrial_gas_capture": {
        "measure_label": "Industrial Gas Capture",
        "abatement_amount": 6.0,
        "cost": 45000.0,
        "activation_timing": "next_year",
    },
    "renewable_certificates": {
        "measure_label": "Renewable Energy Certificates",
        "abatement_amount": 3.0,
        "cost": 20000.0,
        "activation_timing": "immediate",
    },
}

SHOCK_CATALOG = {
    "emissions_spike": {
        "label": "Emissions Spike",
        "description": "Increase projected emissions for all companies in the current year by a percentage, simulating an unexpected production surge.",
        "applies_to": "all_companies",
    },
    "allowance_withdrawal": {
        "label": "Allowance Withdrawal",
        "description": "Reduce current allowance holdings by a percentage, simulating a regulatory correction or pre-verification adjustment.",
        "applies_to": "all_companies",
    },
    "cost_shock": {
        "label": "Cost Shock",
        "description": "Reduce cash for all companies by a percentage, simulating an external financial shock.",
        "applies_to": "all_companies",
    },
    "offset_supply_change": {
        "label": "Offset Supply Change",
        "description": "Change the offset usage cap for the current year, simulating policy changes to offset eligibility.",
        "applies_to": "session_wide",
    },
    "tech_unlock": {
        "label": "Technology Unlock",
        "description": "Add a new abatement measure to a sector's catalog mid-game, making it available to all companies in that sector.",
        "applies_to": "all_companies",
    },
    "fdi_proposal": {
        "label": "FDI Inflow",
        "description": "Foreign direct investment provides a cash infusion proportional to current holdings, boosting financial resources.",
        "applies_to": "all_companies",
    },
    "cbam_threat": {
        "label": "CBAM Pressure",
        "description": "Carbon border adjustment mechanism increases compliance costs for exposed sectors, modeled as a proportional penalty increase.",
        "applies_to": "session_wide",
    },
    "election_pressure": {
        "label": "Election / Policy Pressure",
        "description": "Political pressure modifies future allocation factors, tightening or loosening the cap trajectory for upcoming years.",
        "applies_to": "session_wide",
    },
    "allowance_boost": {
        "label": "Allowance Boost",
        "description": "Additional allowances become available to all companies proportional to their current holdings.",
        "applies_to": "all_companies",
    },
    "cash_boost": {
        "label": "Cash Injection",
        "description": "External funding provides a cash boost proportional to current holdings.",
        "applies_to": "all_companies",
    },
}
