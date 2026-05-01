import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const metrics = [
  { value: '4', label: 'Tender PDFs in' },
  { value: '9+', label: 'Submission files out' },
  { value: 'Local', label: 'Runs on your PC' },
];

const workflow = [
  {
    title: 'Upload Tender PDFs',
    body: 'Add Notice, TDS, BOQ, and supporting tender files into one local folder.',
  },
  {
    title: 'Extract and Cross-check',
    body: 'The parser reads tender fields, flags duplicates, and marks missing or conflicting data for review.',
  },
  {
    title: 'Generate Documents',
    body: 'DOCX declarations, bank forms, work plans, and Excel BOQ sheets are created from your templates.',
  },
];

const features = [
  'Notice, TDS, and BOQ field extraction',
  'DOCX template fill-up with custom instructions',
  'Excel BOQ and work-plan generation',
  'Compare, Duplicate, Approval, and Final Review sheets',
  'Local-first workflow for tender teams',
  'Ready for desktop packaging later',
];

export default function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFiles = (event) => {
    setSelectedFiles(Array.from(event.target.files || []));
    setResult(null);
    setError('');
  };

  const processTender = async () => {
    if (selectedFiles.length < 3) {
      setError('Please select at least Notice, TDS, and BOQ PDF files.');
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append('files', file));

    setProcessing(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/tender/process`, {
        method: 'POST',
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || 'Tender processing failed.');
      }
      setResult(payload);
    } catch (err) {
      setError(err.message || 'Tender processing failed.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <main className="site-shell">
      <nav className="nav-bar" aria-label="Main navigation">
        <a className="brand" href="#top" aria-label="TenderFlow Local home">
          <span className="brand-mark">TF</span>
          <span>TenderFlow Local</span>
        </a>
        <div className="nav-links">
          <a href="#processor">Processor</a>
          <a href="#workflow">Workflow</a>
          <a href="#features">Features</a>
          <a href="#contact">Contact</a>
        </div>
      </nav>

      <section id="top" className="hero-section">
        <div className="hero-content">
          <p className="eyebrow">Local tender document automation</p>
          <h1>Generate tender DOCX and Excel files from PDF documents.</h1>
          <p className="hero-copy">
            TenderFlow Local extracts data from e-GP Notice, TDS, and BOQ PDFs,
            cross-checks key fields, and creates submission-ready document packs
            using your own official templates.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#processor">Process PDFs</a>
            <a className="button secondary" href="#workflow">See workflow</a>
          </div>
        </div>

        <div className="product-preview" aria-label="Tender automation dashboard preview">
          <div className="preview-topbar">
            <span></span><span></span><span></span>
            <strong>Review Export</strong>
          </div>
          <div className="preview-grid">
            <div className="preview-panel wide">
              <span className="status-pill green">Matched</span>
              <h2>{result?.tender_id || '541339'}</h2>
              <p>{result ? result.message : 'Notice, TDS, BOQ extracted and ready for approval.'}</p>
            </div>
            <div className="preview-panel">
              <span className="status-pill amber">Review</span>
              <p>Fields needing confirmation are exported for review.</p>
            </div>
            <div className="preview-panel">
              <span className="status-pill green">Complete</span>
              <p>{result ? `${result.files.length} files prepared` : 'DOCX and Excel outputs prepared'}</p>
            </div>
          </div>
          <div className="preview-table">
            <div><b>Field</b><b>Status</b><b>Source</b></div>
            <div><span>Tender ID</span><span className="ok">Matched</span><span>Notice</span></div>
            <div><span>Security</span><span className="ok">Matched</span><span>Notice</span></div>
            <div><span>Equipment</span><span className="check">Review</span><span>TDS</span></div>
          </div>
        </div>
      </section>

      <section className="metrics-strip" aria-label="Key product facts">
        {metrics.map((item) => (
          <div key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </div>
        ))}
      </section>

      <section id="processor" className="processor-section">
        <div className="section-heading">
          <p className="eyebrow">Actual processing</p>
          <h2>Upload tender PDFs and generate files locally.</h2>
          <p>
            Select the Notice, TDS, BOQ, and any related tender PDFs. The backend
            will save them into the local tender engine, run extraction, fill
            templates, and return generated output links.
          </p>
        </div>

        <div className="processor-panel">
          <label className="file-drop">
            <span>Select tender PDF files</span>
            <input type="file" accept="application/pdf,.pdf" multiple onChange={handleFiles} />
          </label>

          {selectedFiles.length > 0 && (
            <div className="file-list">
              {selectedFiles.map((file) => (
                <span key={`${file.name}-${file.size}`}>{file.name}</span>
              ))}
            </div>
          )}

          <button className="button primary" type="button" onClick={processTender} disabled={processing}>
            {processing ? 'Processing...' : 'Generate DOCX and Excel files'}
          </button>

          {error && <div className="message-box error">{error}</div>}

          {result && (
            <div className="result-panel">
              <div className="result-header">
                <span className="status-pill green">Success</span>
                <strong>Tender ID: {result.tender_id}</strong>
              </div>
              <p>{result.message}</p>
              <div className="generated-files">
                {result.files.map((file) => (
                  <a key={file.url} href={file.url} target="_blank" rel="noreferrer">
                    <span>{file.name}</span>
                    <small>{file.size_kb} KB</small>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      <section id="workflow" className="section-block">
        <div className="section-heading">
          <p className="eyebrow">Workflow</p>
          <h2>From tender PDFs to review-ready outputs.</h2>
        </div>
        <div className="workflow-grid">
          {workflow.map((step, index) => (
            <article className="workflow-card" key={step.title}>
              <span className="step-number">0{index + 1}</span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="features" className="section-block feature-section">
        <div className="section-heading narrow">
          <p className="eyebrow">Capabilities</p>
          <h2>Built around real tender office work.</h2>
          <p>
            The system is designed for repeatable local generation, not one-off
            manual copying between PDFs, Word files, and spreadsheets.
          </p>
        </div>
        <div className="feature-list">
          {features.map((feature) => (
            <div className="feature-item" key={feature}>
              <span aria-hidden="true">✓</span>
              <p>{feature}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-band">
        <div>
          <p className="eyebrow">Deployment path</p>
          <h2>Start locally, then move to production when ready.</h2>
        </div>
        <a className="button primary light" href="#contact">Plan deployment</a>
      </section>

      <section id="contact" className="contact-section">
        <div className="contact-copy">
          <p className="eyebrow">Contact</p>
          <h2>Tell us what tender files you need generated.</h2>
          <p>
            Share your template list, PDF types, and preferred output format.
            The first production milestone is a clean local build with reliable
            extraction, cross-checking, and export.
          </p>
        </div>

        <form className="contact-form" onSubmit={(event) => event.preventDefault()}>
          <label>
            Name
            <input type="text" name="name" placeholder="Your name" />
          </label>
          <label>
            Email
            <input type="email" name="email" placeholder="you@example.com" />
          </label>
          <label>
            Project details
            <textarea name="message" rows="5" placeholder="Tell us about the tender document workflow you want to automate." />
          </label>
          <button className="button primary" type="submit">Send request</button>
        </form>
      </section>
    </main>
  );
}
