"""
GeoPulse Hyper-Local Retail Mobility Analytics
Module: Interactive Geospatial Retail Catchment & SVI Visualizer
Author: Amit Prajapati (Member 3 - Spatial Mobility & Retail Catchment Analyst)
Role: Member 3 - Infotact Batch 22.1
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SVI_CSV = os.path.join(REPORTS_DIR, "store_viability_rankings.csv")
CANNIBALIZATION_CSV = os.path.join(REPORTS_DIR, "store_cannibalization_risk.csv")
OUTPUT_HTML = os.path.join(REPORTS_DIR, "geopulse_interactive_catchment_map.html")

def build_interactive_map():
    print("=" * 70)
    print("GeoPulse: Generating Interactive Geospatial Catchment & SVI Map")
    print("=" * 70)

    if not os.path.exists(SVI_CSV):
        raise FileNotFoundError(f"Missing {SVI_CSV}. Run store_viability_index.py first.")

    df_svi = pd.read_csv(SVI_CSV)
    df_cannibal = pd.read_csv(CANNIBALIZATION_CSV) if os.path.exists(CANNIBALIZATION_CSV) else pd.DataFrame()

    # Convert nodes to list of dicts
    nodes_data = df_svi.to_dict(orient='records')

    # Filter critical cannibalization pairs
    critical_pairs = []
    if not df_cannibal.empty:
        critical_df = df_cannibal[df_cannibal['cannibalization_risk_index'] >= 50.0]
        critical_pairs = critical_df.to_dict(orient='records')

    # Color mapping for tiers
    tier_colors = {
        "Tier 1 - Flagship Catchment": "#eab308",       # Gold
        "Tier 2 - High-Yield Commercial Hub": "#10b981", # Emerald
        "Tier 3 - Moderate Local Catchment": "#0284c7",  # Sky Blue
        "Tier 4 - Peripheral / Low-Footfall": "#64748b"  # Slate
    }

    # Prepare JSON payloads for Leaflet template
    nodes_json = json.dumps(nodes_data)
    pairs_json = json.dumps(critical_pairs)
    tier_colors_json = json.dumps(tier_colors)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoPulse | Melbourne Retail Catchment & SVI Map</title>
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ display: flex; height: 100vh; background: #0f172a; color: #f8fafc; overflow: hidden; }}
        
        #sidebar {{
            width: 380px;
            background: #1e293b;
            border-right: 1px solid #334155;
            display: flex;
            flex-direction: column;
            z-index: 1000;
            box-shadow: 4px 0 24px rgba(0,0,0,0.4);
        }}
        
        .sidebar-header {{
            padding: 20px;
            border-bottom: 1px solid #334155;
            background: linear-gradient(135deg, #1e293b, #0f172a);
        }}
        .brand-title {{ font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
        .brand-subtitle {{ font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }}
        .role-tag {{ display: inline-block; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; background: #0369a1; color: #e0f2fe; border-radius: 12px; margin-top: 6px; }}
        
        .kpi-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 15px 20px; border-bottom: 1px solid #334155; background: #0f172a; }}
        .kpi-card {{ background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; text-align: center; }}
        .kpi-val {{ font-size: 1.3rem; font-weight: 700; color: #38bdf8; }}
        .kpi-label {{ font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }}

        .controls-pane {{ padding: 15px 20px; flex: 1; overflow-y: auto; }}
        .control-group {{ margin-bottom: 18px; }}
        .control-title {{ font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 8px; display: flex; justify-content: space-between; }}
        
        select, input[type="text"] {{
            width: 100%; padding: 8px 12px; background: #0f172a; border: 1px solid #334155; color: #f8fafc; border-radius: 6px; font-size: 0.85rem;
        }}
        select:focus, input:focus {{ outline: none; border-color: #38bdf8; }}

        .checkbox-label {{ display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #cbd5e1; cursor: pointer; margin-bottom: 6px; }}
        .checkbox-label input {{ accent-color: #38bdf8; cursor: pointer; }}

        .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 0.8rem; margin-bottom: 6px; color: #94a3b8; }}
        .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}

        #map {{ flex: 1; height: 100%; position: relative; }}

        .leaflet-popup-content-wrapper {{
            background: #1e293b !important;
            color: #f8fafc !important;
            border-radius: 8px !important;
            border: 1px solid #475569 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        }}
        .leaflet-popup-tip {{ background: #1e293b !important; }}
        .popup-header {{ border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }}
        .popup-title {{ font-size: 0.95rem; font-weight: 700; color: #38bdf8; }}
        .popup-precinct {{ font-size: 0.75rem; color: #94a3b8; }}
        .popup-metric {{ display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }}
        .popup-metric-val {{ font-weight: 600; color: #f1f5f9; }}
        .tier-badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-top: 6px; }}
    </style>
</head>
<body>
    <div id="sidebar">
        <div class="sidebar-header">
            <div class="brand-title">📍 GeoPulse Analytics</div>
            <div class="brand-subtitle">Melbourne Retail Mobility & Catchment Intelligence</div>
            <div class="role-tag">Member 3: Spatial Mobility & Retail Catchment Analyst</div>
        </div>

        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-val" id="stat-sensors">{len(df_svi)}</div>
                <div class="kpi-label">Active Sensors</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val" id="stat-avg-svi">{df_svi['store_viability_index'].mean():.1f}</div>
                <div class="kpi-label">Avg SVI Score</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{len(critical_pairs)}</div>
                <div class="kpi-label">Cannibal Pairs</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{df_svi['avg_hourly_footfall'].max():.0f}</div>
                <div class="kpi-label">Peak Mean / Hr</div>
            </div>
        </div>

        <div class="controls-pane">
            <div class="control-group">
                <div class="control-title">Filter by Precinct</div>
                <select id="precinct-filter" onchange="filterMap()">
                    <option value="ALL">All Retail Precincts (Citywide)</option>
                </select>
            </div>

            <div class="control-group">
                <div class="control-title">Filter by Viability Tier</div>
                <select id="tier-filter" onchange="filterMap()">
                    <option value="ALL">All Viability Tiers</option>
                    <option value="Tier 1 - Flagship Catchment">Tier 1 - Flagship Catchment</option>
                    <option value="Tier 2 - High-Yield Commercial Hub">Tier 2 - High-Yield Commercial Hub</option>
                    <option value="Tier 3 - Moderate Local Catchment">Tier 3 - Moderate Local Catchment</option>
                    <option value="Tier 4 - Peripheral / Low-Footfall">Tier 4 - Peripheral / Low-Footfall</option>
                </select>
            </div>

            <div class="control-group">
                <div class="control-title">Spatial Overlays</div>
                <label class="checkbox-label">
                    <input type="checkbox" id="toggle-isochrones" checked onchange="toggleIsochrones()">
                    Show 300m Primary Isochrone Buffers
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="toggle-cannibal" checked onchange="toggleCannibalization()">
                    Highlight Critical Cannibalization Arcs (CRI &ge; 50)
                </label>
            </div>

            <div class="control-group">
                <div class="control-title">Viability Tier Legend</div>
                <div class="legend-item"><span class="legend-dot" style="background:#eab308;"></span> Tier 1 - Flagship Catchment (SVI &ge; 80)</div>
                <div class="legend-item"><span class="legend-dot" style="background:#10b981;"></span> Tier 2 - High-Yield Hub (SVI 65-79.9)</div>
                <div class="legend-item"><span class="legend-dot" style="background:#0284c7;"></span> Tier 3 - Moderate Local (SVI 50-64.9)</div>
                <div class="legend-item"><span class="legend-dot" style="background:#64748b;"></span> Tier 4 - Peripheral / Low-Flow (SVI &lt; 50)</div>
            </div>
        </div>
    </div>

    <div id="map"></div>

    <script>
        const nodes = {nodes_json};
        const cannibalPairs = {pairs_json};
        const tierColors = {tier_colors_json};

        // Initialize Map centered on Melbourne CBD
        const map = L.map('map', {{
            center: [-37.8136, 144.9631],
            zoom: 15,
            zoomControl: true
        }});

        // Dark Matter / CartoDB tiles
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        const markersLayer = L.layerGroup().addTo(map);
        const isochronesLayer = L.layerGroup().addTo(map);
        const cannibalLayer = L.layerGroup().addTo(map);

        // Populate Precinct Filter
        const precincts = [...new Set(nodes.map(n => n.precinct_name))].sort();
        const pSelect = document.getElementById('precinct-filter');
        precincts.forEach(p => {{
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            pSelect.appendChild(opt);
        }});

        function renderNodes(filtered) {{
            markersLayer.clearLayers();
            isochronesLayer.clearLayers();

            filtered.forEach(node => {{
                const color = tierColors[node.viability_tier] || '#64748b';
                
                // Sensor Marker
                const marker = L.circleMarker([node.latitude, node.longitude], {{
                    radius: 7,
                    fillColor: color,
                    color: '#ffffff',
                    weight: 1.5,
                    opacity: 1,
                    fillOpacity: 0.9
                }});

                const popupHtml = `
                    <div class="popup-header">
                        <div class="popup-title">${{node.sensor_name}}</div>
                        <div class="popup-precinct">${{node.precinct_name}} (ID: ${{node.sensor_id}})</div>
                    </div>
                    <div class="popup-metric"><span>Store Viability Index:</span><span class="popup-metric-val" style="color:${{color}}">${{node.store_viability_index}} / 100</span></div>
                    <div class="popup-metric"><span>Avg Hourly Footfall:</span><span class="popup-metric-val">${{node.avg_hourly_footfall}} / hr</span></div>
                    <div class="popup-metric"><span>Weekend Surge Ratio:</span><span class="popup-metric-val">${{node.weekend_surge_ratio}}x</span></div>
                    <div class="popup-metric"><span>Mobility Pattern:</span><span class="popup-metric-val">${{node.behavior_profile}}</span></div>
                    <div class="tier-badge" style="background:${{color}}22; color:${{color}}; border:1px solid ${{color}};">${{node.viability_tier}}</div>
                `;

                marker.bindPopup(popupHtml);
                markersLayer.addLayer(marker);

                // 300m Isochrone Buffer
                const buffer = L.circle([node.latitude, node.longitude], {{
                    radius: 300,
                    color: color,
                    weight: 1,
                    dashArray: '4, 4',
                    fillColor: color,
                    fillOpacity: 0.08
                }});
                isochronesLayer.addLayer(buffer);
            }});

            document.getElementById('stat-sensors').innerText = filtered.length;
            if(filtered.length > 0) {{
                const avgSvi = filtered.reduce((acc, cur) => acc + cur.store_viability_index, 0) / filtered.length;
                document.getElementById('stat-avg-svi').innerText = avgSvi.toFixed(1);
            }} else {{
                document.getElementById('stat-avg-svi').innerText = "0";
            }}
        }}

        function renderCannibalization() {{
            cannibalLayer.clearLayers();
            const nodeMap = {{}};
            nodes.forEach(n => {{ nodeMap[n.sensor_id] = n; }});

            cannibalPairs.forEach(pair => {{
                const a = nodeMap[pair.sensor_a_id];
                const b = nodeMap[pair.sensor_b_id];
                if (a && b) {{
                    const line = L.polyline([[a.latitude, a.longitude], [b.latitude, b.longitude]], {{
                        color: '#ef4444',
                        weight: 2.5,
                        dashArray: '6, 6',
                        opacity: 0.85
                    }});
                    line.bindPopup(`
                        <div class="popup-header">
                            <div class="popup-title" style="color:#ef4444">⚠️ Cannibalization Overlap</div>
                            <div class="popup-precinct">${{pair.sensor_a_name}} &harr; ${{pair.sensor_b_name}}</div>
                        </div>
                        <div class="popup-metric"><span>Separation Distance:</span><span class="popup-metric-val">${{pair.distance_meters}} m</span></div>
                        <div class="popup-metric"><span>Cannibalization Risk (CRI):</span><span class="popup-metric-val" style="color:#ef4444">${{pair.cannibalization_risk_index}}</span></div>
                        <div style="font-size:0.75rem; color:#cbd5e1; margin-top:6px; font-style:italic;">${{pair.recommendation}}</div>
                    `);
                    cannibalLayer.addLayer(line);
                }}
            }});
        }}

        function filterMap() {{
            const pVal = document.getElementById('precinct-filter').value;
            const tVal = document.getElementById('tier-filter').value;

            let filtered = nodes;
            if (pVal !== 'ALL') {{
                filtered = filtered.filter(n => n.precinct_name === pVal);
            }}
            if (tVal !== 'ALL') {{
                filtered = filtered.filter(n => n.viability_tier === tVal);
            }}
            renderNodes(filtered);
        }}

        function toggleIsochrones() {{
            const checked = document.getElementById('toggle-isochrones').checked;
            if (checked) {{ map.addLayer(isochronesLayer); }} else {{ map.removeLayer(isochronesLayer); }}
        }}

        function toggleCannibalization() {{
            const checked = document.getElementById('toggle-cannibal').checked;
            if (checked) {{ map.addLayer(cannibalLayer); }} else {{ map.removeLayer(cannibalLayer); }}
        }}

        // Initial Render
        renderNodes(nodes);
        renderCannibalization();
    </script>
</body>
</html>
"""

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Interactive Geospatial Map saved to: {OUTPUT_HTML} (Size: {len(html_content):,} bytes)")
    return OUTPUT_HTML

if __name__ == '__main__':
    build_interactive_map()
