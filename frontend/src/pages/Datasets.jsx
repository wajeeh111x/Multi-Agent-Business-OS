import { useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  FileSpreadsheet,
  FileText,
  Trash2,
  Database,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000";

function Datasets() {
  const fileInputRef = useRef(null);
    
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [datasets, setDatasets] = useState([]);

  function handleFileChange(e) {
    const selectedFile = e.target.files?.[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setMessage("");
    setError("");
  }

  async function handleUpload() {
    if (!file) {
      setError("Please select a CSV or Excel file.");
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_BASE_URL}/business/datasets/upload`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Dataset upload failed."
        );
      }

      setDatasets((previous) => [
        {
          id: data.dataset_id,
          filename: data.filename,
          size: data.size_bytes,
        },
        ...previous,
      ]);

      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      setMessage("Dataset uploaded successfully.");
    } catch (err) {
      setError(
        err.message || "Unable to upload dataset."
      );
    } finally {
      setUploading(false);
    }
  }

  function formatSize(bytes) {
    if (!bytes) return "—";

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <motion.div
      className="page"
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.25,
      }}
    >
      <div className="page-header">
        <div>
          <div className="eyebrow">
            <span className="status-dot" />
            BUSINESS DATA
          </div>

          <h1>Datasets</h1>

          <p>
            Upload and manage the business data used
            by your AI Business OS.
          </p>
        </div>
      </div>

      <section className="panel dataset-upload-panel">
        <div className="panel-header">
          <div>
            <h2>Upload Dataset</h2>

            <span>
              CSV and Excel files up to 50 MB
            </span>
          </div>

          <Database size={22} />
        </div>

        <div
          className="dataset-dropzone"
          onClick={() =>
            fileInputRef.current?.click()
          }
        >
          <Upload size={30} />

          <strong>
            {file
              ? file.name
              : "Choose a dataset"}
          </strong>

          <span>
            Click here to select CSV or Excel
          </span>

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            hidden
            onChange={handleFileChange}
          />
        </div>

        {file && (
          <div className="selected-file">
            <FileSpreadsheet size={20} />

            <div>
              <strong>{file.name}</strong>

              <span>
                {formatSize(file.size)}
              </span>
            </div>
          </div>
        )}

        {message && (
          <div className="dataset-message success">
            <CheckCircle size={17} />
            {message}
          </div>
        )}

        {error && (
          <div className="dataset-message error">
            <AlertCircle size={17} />
            {error}
          </div>
        )}

        <button
          className="primary-button"
          onClick={handleUpload}
          disabled={uploading || !file}
        >
          <Upload size={17} />

          {uploading
            ? "Uploading..."
            : "Upload Dataset"}
        </button>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Your Datasets</h2>

            <span>
              Uploaded business data
            </span>
          </div>
        </div>

        {datasets.length === 0 ? (
          <div className="dataset-empty">
            <FileText size={32} />

            <strong>
              No datasets uploaded yet
            </strong>

            <span>
              Upload your first CSV or Excel
              dataset above.
            </span>
          </div>
        ) : (
          <div className="dataset-list">
            {datasets.map((dataset) => (
              <div
                className="dataset-row"
                key={dataset.id}
              >
                <div className="dataset-icon">
                  <FileSpreadsheet size={20} />
                </div>

                <div className="dataset-info">
                  <strong>
                    {dataset.filename}
                  </strong>

                  <span>
                    {formatSize(dataset.size)}
                  </span>
                </div>

                <span className="dataset-status">
                  Uploaded
                </span>

                <button
                  className="icon-button"
                  title="Delete dataset"
                  onClick={() =>
                    setDatasets((items) =>
                      items.filter(
                        (item) =>
                          item.id !== dataset.id
                      )
                    )
                  }
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
}

export default Datasets;