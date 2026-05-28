# sleep.md (example)

## Status
v1. Third leg of the bulk stool with workout.md and nutrition_targets.md.

---

## Operator baseline
- Current sleep pattern: [describe current pattern]
- Target: [X] hrs in bed ([time]-[time]), seven days
- Bedroom: [location] — [conditions]
- Current bad habits: [e.g. sleeps with light on, phone in bed, doomscrolling]
- Caffeine: [rules, e.g. no caffeine after 14:00]
- Bot intervention style: [soft nudge / hard interrupt]

---

## Why sleep matters

The lifts in workout.md are written for someone sleeping [X] hrs. The calories in nutrition_targets.md are sized for someone sleeping [X] hrs. Drop sleep below [threshold] and three things happen:

1. Muscle synthesis drops. Growth hormone releases during deep sleep. Less deep sleep = less GH = less muscle from the same volume.
2. Calorie partitioning worsens. Under-slept bodies store more surplus as fat instead of muscle.
3. Recovery debt accumulates. Under-slept lifters miss reps, cannot progress weights, get injured.

Sleep is not optional for this program. It is the program.

---

## Hard rules

- Bed at [time], lights out by [time].
- Lights off when sleeping. [Specific environment fix.]
- Phone leaves the bed. Phone goes on the dresser, desk, or charger across the room.
- No screens in the 30 min before sleep.
- [Wake time] wake, every day. No catching up on weekends.
- No caffeine after [time].

## Soft rules

- One bad night (less than [X] hrs): hold the template, lift goes to [X]% volume that day.
- Two bad nights in a row: force earlier wind-down start, skip lift, prioritize sleep.
- Three bad nights: something is wrong. Bot surfaces a context_item for review.
- If wide awake past [time] unable to sleep: get out of bed, read for 20 min in dim light, return to bed.
- Naps allowed if needed, max 30 min, before [time] only.

---

## Wind-down protocol ([time]-[time])

### [time] — Component 1 (e.g. warm shower)
Why this works physiologically. What to do if schedule slips.

### [time] — Tomorrow's plan from bot
Bot delivers a structured plan message including:
- Tomorrow's date and day
- Wake time and first block
- Lift session type
- Meal slots and any prep needs
- Calendar events ingested during the day and any conflicts
- Goal status, one line

User reads, pushes back or confirms, plan locks. Phone goes away.

### [time] — Personal ritual (e.g. reading, prayer, meditation)
No phone, no screen.

### [final time] — Lights off, in bed.

---

## Sleep environment fix list

| Item | Action | Cost |
|---|---|---|
| Lights | Stop sleeping with overhead light on. Warm bulb only, off when in bed. | $0 |
| Blackout | Blackout curtains or sleep mask if light bleeds in. | $10-30 |
| Temperature | Set room to [X]C at bedtime. | $0 |
| Phone charging | Move charger across the room. Phone never on the bed. | $0 |

---

## Tracking

Logged daily to the logs table:

kind: sleep_log
payload fields: date, bedtime, wake_time, total_in_bed_hours, estimated_sleep_hours,
lights_off_compliance, phone_in_bed, wind_down_completed, quality_self_report (1-10), notes

Bot prompts at [wake time + 15 min]: "How did you sleep? Bedtime / wake / quality 1-10."

---

## Bot intervention protocol (soft nudge)

| Time | Message |
|---|---|
| [time] | "60 min to bed. Wind-down starts at [time]." |
| [time] | "Wind-down. [Component 1] in [N] min. Plan at [time]." |
| [time] | Daily plan delivered. |
| [time] | "Lights off, phone across the room. Plan locked. Sleep." |
| [time+30] | "It's [time]. Everything okay?" One soft check, logs the slip. |
| [time+60] | "Tomorrow's plan assumes [X] hrs sleep. You're now under [Y]." |
| [wake time] | "How did you sleep? Bedtime / wake / quality 1-10." |

---

## Skip protocol

When bedtime missed by more than 30 min:
1. Log the slip (kind = sleep_skip, payload includes intended_bedtime, actual_bedtime, reason).
2. Recalculate projected sleep. If under [threshold] hrs, flag tomorrow's lift as reduced volume.
3. Soft nudge: "Tomorrow's lift will run lighter. Eat the same, lift less."

Two skips in a row:
1. Force earlier wind-down start tomorrow.
2. Skip tomorrow's lift, do mobility instead.
3. Surface in Sunday review.

Three skips in a row:
1. Pattern flagged as context_item.
2. Sunday review asks: what is blocking sleep?
