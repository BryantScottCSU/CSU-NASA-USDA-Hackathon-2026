from __future__ import annotations

from collections import defaultdict
from math import log1p

from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render

from .models import AirTrafficAggregate, DetectionAggregate, PortTraffic
from .utils import month_shift, normalize_metric, pearson, season_filter


def dashboard(request):
    return render(request, "outbreaks/dashboard.html")


def api_options(request):
    states = list(DetectionAggregate.objects.order_by("state_name").values_list("state_name", flat=True).distinct())
    countries = list(AirTrafficAggregate.objects.order_by("origin_country").values_list("origin_country", flat=True).distinct()[:500])
    years = sorted(set(DetectionAggregate.objects.values_list("year", flat=True).distinct()) | set(AirTrafficAggregate.objects.values_list("year", flat=True).distinct()))
    return JsonResponse({"states": states, "countries": countries, "years": years})


def api_summary(request):
    det = DetectionAggregate.objects.aggregate(rows=Count("id"), total=Sum("count"))
    air = AirTrafficAggregate.objects.aggregate(rows=Count("id"), passengers=Sum("passengers"), freight=Sum("freight"), flights=Sum("flights"))
    ports = PortTraffic.objects.aggregate(rows=Count("id"), foreign=Sum("total_foreign_loaded"))
    return JsonResponse({"detections": det, "air_traffic": air, "ports": ports})


def _detection_series(state=None):
    qs = DetectionAggregate.objects.all()
    if state and state != "all":
        qs = qs.filter(state_name=state)
    rows = qs.values("year", "month").annotate(total=Sum("count")).order_by("year", "month")
    return {(__import__("datetime").date(r["year"], r["month"], 1)): float(r["total"] or 0) for r in rows}


def api_countries(request):
    metric = normalize_metric(request.GET.get("metric"))
    state = request.GET.get("state") or "all"
    try:
        lag = int(request.GET.get("lag", 0))
    except ValueError:
        lag = 0

    detections = _detection_series(state)
    qs = AirTrafficAggregate.objects.all()
    if state and state != "all":
        qs = qs.filter(state_name=state)
    rows = qs.values("origin_country", "year", "month").annotate(v=Sum(metric)).order_by("origin_country", "year", "month")

    traffic_by_country = defaultdict(dict)
    totals = defaultdict(float)
    for r in rows:
        d = __import__("datetime").date(r["year"], r["month"], 1)
        val = float(r["v"] or 0)
        traffic_by_country[r["origin_country"]][d] = val
        totals[r["origin_country"]] += val

    out = []
    for country, series in traffic_by_country.items():
        xs, ys = [], []
        for det_month, det_val in detections.items():
            traffic_month = month_shift(det_month, -lag)
            xs.append(series.get(traffic_month, 0.0))
            ys.append(det_val)
        corr = pearson(xs, ys)
        total_det = sum(ys)
        risk = (max(corr or 0, 0) + 0.05) * log1p(totals[country]) * log1p(total_det)
        out.append({
            "country": country,
            "correlation": corr,
            "traffic_total": totals[country],
            "detection_total": total_det,
            "risk_score": risk,
            "lag_months": lag,
        })
    out.sort(key=lambda r: (r["risk_score"], r["traffic_total"]), reverse=True)
    return JsonResponse({"metric": metric, "state": state, "countries": out[:75]})


def api_timeseries(request):
    metric = normalize_metric(request.GET.get("metric"))
    country = request.GET.get("country")
    state = request.GET.get("state") or "all"
    detections = _detection_series(state)
    qs = AirTrafficAggregate.objects.all()
    if country:
        qs = qs.filter(origin_country=country)
    if state and state != "all":
        qs = qs.filter(state_name=state)
    traffic_rows = qs.values("year", "month").annotate(v=Sum(metric)).order_by("year", "month")
    traffic = {__import__("datetime").date(r["year"], r["month"], 1): float(r["v"] or 0) for r in traffic_rows}
    months = sorted(set(detections) | set(traffic))
    return JsonResponse({
        "labels": [d.strftime("%Y-%m") for d in months],
        "detections": [detections.get(d, 0.0) for d in months],
        "traffic": [traffic.get(d, 0.0) for d in months],
        "metric": metric,
        "country": country,
        "state": state,
    })


def api_hotspots(request):
    metric = normalize_metric(request.GET.get("metric"))
    state = request.GET.get("state") or "all"
    country = request.GET.get("country")
    season = request.GET.get("season") or "all"
    year = request.GET.get("year")

    det_qs = DetectionAggregate.objects.exclude(lat__isnull=True).exclude(lon__isnull=True)
    air_qs = AirTrafficAggregate.objects.exclude(dest_lat__isnull=True).exclude(dest_lon__isnull=True)
    port_qs = PortTraffic.objects.all()
    if state != "all":
        det_qs = det_qs.filter(state_name=state)
        air_qs = air_qs.filter(state_name=state)
    if country:
        air_qs = air_qs.filter(origin_country=country)
    if year:
        det_qs = det_qs.filter(year=year)
        air_qs = air_qs.filter(year=year)
        port_qs = port_qs.filter(year=year)

    detections = []
    for r in det_qs.values("state_name", "county_name", "year", "month", "lat", "lon").annotate(total=Sum("count"))[:3000]:
        if season_filter(r["month"], season):
            detections.append({"type": "detection", "state": r["state_name"], "name": r["county_name"], "year": r["year"], "month": r["month"], "lat": r["lat"], "lon": r["lon"], "value": float(r["total"] or 0)})

    airports = []
    for r in air_qs.values("state_name", "dest_city_name", "dest_airport", "year", "month", "dest_lat", "dest_lon").annotate(value=Sum(metric))[:3000]:
        if season_filter(r["month"], season):
            airports.append({"type": "airport", "state": r["state_name"], "name": f"{r['dest_airport']} {r['dest_city_name']}", "year": r["year"], "month": r["month"], "lat": r["dest_lat"], "lon": r["dest_lon"], "value": float(r["value"] or 0)})

    ports = list(port_qs.values("year", "port_name", "state").annotate(value=Sum("total_foreign_loaded")).order_by("-value")[:200])
    return JsonResponse({"detections": detections, "airports": airports, "ports": ports, "metric": metric, "season": season})
