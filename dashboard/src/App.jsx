
import { useEffect, useState } from "react";
import Papa from "papaparse";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

import {
  Activity,
  MapPin,
  Users,
  Footprints,
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
  const [activeMenu, setActiveMenu] = useState("overview");

  // Sidebar Navigation
  const navigateTo = (sectionId, menuName) => {
    document.getElementById(sectionId)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    setActiveMenu(menuName);
  };

  // Load CSV Data
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

            if (!response.ok) {
              throw new Error(`Could not load ${file}`);
            }

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

  // Get Summary Metrics
  const getMetric = (keyword) => {
    const item = data.summary.find((row) =>
      Object.values(row).some((value) =>
        String(value)
          .toLowerCase()
          .includes(keyword.toLowerCase())
      )
    );

    if (!item) return 0;

    const number = Object.values(item).find(
      (value) => typeof value === "number"
    );

    return number ?? 0;
  };

  // KPI Calculations
  const footfall = data.daily.reduce(
    (sum, row) =>
      sum + (Number(row.Total_Count) || 0),
    0
  );

  const gpsRecords = getMetric("total gps records");
  const devices = getMetric("unique devices");
  const sensorCount = data.sensors.length;

  const topSensors = [...data.sensors]
    .sort(
      (a, b) =>
        Number(b.Total_Pedestrian_Count) -
        Number(a.Total_Pedestrian_Count)
    )
    .slice(0, 10);

  const formatNumber = (number) =>
    Number(number || 0).toLocaleString("en-IN");

const busiestSensor = topSensors[0];

const averageFootfall =
  data.daily.length > 0
    ? Math.round(footfall / data.daily.length)
    : 0;

  if (loading) {
    return (
      <div className="loading">
        Loading GeoPulse Dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="dashboard">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <MapPin size={28} />
          <span>GeoPulse</span>
        </div>

        <p className="menu-label">ANALYTICS</p>

        <button
          className={`menu-item ${
            activeMenu === "overview" ? "active" : ""
          }`}
          onClick={() =>
            navigateTo("overview", "overview")
          }
        >
          <Activity size={19} />
          Overview
        </button>

        <button
          className={`menu-item ${
            activeMenu === "footfall" ? "active" : ""
          }`}
          onClick={() =>
            navigateTo("footfall", "footfall")
          }
        >
          <Footprints size={19} />
          Footfall Analysis
        </button>

        <button
          className={`menu-item ${
            activeMenu === "mobility" ? "active" : ""
          }`}
          onClick={() =>
            navigateTo("mobility", "mobility")
          }
        >
          <MapPin size={19} />
          Mobility Insights
        </button>

        <button
          className={`menu-item ${
            activeMenu === "sensors" ? "active" : ""
          }`}
          onClick={() =>
            navigateTo("sensors", "sensors")
          }
        >
          <Users size={19} />
          Sensor Activity
        </button>

        <div className="sidebar-footer">
          Hyper-Local Retail
          <br />
          Mobility Analytics
        </div>

      </aside>

      {/* Main Dashboard */}
      <main className="main-content">

        {/* Header */}
        <header className="topbar" id="overview">

          <div>
            <h1>Analytics Overview</h1>
            <p>
              Melbourne Mobility & Pedestrian Insights
            </p>
          </div>

          <div className="live-status">
            <span className="status-dot"></span>
            Data Dashboard
          </div>

        </header>

        {/* Welcome Banner */}
        <section className="welcome">

          <div>
            <h2>Welcome to GeoPulse</h2>

            <p>
              Understand pedestrian activity and GPS
              mobility patterns through real project data.
            </p>
          </div>

          <Activity size={48} />

        </section>

        {/* KPI Cards */}
        <section className="kpi-grid">

          <div className="kpi-card">
            <div className="kpi-icon purple">
              <Footprints />
            </div>

            <p>Total Pedestrian Footfall</p>
            <h2>{formatNumber(footfall)}</h2>
            <span>Week 1 data</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon blue">
              <Activity />
            </div>

            <p>Total GPS Records</p>
            <h2>{formatNumber(gpsRecords)}</h2>
            <span>GPS mobility data</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon green">
              <Users />
            </div>

            <p>Unique Devices</p>
            <h2>{formatNumber(devices)}</h2>
            <span>Tracked devices</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon orange">
              <MapPin />
            </div>

            <p>Total Sensors</p>
            <h2>{formatNumber(sensorCount)}</h2>
            <span>Sensor locations</span>
          </div>

        </section>

        {/* Project Insights */}
<section className="insights-section">
  <h2>Project Insights</h2>

  <div className="insights-grid">

    <div className="insight-card">
      <h3>Average Daily Footfall</h3>
      <p>{formatNumber(averageFootfall)}</p>
      <span>Average pedestrian count per day</span>
    </div>

    <div className="insight-card">
      <h3>Busiest Sensor</h3>
      <p>
        {busiestSensor
          ? `Sensor ${busiestSensor.Sensor_ID}`
          : "No Data"}
      </p>
      <span>Highest pedestrian activity</span>
    </div>

    <div className="insight-card">
      <h3>Active GPS Devices</h3>
      <p>{formatNumber(devices)}</p>
      <span>Unique tracked devices</span>
    </div>

  </div>
</section>

        {/* Charts */}
        <section className="chart-grid">

          {/* Daily Footfall */}
          <div className="chart-card" id="footfall">

            <h3>Daily Pedestrian Footfall</h3>

            <p className="chart-subtitle">
              Total pedestrian count by day
            </p>

            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.daily}>

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

                <XAxis dataKey="Day" />
                <YAxis />
                <Tooltip />

                <Bar
                  dataKey="Total_Count"
                  fill="#7564e8"
                  radius={[6, 6, 0, 0]}
                />

              </BarChart>
            </ResponsiveContainer>

          </div>

          {/* Hourly Activity */}
          <div className="chart-card">

            <h3>Hourly Pedestrian Activity</h3>

            <p className="chart-subtitle">
              Footfall trends across 24 hours
            </p>

            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.hourly}>

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

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

          {/* GPS Mobility */}
          <div className="chart-card" id="mobility">

            <h3>Hourly GPS Mobility</h3>

            <p className="chart-subtitle">
              GPS pings and active devices
            </p>

            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.mobility}>

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

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

          {/* Top Sensors */}
          <div className="chart-card" id="sensors">

            <h3>Top 10 Busiest Sensors</h3>

            <p className="chart-subtitle">
              Sensors ranked by pedestrian count
            </p>

            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={topSensors}
                layout="vertical"
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                />

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

        {/* Footer */}
        <footer className="footer">
          GeoPulse Analytics Dashboard |
          Built with React & CSV Data
        </footer>

      </main>

    </div>
  );
}

export default App;
