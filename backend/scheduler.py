from datetime import timedelta, datetime


def group_counters_by_zone(counters):
    zones = {}
    for name in counters:
        if "AC" in name or "DC" in name:
            zone = "Zone" + str((int(name[2:])-1)//10 + 1)
        else:
            zone = "BIKES"
        zones.setdefault(zone, []).append(name)
    return zones


def assign_counters(officers, counters, current_time):
    schedule = {}
    zones = group_counters_by_zone(counters)

    for zone, counters_in_zone in zones.items():
        # Ensure 50% min manning
        min_manning = max(1, len(counters_in_zone)//2)
        # Start from back counters
        counters_in_zone = sorted(counters_in_zone, reverse=True)

        # Filter available officers
        available_officers = [
            o for o in officers
            if o.available and o.actual_arrival <= current_time < o.actual_leave
            and (not o.zones or zone in o.zones)
        ]
        # Prioritize: Regular -> OT -> SOS
        available_officers.sort(
            key=lambda x: {"regular": 0, "OT": 1, "SOS": 2}[x.type])

        assigned_count = 0
        for counter in counters_in_zone:
            if assigned_count >= min_manning:
                break
            if counter in schedule:
                continue
            if available_officers:
                officer = available_officers.pop(0)
                schedule[counter] = {
                    "officer": officer.name,
                    "type": officer.type,
                    "zone": zone,
                    "start_time": current_time,
                    "end_time": min(officer.actual_leave, current_time + timedelta(hours=3))
                }
                assigned_count += 1
            else:
                schedule[counter] = {"officer": None, "zone": zone}
    return schedule


def generate_time_slots(start, end, interval=15):
    slots = []
    current = start
    while current <= end:
        slots.append(current)
        current += timedelta(minutes=interval)
    return slots


def shift_summary(officers, counters, shift_start, shift_end, interval=15):
    slots = generate_time_slots(shift_start, shift_end, interval)
    summary = []

    for t in slots:
        schedule = assign_counters(officers, counters, t)

        # Count running car and motorcycle counters
        car_count = sum(1 for c, o in schedule.items() if o.get(
            "officer") and ("AC" in c or "DC" in c))
        bike_count = sum(1 for c, o in schedule.items() if o.get(
            "officer") and ("AM" in c or "DM" in c))

        # Breakdown by zone
        zones = group_counters_by_zone(counters)
        zone_counts = [sum(1 for c in zones[z] if schedule.get(c, {}).get(
            "officer")) for z in ["Zone1", "Zone2", "Zone3", "Zone4"]]

        summary.append({
            "time": t.strftime("%H%M"),
            "total_car": car_count,
            "total_bike": bike_count,
            "zone_counts": zone_counts
        })
    return summary
