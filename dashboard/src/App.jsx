
import { useEffect, useState } from "react";
import Papa from "papaparse";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, LineChart, Line
} from "recharts";
import {
  Activity, MapPin, Users, Footprints, RefreshCw
} from "lucide-react";
import "./App.css";

function App() {
  const [data, setData] = useState({
    daily: [],
    hourly: [],
    mobility: [],
    sensors: [],
    summary: [],
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const files = [
          "day_wise_activity.csv",
          "hourly_activity.csv",
          "hourly_mobility.csv",
          "mobility_summary.csv",
          "sensor_activity.csv",
        ];

        const results = await Promise.all(
          files.map(async (file) => {
            const response = await fetch(`/data/${file}`);
            if (!response.ok) throw new Error(`Could not load ${file}`);
            const csv = await response.text();
            return Papa.parse(csv, {
              header: true,
              skipEmptyLines: true,
              dynamicTyping: true,
            }).data;
          })
        );

        setData({
          daily: results[0],
          hourly: results[1],
          mobility: results[2],
          summary: results[3],
          sensors: results[4],
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const getMetric = (keyword) => {
    const item = data.summary.find((row) =>
      Object.values(row).some((value) =>
        String(value).toLowerCase().includes(keyword.toLowerCase())
      )
    );

    if (!item) return 0;

    const values = Object.values(item);
    const number = values.find((value) => typeof value === "number");
    return number ?? 0;
  };

  const footfall = data.daily.reduce(
    (sum, row) => sum + (Number(row.Total_Count) || 0), 0
  );

  const gpsRecords = getMetric("total gps records");
  const devices = getMetric("unique devices");
  const sensorCount = data.sensors.length;

  const topSensors = [...data.sensors]
    .sort((a, b) =>
      Number(b.Total_Pedestrian_Count) - Number(a.Total_Pedestrian_Count)
    )
    .slice(0, 10);

  const formatNumber = (number) =>
    Number(number || 0).toLocaleString("en-IN");

  if (loading) {
    return <div className="loading">Loading GeoPulse Dashboard...</div>;
  }

  if (error) {
    return <div className="loading">Error: {error}</div>;
  }

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <MapPin size={28} />
          <span>GeoPulse</span>
        </div>

        <p className="menu-label">ANALYTICS</p>
        <div className="menu-item active">
          <Activity size={19} /> Overview
        </div>
        <div className="menu-item">
          <Footprints size={19} /> Footfall Analysis
        </div>
        <div className="menu-item">
          <MapPin size={19} /> Mobility Insights
        </div>
        <div className="menu-item">
          <Users size={19} /> Sensor Activity
        </div>

        <div className="sidebar-footer">
          Hyper-Local Retail<br />Mobility Analytics
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Analytics Overview</h1>
            <p>Melbourne Mobility & Pedestrian Insights</p>
          </div>
          <div className="live-status">
            <span className="status-dot"></span>
            Data Dashboard
          </div>
        </header>

        <section className="welcome">
          <div>
            <h2>Welcome to GeoPulse</h2>
            <p>
              Understand pedestrian activity and GPS mobility patterns
              through real project data.
            </p>
          </div>
          <Activity size={48} />
        </section>

        <section className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon purple"><Footprints /></div>
            <p>Total Pedestrian Footfall</p>
            <h2>{formatNumber(footfall)}</h2>
            <span>Week 1 data</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon blue"><Activity /></div>
            <p>Total GPS Records</p>
            <h2>{formatNumber(gpsRecords)}</h2>
            <span>GPS mobility data</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon green"><Users /></div>
            <p>Unique Devices</p>
            <h2>{formatNumber(devices)}</h2>
            <span>Tracked devices</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon orange"><MapPin /></div>
            <p>Total Sensors</p>
            <h2>{formatNumber(sensorCount)}</h2>
            <span>Sensor locations</span>
          </div>
        </section>

        <section className="chart-grid">
          <div className="chart-card">
            <h3>Daily Pedestrian Footfall</h3>
            <p className="chart-subtitle">Total pedestrian count by day</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.daily}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="Day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="Total_Count" fill="#7564e8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Hourly Pedestrian Activity</h3>
            <p className="chart-subtitle">Footfall trends across 24 hours</p>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.hourly}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="Hour" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="Total_Count"
                  stroke="#16a6a1"
                  strokeWidth={3}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Hourly GPS Mobility</h3>
            <p className="chart-subtitle">GPS pings and active devices</p>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.mobility}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="Hour" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="Total_GPS_Pings"
                  stroke="#7564e8"
                  strokeWidth={3}
                  name="GPS Pings"
                />
                <Line
                  type="monotone"
                  dataKey="Active_Devices"
                  stroke="#16a6a1"
                  strokeWidth={3}
                  name="Active Devices"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Top 10 Busiest Sensors</h3>
            <p className="chart-subtitle">Sensors ranked by pedestrian count</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={topSensors} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" />
                <YAxis
                  type="category"
                  dataKey="Sensor_ID"
                  width={55}
                />
                <Tooltip />
                <Bar
                  dataKey="Total_Pedestrian_Count"
                  fill="#f59e0b"
                  radius={[0, 6, 6, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <footer className="footer">
          GeoPulse Analytics Dashboard | Built with React & CSV Data
        </footer>
      </main>
    </div>
  );
}

export default App;
