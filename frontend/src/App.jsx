import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getDashboard,
  uploadDataset,
  askDataset,
} from "./api";


import {
  LayoutDashboard,
  Database,
  BrainCircuit,
  Lightbulb,
  Settings,
  Menu,
  Bell,
  Search,
  TrendingUp,
  TrendingDown,
  DollarSign,
  ShoppingCart,
  Users,
  Activity,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";

import Login from "./pages/Login";
import Datasets from "./pages/Datasets";


import "./App.css";

const navigation = [
  {
    name: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Datasets",
    icon: Database,
  },
  {
    name: "AI Analyst",
    icon: BrainCircuit,
  },
  {
    name: "Insights",
    icon: Lightbulb,
  },
];

const formatCurrency = (value) => {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `$${Number(value).toLocaleString("en-US", {
    maximumFractionDigits: 0,
  })}`;
};

const formatNumber = (value) => {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return Number(value).toLocaleString("en-US", {
    maximumFractionDigits: 0,
  });
};

const formatPercent = (value) => {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(2)}%`;
};

function AIChart({ chart }) {
  if (!chart || !chart.data?.length) {
    return null;
  }

  const values = chart.data.map(
    (item) => Number(item.value) || 0
  );

  const maxValue = Math.max(...values, 1);

  const width = 800;
  const height = 300;
  const padding = 40;

  const getX = (index) => {
    if (chart.data.length === 1) {
      return width / 2;
    }

    return (
      padding +
      (index /
        (chart.data.length - 1)) *
        (width - padding * 2)
    );
  };

  const getY = (value) => {
    return (
      height -
      padding -
      (value / maxValue) *
        (height - padding * 2)
    );
  };

  if (chart.type === "line") {
    const path = chart.data
      .map((item, index) => {
        const x = getX(index);
        const y = getY(
          Number(item.value) || 0
        );

        return `${
          index === 0 ? "M" : "L"
        }${x} ${y}`;
      })
      .join(" ");

    return (
      <div className="ai-chart">

        <div className="ai-chart-header">

          <div>
            <h3>
              {chart.title}
            </h3>

            <span>
              {chart.x_axis} vs. {chart.y_axis}
            </span>
          </div>

        </div>

        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="ai-chart-svg"
          preserveAspectRatio="none"
        >

          <path
            d={path}
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {chart.data.map(
            (item, index) => (
              <circle
                key={index}
                cx={getX(index)}
                cy={getY(
                  Number(item.value) || 0
                )}
                r="4"
                fill="currentColor"
              />
            )
          )}

        </svg>

        <div className="ai-chart-labels">

          {chart.data.map(
            (item, index) => (
              <span key={index}>
                {item.label}
              </span>
            )
          )}

        </div>

      </div>
    );
  }

  if (chart.type === "bar") {
    return (
      <div className="ai-chart">

        <div className="ai-chart-header">

          <div>
            <h3>
              {chart.title}
            </h3>

            <span>
              {chart.x_axis} vs. {chart.y_axis}
            </span>
          </div>

        </div>

        <div className="ai-bar-chart">

          {chart.data.map(
            (item, index) => {

              const value =
                Number(item.value) || 0;

              const percentage =
                (value / maxValue) * 100;

              return (
                <div
                  className="ai-bar-row"
                  key={index}
                >

                  <div className="ai-bar-label">
                    {item.label}
                  </div>

                  <div className="ai-bar-track">

                    <div
                      className="ai-bar-fill"
                      style={{
                        width:
                          `${percentage}%`,
                      }}
                    />

                  </div>

                  <strong>
                    {formatCurrency(value)}
                  </strong>

                </div>
              );
            }
          )}

        </div>

      </div>
    );
  }

  return null;
}

function App() {
  const [authenticated, setAuthenticated] = useState(
    !!localStorage.getItem("access_token")
  );

  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  // AI ANALYST STATE
  const [aiQuestion, setAiQuestion] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [selectedAiChart, setSelectedAiChart] = useState(null);
  const [aiDatasetId, setAiDatasetId] = useState(null);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState("Dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleLogout() {
    localStorage.removeItem("access_token");
    setAuthenticated(false);
  }

  async function handleDatasetUpload() {
    if (!selectedFile) {
      setUploadError("Please select a CSV or Excel file.");
      return;
    }

    setUploading(true);
    setUploadError("");
    setUploadMessage("");

    try {
      const data = await uploadDataset(selectedFile);
      setDatasets((prev) => [
        ...prev,
        {
          id: data.dataset_id,
          filename: data.filename,
          size: data.size_bytes,
          extension: data.extension,
        },
      ]);

      setSelectedDatasetId(data.dataset_id);
      console.log("Dataset uploaded:", data);
      setUploadMessage(
        `Dataset "${data.filename}" uploaded successfully.`
      );
      setSelectedFile(null);
    } catch (err) {
      console.error(err);
      setUploadError(err.message || "Dataset upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAskAI() {
    if (!aiQuestion.trim()) {
      setAiError("Please enter a question.");
      return;
    }

    if (!aiDatasetId) {
      setAiError("Please select a dataset first.");
      return;
    }

    setAiLoading(true);
    setAiError("");
    setAiResponse(null);
    setSelectedAiChart(null);

    try {
      const data = await askDataset(
        aiDatasetId,
        aiQuestion
      );

      console.log("AI Analyst result:", data);

      setAiResponse(data);

      if (data.chart) {
        setSelectedAiChart(data.chart);
      }

    } catch (err) {
      console.error("AI Analyst error:", err);

      setAiError(
        err.message || "Unable to analyze the dataset."
      );
    } finally {
      setAiLoading(false);
    }
  }

  useEffect(() => {
  let cancelled = false;

  async function loadDashboard() {
    if (!selectedDatasetId) {
      setLoading(false);
      setDashboard(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await getDashboard(selectedDatasetId);

      if (!cancelled) {
        console.log("Dashboard data:", data);
        setDashboard(data);
      }
    } catch (err) {
      console.error("Dashboard error:", err);

      if (!cancelled) {
        setError(
          err.message || "Unable to load dashboard data."
        );
      }
    } finally {
      if (!cancelled) {
        setLoading(false);
      }
    }
  }

  loadDashboard();

  return () => {
    cancelled = true;
  };
}, [selectedDatasetId]);

  const kpiData =
    dashboard?.kpis ?? {};



  // -----------------------------------------
  // LIVE REVENUE TREND DATA
  // -----------------------------------------

  const trendData = (dashboard?.charts?.trends ?? [])
    .map((item) => ({
      period: item?.period ?? "",
      value: Number(item?.total) || 0,
    }))
    .filter((item) => item.period);

  const chartWidth = 800;
  const chartHeight = 260;
  const chartPadding = 12;

  const chartMax = Math.max(
    ...trendData.map((item) => item.value),
    1
  );

  const getChartX = (index) => {
    if (trendData.length <= 1) {
      return chartWidth / 2;
    }

    return (
      chartPadding +
      (index / (trendData.length - 1)) *
        (chartWidth - chartPadding * 2)
    );
  };

  const getChartY = (value) =>
    chartHeight -
    chartPadding -
    (value / chartMax) *
      (chartHeight - chartPadding * 2);

  const revenueLinePath = trendData
    .map((item, index) => {
      const x = getChartX(index);
      const y = getChartY(item.value);

      return `${index === 0 ? "M" : "L"}${x} ${y}`;
    })
    .join(" ");

  const revenueAreaPath = trendData.length
    ? `${revenueLinePath}
       L${getChartX(trendData.length - 1)} ${chartHeight}
       L${getChartX(0)} ${chartHeight}
       Z`
    : "";

  // -----------------------------------------
  // KPI DATA
  // -----------------------------------------

  const kpis = [
    {
      title: "Total Revenue",
      value: formatCurrency(kpiData.revenue?.total),
      change:
        kpiData.period_change_percent !== undefined
          ? `${
              Number(kpiData.period_change_percent) >= 0
                ? "+"
                : ""
            }${Number(
              kpiData.period_change_percent
            ).toFixed(2)}%`
          : "—",
      positive:
        Number(kpiData.period_change_percent) >= 0,
      icon: DollarSign,
    },
    {
      title: "Total Profit",
      value: formatCurrency(kpiData.profit?.total),
      change:
        kpiData.profit_margin_percent !== undefined
          ? `${Number(
              kpiData.profit_margin_percent
            ).toFixed(2)}% margin`
          : "—",
      positive: Number(kpiData.profit?.total) >= 0,
      icon: TrendingUp,
    },
    {
      title: "Quantity Sold",
      value: formatNumber(kpiData.quantity?.total),
      change:
        kpiData.quantity?.average !== undefined
          ? `${formatNumber(
              kpiData.quantity.average
            )} avg. / record`
          : "—",
      positive: true,
      icon: ShoppingCart,
    },
    {
      title: "Profit Margin",
      value: formatPercent(
        kpiData.profit_margin_percent
      ),
      change:
        kpiData.profit?.total !== undefined
          ? `${formatCurrency(
              kpiData.profit.total
            )} profit`
          : "—",
      positive:
        Number(kpiData.profit_margin_percent) >= 0,
      icon: Activity,
    },
  ];

  
  if (!authenticated) {
  return (
    <Login
      onLogin={() => setAuthenticated(true)}
    />
  );
}
  // -----------------------------------------
  // LOADING
  // -----------------------------------------

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />

        <strong>
          Loading business data...
        </strong>

        <span>
          Connecting to your AI Business OS backend
        </span>
      </div>
    );
  }

  // -----------------------------------------
  // ERROR
  // -----------------------------------------

  if (error) {
    return (
      <div className="error-screen">
        <strong>
          Dashboard data could not be loaded.
        </strong>

        <span>{error}</span>

        <button
          className="primary-button"
          onClick={() =>
            window.location.reload()
          }
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <motion.aside
        className={`sidebar ${
          sidebarOpen ? "open" : "collapsed"
        }`}
        animate={{
          width: sidebarOpen ? 250 : 82,
        }}
        transition={{
          duration: 0.25,
        }}
      >

        <div className="brand">

          <div className="brand-logo">
            <Sparkles size={20} />
          </div>

          {sidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="brand-text"
            >
              <strong>
                AI Business OS
              </strong>

              <span>
                Business Intelligence
              </span>
            </motion.div>
          )}

        </div>

        <nav className="navigation">

          <div className="nav-section">

            {sidebarOpen && (
              <span className="nav-label">
                WORKSPACE
              </span>
            )}

            {navigation.map((item) => {
              const Icon = item.icon;

              const active =
                activePage === item.name;

              return (
                <button
                  key={item.name}
                  className={`nav-item ${
                    active ? "active" : ""
                  }`}
                  onClick={() =>
                    setActivePage(item.name)
                  }
                >

                  <Icon size={20} />

                  {sidebarOpen && (
                    <span>
                      {item.name}
                    </span>
                  )}

                </button>
              );
            })}

          </div>

          <div className="nav-bottom">

            <button className="nav-item">

              <Settings size={20} />

              {sidebarOpen && (
                <span>
                  Settings
                </span>
              )}

            </button>

          </div>

        </nav>

        {sidebarOpen && (
          <div className="sidebar-ai-card">

            <div className="ai-icon">
              <BrainCircuit size={18} />
            </div>

            <strong>
              AI Analyst
            </strong>

            <p>
              Ask questions about your business data.
            </p>

            <button
              onClick={() =>
                setActivePage("AI Analyst")
              }
            >
              Open Analyst
              <ArrowUpRight size={15} />
            </button>

          </div>
        )}

      </motion.aside>

      {/* MAIN */}

      <main className="main-content">

        {/* TOPBAR */}

        <header className="topbar">

          <div className="topbar-left">

            <button
              className="icon-button"
              onClick={() =>
                setSidebarOpen(!sidebarOpen)
              }
            >
              <Menu size={21} />
            </button>

            <div className="breadcrumb">

              <span>
                Workspace
              </span>

              <strong>
                /
              </strong>

              <b>
                {activePage}
              </b>

            </div>

          </div>

          <div className="topbar-right">

            <button className="icon-button">
              <Search size={21} />
            </button>

            <button className="icon-button">
              <Bell size={21} />
            </button>

            <button
              className="primary-button"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>  

        </header>

        {/* PAGE */}

        <AnimatePresence mode="wait">

          {activePage === "Dashboard" && (

            <motion.div
              key="dashboard"
              className="page"
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -10,
              }}
              transition={{
                duration: 0.25,
              }}
            >

              {/* PAGE HEADER */}

              <div className="page-header">

                <div>

                  <div className="eyebrow">

                    <span className="status-dot" />

                    LIVE BUSINESS DATA

                  </div>

                  <h1>
                    Business Overview
                  </h1>

                  <p>
                    Monitor your business performance
                    and discover actionable insights.
                  </p>

                </div>

                <button className="primary-button">

                  <Sparkles size={17} />

                  Ask AI

                </button>

              </div>

              {/* KPI GRID */}

              <div className="kpi-grid">

                {kpis.map((kpi, index) => {

                  const Icon = kpi.icon;

                  return (
                    <motion.div
                      key={kpi.title}
                      className="kpi-card"
                      initial={{
                        opacity: 0,
                        y: 20,
                      }}
                      animate={{
                        opacity: 1,
                        y: 0,
                      }}
                      transition={{
                        delay: index * 0.08,
                      }}
                      whileHover={{
                        y: -4,
                      }}
                    >

                      <div className="kpi-top">

                        <div className="kpi-icon">
                          <Icon size={19} />
                        </div>

                        <span
                          className={
                            kpi.positive
                              ? "change positive"
                              : "change negative"
                          }
                        >

                          {kpi.positive ? (
                            <TrendingUp size={14} />
                          ) : (
                            <TrendingDown size={14} />
                          )}

                          {kpi.change}

                        </span>

                      </div>

                      <span className="kpi-title">
                        {kpi.title}
                      </span>

                      <strong className="kpi-value">
                        {kpi.value}
                      </strong>

                      <span className="kpi-period">
                        vs. previous period
                      </span>

                    </motion.div>
                  );
                })}

              </div>

              {/* ANALYTICS GRID */}

              <div className="analytics-grid">

                {/* REVENUE */}

                <motion.section
                  className="panel revenue-panel"
                  initial={{
                    opacity: 0,
                    y: 20,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    delay: 0.35,
                  }}
                >

                  <div className="panel-header">

                    <div>

                      <h2>
                        Revenue Overview
                      </h2>

                      <span>
                        Monthly performance
                      </span>

                    </div>

                    <select defaultValue="12">

                      <option value="12">
                        Last 12 months
                      </option>

                      <option value="6">
                        Last 6 months
                      </option>

                    </select>

                  </div>

                  <div className="revenue-summary">

                    <strong>
                      {formatCurrency(
                        kpiData.revenue?.total
                      )}
                    </strong>

                    <span
                      className={
                        Number(
                          kpiData.period_change_percent
                        ) >= 0
                          ? "positive"
                          : "negative"
                      }
                    >

                      {kpiData.period_change_percent !==
                      undefined
                        ? `${
                            Number(
                              kpiData.period_change_percent
                            ) >= 0
                              ? "+"
                              : ""
                          }${Number(
                            kpiData.period_change_percent
                          ).toFixed(2)}%`
                        : "—"}

                    </span>

                  </div>

                  <div className="chart">

                    <div className="chart-grid">

                      <span />
                      <span />
                      <span />
                      <span />

                    </div>

                    <svg
                      viewBox="0 0 800 260"
                      preserveAspectRatio="none"
                      className="chart-svg"
                    >

                      <defs>

                        <linearGradient
                          id="areaGradient"
                          x1="0"
                          x2="0"
                          y1="0"
                          y2="1"
                        >

                          <stop
                            offset="0%"
                            stopColor="#8b5cf6"
                            stopOpacity="0.3"
                          />

                          <stop
                            offset="100%"
                            stopColor="#8b5cf6"
                            stopOpacity="0"
                          />

                        </linearGradient>

                      </defs>

                      {revenueAreaPath && (
                        <motion.path
                          d={revenueAreaPath}
                          fill="url(#areaGradient)"
                          initial={{
                            opacity: 0,
                          }}
                          animate={{
                            opacity: 1,
                          }}
                          transition={{
                            duration: 0.8,
                          }}
                        />
                      )}

                      {revenueLinePath && (
                        <motion.path
                          d={revenueLinePath}
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          vectorEffect="non-scaling-stroke"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          initial={{
                            pathLength: 0,
                            opacity: 0,
                          }}
                          animate={{
                            pathLength: 1,
                            opacity: 1,
                          }}
                          transition={{
                            duration: 1.2,
                            ease: "easeInOut",
                          }}
                        />
                      )}

                    </svg>

                    <div className="chart-labels">

                      {trendData.map((item) => (
                        <span key={item.period}>
                          {item.period}
                        </span>
                      ))}

                    </div>

                  </div>

                </motion.section>

                {/* AI INSIGHTS */}

                <motion.section
                  className="panel insights-panel"
                  initial={{
                    opacity: 0,
                    y: 20,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    delay: 0.42,
                  }}
                >

                  <div className="panel-header">

                    <div>

                      <h2>
                        AI Insights
                      </h2>

                      <span>
                        Latest business intelligence
                      </span>

                    </div>

                    <button className="text-button">

                      View all

                      <ArrowUpRight size={15} />

                    </button>

                  </div>

                  {/* DYNAMIC BACKEND INSIGHTS */}

                  <div className="insight-list">

                    {(dashboard?.insights?.items ?? [])
                      .slice(0, 5)
                      .map((insight, index) => {

                        const icons = [
                          TrendingUp,
                          ShoppingCart,
                          Activity,
                          Lightbulb,
                          Sparkles,
                        ];

                        const colors = [
                          "purple",
                          "blue",
                          "orange",
                          "purple",
                          "blue",
                        ];

                        const Icon =
                          icons[index % icons.length];

                        return (
                          <motion.div
                            className="insight"
                            key={`${insight.title}-${index}`}
                            initial={{
                              opacity: 0,
                              x: 15,
                            }}
                            animate={{
                              opacity: 1,
                              x: 0,
                            }}
                            transition={{
                              delay:
                                0.45 +
                                index * 0.08,
                            }}
                          >

                            <div
                              className={`insight-icon ${
                                colors[
                                  index %
                                    colors.length
                                ]
                              }`}
                            >
                              <Icon size={17} />
                            </div>

                            <div>

                              <strong>
                                {insight.title}
                              </strong>

                              <p>
                                {insight.description}
                              </p>

                            </div>

                          </motion.div>
                        );
                      })}

                  </div>

                </motion.section>

              </div>

              {/* LOWER GRID */}

              <div className="bottom-grid">

                {/* TOP PRODUCTS */}

                <section className="panel">

                  <div className="panel-header">

                    <div>

                      <h2>
                        Top Products
                      </h2>

                      <span>
                        Best performing products
                      </span>

                    </div>

                    <button className="text-button">
                      View report
                    </button>

                  </div>

                  <div className="product-list">

                    {[
                      [
                        kpiData.top_product?.name ||
                          "Top product",

                        formatCurrency(
                          kpiData.top_product?.total
                        ),

                        `${Number(
                          kpiData.top_product_contribution_percent ||
                            0
                        ).toFixed(2)}%`,
                      ],
                    ].map(
                      (product, index) => (

                        <div
                          className="product-row"
                          key={product[0]}
                        >

                          <div className="product-rank">
                            0{index + 1}
                          </div>

                          <div className="product-name">

                            <strong>
                              {product[0]}
                            </strong>

                            <div className="progress">

                              <span
                                style={{
                                  width:
                                    product[2],
                                }}
                              />

                            </div>

                          </div>

                          <strong>
                            {product[1]}
                          </strong>

                          <span className="positive">
                            {product[2]}
                          </span>

                        </div>

                      )
                    )}

                  </div>

                </section>

                {/* AI PROMPT */}

                <section className="panel ai-prompt-panel">

                  <div className="ai-prompt-icon">

                    <BrainCircuit size={24} />

                  </div>

                  <h2>
                    Ask your data anything
                  </h2>

                  <p>
                    Let AI analyze your business data,
                    identify trends and generate charts.
                  </p>

                  <button
                    className="primary-button full"
                    onClick={() =>
                      setActivePage("AI Analyst")
                    }
                  >

                    <Sparkles size={17} />

                    Open AI Analyst

                  </button>

                </section>

              </div>

            </motion.div>
          )}

          {activePage === "Datasets" && (
            <motion.div
              key="datasets"
              className="page"
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -10,
              }}
            >
              <div className="page-header">
                <div>
                  <div className="eyebrow">
                    <span className="status-dot" />
                    DATA MANAGEMENT
                  </div>

                  <h1>
                    Datasets
                  </h1>

                  <p>
                    Upload and manage your business data.
                  </p>
                </div>
              </div>

              <section className="panel">
                <div className="panel-header">
                  <div>
                    <h2>
                      Upload Dataset
                    </h2>

                    <span>
                      CSV and Excel files are supported.
                    </span>
                  </div>
                </div>

                <div className="dataset-upload">
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) =>
                      setSelectedFile(
                        e.target.files[0] || null
                      )
                    }
                  />

                  {selectedFile && (
                    <p>
                      Selected file:{" "}
                      <strong>
                        {selectedFile.name}
                      </strong>
                    </p>
                  )}

                  <button
                    className="primary-button"
                    onClick={handleDatasetUpload}
                    disabled={uploading || !selectedFile}
                  >
                    {uploading ? "Uploading..." : "Upload Dataset"}
                  </button>

                  {uploadMessage && (
                    <div className="upload-success">
                      {uploadMessage}
                    </div>
                  )}

                  {uploadError && (
                    <div className="upload-error">
                      {uploadError}
                    </div>
                  )}
                </div>
              </section>
            </motion.div>
          )}

          {activePage === "AI Analyst" && (
            <motion.div
              key="ai-analyst"
              className="page"
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -10,
              }}
            >
              <div className="page-header">
                <div>
                  <div className="eyebrow">
                    <span className="status-dot" />
                    AI BUSINESS ANALYST
                  </div>

                  <h1>
                    AI Analyst
                  </h1>

                  <p>
                    Ask questions about your business data.
                  </p>
                </div>
              </div>

              <section className="panel ai-chat-panel">
                <div className="panel-header">
                  <div>
                    <h2>
                      Ask Your Data
                    </h2>

                    <span>
                      Powered by your selected dataset.
                    </span>
                  </div>
                </div>

                <div className="ai-question-box">
                 <div className="ai-suggestions">
  <span>Try asking:</span>

  {[
    "What is the total revenue?",
    "Which product generates the most revenue?",
    "Which region performs best?",
    "What is the profit margin?",
    "What was the best sales period?",
    "What was the worst sales period?",
  ].map((question) => (
    <button
      key={question}
      type="button"
      className="secondary-button"
      onClick={() => setAiQuestion(question)}
    >
      {question}
    </button>
  ))}
</div>
                  <div className="ai-dataset-selector">
                    <label>Dataset</label>

                    <select
                      value={aiDatasetId || ""}
                      onChange={(e) => {
                        setAiDatasetId(e.target.value);
                        setAiResponse(null);
                        setSelectedAiChart(null);
                        setAiError("");
                      }}
                    >
                      <option value="">Select a dataset</option>

                      {datasets.map((dataset) => (
                        <option key={dataset.id} value={dataset.id}>
                          {dataset.filename}
                        </option>
                      ))}
                    </select>
                  </div>

                  <textarea
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    placeholder="Ask something like: What is the total revenue?"
                    rows={4}
                  />

                  <button
                    className="primary-button"
                    onClick={handleAskAI}
                    disabled={aiLoading || !aiQuestion.trim() || !aiDatasetId }
                  >
                    <Sparkles size={17} />
                    {aiLoading ? "Analyzing..." : "Ask AI"}
                  </button>
                </div>

                {aiError && <div className="upload-error">{aiError}</div>}

                {aiResponse && (
                  <div className="ai-results">
                    <section className="panel">
                      <div className="ai-response-header">
                        <BrainCircuit size={18} />
                        <strong>AI Analyst</strong>
                      </div>

                      <div className="ai-answer">
                        <p>{aiResponse.answer}</p>
                      </div>

                      {aiResponse.analysis_type && (
                        <div className="ai-result-meta">
                          Analysis type:
                          <strong>{aiResponse.analysis_type}</strong>
                        </div>
                      )}
                    </section>

                    {aiResponse.kpis && (
                      <section className="ai-kpi-grid">
                        <div className="ai-kpi-card">
                          <span>Total Revenue</span>
                          <strong>
                            {formatCurrency(aiResponse.kpis.revenue?.total)}
                          </strong>
                        </div>

                        <div className="ai-kpi-card">
                          <span>Total Profit</span>
                          <strong>
                            {formatCurrency(aiResponse.kpis.profit?.total)}
                          </strong>
                        </div>

                        <div className="ai-kpi-card">
                          <span>Quantity Sold</span>
                          <strong>
                            {formatNumber(aiResponse.kpis.quantity?.total)}
                          </strong>
                        </div>

                        <div className="ai-kpi-card">
                          <span>Profit Margin</span>
                          <strong>
                            {formatPercent(aiResponse.kpis.profit_margin_percent)}
                          </strong>
                        </div>
                      </section>
                    )}

                    {selectedAiChart && (
                      <section className="panel">
                        <AIChart chart={selectedAiChart} />
                      </section>
                    )}

                    {aiResponse.available_charts?.length > 1 && (
                      <section className="panel">
                        <div className="panel-header">
                          <div>
                            <h2>Explore Analysis</h2>
                            <span>
                              View different perspectives of your business data.
                            </span>
                          </div>
                        </div>

                        <div className="ai-chart-buttons">
                          {aiResponse.available_charts.map((chart, index) => (
                            <button
                              key={`${chart.title}-${index}`}
                              className="secondary-button"
                              onClick={() => setSelectedAiChart(chart)}
                            >
                              {chart.title}
                            </button>
                          ))}
                        </div>
                      </section>
                    )}
                  </div>
                )}
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;