# nutrition_targets.md (example)

## Status
v4. Dynamic recalibration model — bot composes meals from real ingredients, sized to hit the running target. Calibrated to match workout.md v2.

---

# Part 1: Targets

## Operator baseline
- Height: [height]
- Starting weight: [weight]
- Goal: [X] kg by [date]

## Daily macro targets — Phase 1

| Macro | Target | Rationale |
|---|---|---|
| Calories | [X] kcal/day | Maintenance ~[Y] + surplus ~[Z], projects [rate] kg/week gain |
| Protein | [X] g | [X] g/kg target bodyweight |
| Carbs | [X] g | Fuel for [N] lifting days/week |
| Fat | [X] g | [X]% of calories, hormonal floor |
| Water | [X] L | |

## Daily macro targets — Phase 2
Escalate at week [N] if weekly bodyweight gain has been less than [X] kg/week.

| Macro | Target |
|---|---|
| Calories | [X] kcal/day |
| Protein | [X] g |
| Carbs | [X] g |
| Fat | [X] g |

## Meal schedule

| Slot | Time | Target kcal | Target protein |
|---|---|---|---|
| Breakfast | [time] | [X] | [X]g |
| Snack 1 | [time] | [X] | [X]g |
| Lunch | [time] | [X] | [X]g |
| Pre-lift snack | [time] | [X] | [X]g |
| Post-lift dinner | [time] | [X] | [X]g |
| Pre-bed shake | [time] | [X] | [X]g |
| Total | | [X] | [X]g |

---

# Part 2: Hard rules

- Daily protein floor: [X]g. If under [Y]g by [time], force a whey shake.
- Minimum [N] meals/day.
- Pre-bed shake every training day.
- Soda cap: [N]/day, hard cutoff at [time].
- Eat-out rule: [e.g. no weekday eat-out].
- Eat within 90 min post-lift.
- No alcohol on training days.

---

# Part 3: The recalibration loop

The bot does not run hard-coded if/then rules. It does live arithmetic against the running daily total and composes meals from whatever ingredients are actually available.

## The core math

remaining_kcal = daily_kcal_target - running_kcal
remaining_protein = daily_protein_target - running_protein
remaining_meals = number of meal slots left in the day

next_meal_kcal_target = remaining_kcal x (this meal's normal share of remaining)
next_meal_protein_target = remaining_protein x (this meal's normal share of remaining)

## What this means in practice

- On target: bot suggests the next meal at standard quantities.
- Behind on calories: bot scales the next meal up and absorbs the deficit across remaining slots.
- Ahead on calories: bot scales down. Hold protein, trim fat/carbs.
- Behind on protein: bot prioritizes high-protein options for the next meal.

## The meal-time prompt

At every scheduled meal time the bot asks: "Did you have [meal slot]?"

If YES: bot asks for the log. Three input modes accepted: text, voice, picture. Estimates macros, adds to running total, schedules the next prompt.

If NO: bot asks "What ingredients do you have?" User lists what is available. Bot composes a meal from those ingredients sized to hit the recalibrated target for the slot.

## End-of-day summary

Posted at [time]:
  Calories: [X] / [target] ([+/-])
  Protein: [X]g / [target]g ([+/-])
  Soda: [N] / [cap]
  Eat-out: [N]
  Pre-bed shake: taken / skipped
  Weight: [X] kg (yesterday [Y], [+/-])
  Weekly avg: [X] kg (last week [Y], [+/-] kg/week, target [Z])
  Status: [on track / slightly behind / ahead with specific adjustment]

## Weekly trajectory check

- Weekly gain on/above target: continue current macros.
- Weekly gain 60-80% of target: hold one more week, watch.
- Flat for 2 weeks: bump baseline by [X] kcal AND push pre-bed shake.

---

# Part 4: Meal log schema

kind: meal_log
payload fields: meal_slot, time_logged, input_mode, raw_input, items (food/quantity/kcal/protein_g), total_kcal, total_protein_g, total_carbs_g, total_fat_g, matches_planned, notes

Skipped meals: kind = meal_skip, payload includes slot, reason, recovery meal proposed.

---

# Part 5: Meal options

Operator-specific meal compositions with macro breakdowns, sized to each slot target. Bot uses these as templates when composing freely or when the user has the right ingredients.

---

# Part 6: Emergency meals

Pantry-only meals that hit protein and calorie targets with no fresh ingredients required.

---

# Part 7: Meal prep schedule

Weekly prep covers Mon-Wed. Midweek refresh covers Thu-Sat.

Weekly shopping list includes protein, carbs, produce, dairy, staples.
Weekly grocery budget: $[X]-[Y].

---

# Part 8: Skip protocol

- No response to meal prompt for 60+ min: log as skip, send check-in.
- 2 meals skipped same day: hard nudge with remaining calorie math.
- 3 days in a row with 2+ skips: pattern flagged, surfaces in Sunday review.
- Prep did not happen on schedule: bot proposes alternate prep slot.

---

# Part 9: Cheat meal allowance

[N] cheat meal(s) per week. [Day] only.
Tracked in logs as kind = cheat_meal.
