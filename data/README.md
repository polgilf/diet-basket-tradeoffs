# Data inputs and provenance

The 16 Excel workbooks in this directory are the analytical inputs used by the model. They contain food-item, food-group, population-group, and Cambodian regional aggregates; they contain no names, contact details, household identifiers, or individual-level observations.

| File | Content | Primary provenance |
|---|---|---|
| `afe_factors.xlsx` | Adult-female-equivalent factors | WFP ENHANCE inputs |
| `current_environmental_impact.xlsx` | Regional current-diet environmental aggregates | Derived model input; source methods described in the manuscript |
| `current_food_expenditure.xlsx` | Regional expenditure percentiles | Cambodia Socio-Economic Survey 2021 aggregates (NIS, 2022) |
| `food_consumption.xlsx` | Sub-food-group consumption distributions by region | Cambodia Socio-Economic Survey 2021 aggregates (NIS, 2022) |
| `food_environmental.xlsx` | Environmental coefficients by food item | Poore and Nemecek (2018), with Cambodia-specific adjustments for rice and freshwater fish |
| `food_group_lower_limits.xlsx` | Food-group minimum quantities | Study model parameters |
| `food_group_percentages.xlsx` | Healthy Diet Basket energy-share bounds | Herforth et al. (2022) |
| `food_items_match.xlsx` | Food list and group/sub-group mappings | Fill the Nutrient Gap, Cambodia (WFP, UNICEF, and CARD, 2023) |
| `food_nutritional_composition.xlsx` | Nutrient composition by food item | Food-composition sources for Indonesia, Bangladesh, Kenya, USDA, West Africa, and Mexico, harmonized for the FNG analysis |
| `food_prices.xlsx` | March-April 2022 retail prices by food item and region | Fill the Nutrient Gap, Cambodia (WFP, UNICEF, and CARD, 2023) |
| `food_subgroup_colors.xlsx` | Plot color mapping | Study visualization parameter |
| `food_subgroup_importance.xlsx` | Dietary-continuity importance weights | Study model parameters |
| `food_subgroup_lower_limits.xlsx` | Sub-food-group minimum quantities | Study model parameters |
| `nutrient_match.xlsx` | Nutrient-name and constraint mapping | Study data-harmonization table |
| `nutritional_requirements.xlsx` | Nutrient reference values by population group | WHO and FAO (2004), Institute of Medicine (2005), and EFSA (2017), consolidated through WFP ENHANCE |
| `offal_food_items.xlsx` | Foods subject to the per-item 10 g/day cap | Study model parameter |

All quantities used in the paper are harmonized to a woman of reproductive age with an adult-female-equivalent factor of 1.0. See the manuscript methods and supplementary Tables S1-S4 for the complete methodological definitions and citations.

## Privacy review

An automated and structural review on 7 September 2026 found no email addresses, telephone numbers, direct identifiers, hidden worksheets, external workbook links, or individual/household-level rows. Workbook creator metadata names the repository author or source team in some files; this is consistent with this public, author-identified release.

## Reuse and third-party rights

The repository's MIT licence applies to original source code, not automatically to third-party data or source databases represented in these derived workbooks. Citations establish provenance but do not themselves establish redistribution permission. Users must cite the original sources and comply with their applicable terms.

The authors must confirm that their agreements with WFP and the underlying data providers permit public redistribution of these transformed inputs. If any agreement does not, the affected workbook must be replaced by access instructions or another shareable reproducibility artifact before the submission release is finalized.