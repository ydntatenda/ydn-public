# workout.md (example)

## Status
v2. Aggressive hard-bulk program, rebalanced for [aesthetic priority] priority. Revisit [date], [date], [date].

## Operator baseline
- Height: [height]
- Starting weight: [weight]
- BMI at start: [BMI]
- Lifting history: [none / recreational / competitive]
- Injuries: [none / list]
- Goal: [hard bulk / cut / recomp]
- Aesthetic priority: [e.g. chest and arms]

## Goal for the program
Gain [X] kg of body weight over [Y] weeks, weighted toward muscle, accepting some fat gain. Get from [start] kg to [target] kg. By [date]: [specific physical milestone].

This program works if and only if the food shows up. The nutrition_targets.md library is the other half. Without [kcal]/day and [protein]g protein, the volume here will break you, not build you.

## Operating principles
- High frequency, high volume. Each muscle group hit 2x per week. [Priority muscles] hit 4-5x per week.
- Compounds drive 60-70% of size. Isolation drives the remaining definition.
- Linear progression on compounds for as long as it holds.
- Two phases. Weeks 1 to [N] build pattern competence. Weeks [N+1] to [end] push volume hard.
- Sleep is part of the program. Food is part of the program.
- Form first, ego second.

## Weekly volume targets (Phase 2)
- [Muscle group]: [X]-[Y] sets/week
- [Muscle group]: [X]-[Y] sets/week
- [Muscle group]: [X]-[Y] sets/week

## Weekly split
| Day | Session | Duration |
|---|---|---|
| Mon | Push (chest, shoulders, triceps) | 1.5 h |
| Tue | Pull (back, biceps, rear delts) | 1.5 h |
| Wed | Legs (quads, hamstrings, glutes, calves, abs) | 1.5 h |
| Thu | Push | 1.5 h |
| Fri | Pull | 1.5 h |
| Sat | Legs + arm finisher + sauna + pool | 2.5 h |
| Sun | Off lift. Mobility + sauna + pool. | 1.5 h |

---

## Phase 1: Foundation (weeks 1 to [N])

### Phase 1, Push day
[Compound lifts, sets x reps. Isolation. Total set count per muscle group.]

### Phase 1, Pull day
[Compound lifts, sets x reps. Isolation. Total set count per muscle group.]

### Phase 1, Leg day
[Compound lifts, sets x reps. Isolation. Total set count per muscle group.]

### Phase 1, starting weights
[Specific starting weights for each lift, sized to the operator's baseline.]

### Phase 1 progression rule
Each session, add weight if all working sets completed cleanly:
- Squat, Bench, Row, RDL: +[X] kg
- OHP, Incline DB press: +[X] kg
- Isolation lifts: +1 rep per set until top of rep range, then add weight

Missed working set = repeat the weight next session.

### Phase 1 targets (end of week [N])
- Bench: [X] kg x 8
- OHP: [X] kg x 8
- Squat: [X] kg x 8
- Deadlift: [X] kg x 5
- Bodyweight: [X] kg

Hit targets, move to Phase 2. Behind, hold Phase 1 an extra week and look at food.

---

## Phase 2: Hypertrophy push (weeks [N+1] to [end])

[Same structure as Phase 1 but with higher volume and heavier weights.]

### Phase 2 targets (end of program)
- Bench: [X]-[Y] kg x 6
- OHP: [X]-[Y] kg x 6
- Squat: [X]-[Y] kg x 6
- Deadlift: [X]-[Y] kg x 5
- Bodyweight: [X]-[Y] kg

---

## Hard rules
- 10-min warm-up every session. No exceptions.
- Form first, weight second.
- Under [X] hrs sleep: working sets drop one, isolation drops entirely.
- Under [X] kcal eaten that day: working sets drop one, isolation drops entirely.
- No alcohol on training days.
- Eat within 90 min post-lift.

## Skip protocol
When a session is skipped:
1. Log skip and reason in logs (kind = 'workout_skip').
2. Illness or injury: accept, no make-up.
3. "Busy / tired / forgot": propose restructure.
4. Two missed sessions in one week: no more restructure. Surface in Sunday review.
5. Three+ skips: pattern flagged. Bot stops proposing restructure and asks what is wrong with the template, not the lifter.
6. Three clean weeks in a row: progression audit — are weights actually going up?

## Tracking
Every session, log to the bot:
- Session type (Push / Pull / Leg / Sat-Leg)
- Top set weight x reps actually completed for each main lift
- RPE 1-10
- Any PRs (pr: true in log payload)
- Any injury signal

Bodyweight: daily, same time (morning, post-bathroom, pre-food). If weekly average doesn't move for 7 days, food is the problem.

## Substitutions
- Squat rack busy: goblet squat with heaviest dumbbell, +50% reps
- Bench occupied: dumbbell bench press, same rep target
- Pull-up bar occupied: lat pulldown to failure
- Deadlift platform unavailable: trap bar deadlift or rack pulls from mid-shin

Never skip a main lift. Substitute and log it.
