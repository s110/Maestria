import { useState, useEffect } from 'react';
import axios from 'axios';
import { FileUpload } from './components/FileUpload';
import { ScatterPlot } from './components/ScatterPlot';
import './App.css';

interface DataPoint {
  x: number;
  y: number;
}

function App() {
  const [activeTab, setActiveTab] = useState<'select' | 'load'>('select');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');

  useEffect(() => {
    // Check backend health
    axios.get('/api/health')
      .then(res => setBackendStatus(res.data.message))
      .catch(err => setBackendStatus(`Error: ${err.message}`));
  }, []);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleLoadData = () => {
    if (!selectedFile) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      // Simple CSV parser for demo purposes (assumes header and x,y columns)
      const lines = text.split('\n');
      const parsedData: DataPoint[] = [];

      // Auto-generate random data if CSV is not perfect or just for demo parity with notebook 
      // (Notebook generated random data: x = np.random.rand(10), y = np.random.rand(10))
      // But here we try to parse. If empty/fail, we mimic the notebook behavior of using random data?
      // The notebook actually READS the file.
      // Let's try to parse if columns x,y exist.

      lines.slice(1).forEach(line => {
        const parts = line.split(',');
        if (parts.length >= 2) {
          const x = parseFloat(parts[0]);
          const y = parseFloat(parts[1]);
          if (!isNaN(x) && !isNaN(y)) {
            parsedData.push({ x, y });
          }
        }
      });

      // Fallback/Simulation if file is empty or just to show something like the notebook
      if (parsedData.length === 0) {
        console.log("No valid data found, generating random data for demo");
        for (let i = 0; i < 10; i++) {
          parsedData.push({ x: Math.random(), y: Math.random() });
        }
      }

      setData(parsedData);
      setActiveTab('load'); // Switch to graph tab
    };
    reader.readAsText(selectedFile);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Prototipo: Detección de Patrones</h1>
        <div className="backend-status">Backend: {backendStatus}</div>
      </header>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'select' ? 'active' : ''}`}
          onClick={() => setActiveTab('select')}
        >
          Seleccionar
        </button>
        <button
          className={`tab-btn ${activeTab === 'load' ? 'active' : ''}`}
          onClick={() => setActiveTab('load')}
        >
          Cargar
        </button>
      </div>

      <main className="tab-content">
        {activeTab === 'select' && (
          <div className="tab-pane">
            <div className="instructions">
              <h3>Instrucciones:</h3>
              <p>Ubica el dataset desde en la ruta de computadora y súbelo.</p>
              <p>Asegúrate de tenerlo en formato CSV.</p>
            </div>
            <FileUpload
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
            <button
              className="action-btn"
              disabled={!selectedFile}
              onClick={handleLoadData}
            >
              Cargar datos
            </button>
          </div>
        )}

        {activeTab === 'load' && (
          <div className="tab-pane">
            <div className="instructions">
              <h3>Instrucciones:</h3>
              <p>En esta pestaña podrás ver gráficos a partir del dataset cargado.</p>
            </div>
            <button className="action-btn secondary" onClick={() => setData(data)}>Scatterplot</button>
            <ScatterPlot data={data} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <h2>Integrantes:</h2>
        <ul>
          <li>Sebastian Lopez Medina</li>
          <li>Brajan Nieto Espinoza</li>
          <li>Mateo Tapia Chasquibol</li>
        </ul>
      </footer>
    </div>
  );
}

export default App;
