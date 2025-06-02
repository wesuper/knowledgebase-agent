import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import MermaidRenderer from '@/components/MermaidRenderer';
import Link from 'next/link';

const API_FILE_BASE_URL = process.env.NEXT_PUBLIC_API_FILE_BASE_URL || 'http://localhost:8000/api/files';

const ViewFilePage: React.FC = () => {
  const router = useRouter();
  const { filePath } = router.query;

  const [rawContent, setRawContent] = useState<string | null>(null);
  const [mermaidCode, setMermaidCode] = useState<string | null>(null);
  const [mainMarkdown, setMainMarkdown] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pageTitle, setPageTitle] = useState<string>("View File");

  useEffect(() => {
    if (router.isReady && filePath && Array.isArray(filePath) && filePath.length > 0) {
      const path = filePath.join('/');
      // Use the last part of the path (filename) for the page title, or a default
      setPageTitle(decodeURIComponent(filePath[filePath.length - 1] || "View File"));
      setIsLoading(true);
      setError(null);

      console.log(`Fetching file from: ${API_FILE_BASE_URL}/${path}`);
      axios.get(`${API_FILE_BASE_URL}/${path}`)
        .then(response => {
          let content = response.data;
          if (typeof content === 'object' && content !== null && 'content' in content) {
            content = content.content as string;
          } else if (typeof content !== 'string') {
            console.error("Unexpected response data format:", response.data);
            throw new Error("Received unexpected data format from server.");
          }
          setRawContent(content);

          const separator = '\n\n---\n\n';
          const parts = content.split(separator);

          if (parts.length >= 2 && parts[0].trim().startsWith('```mermaid')) {
            setMermaidCode(parts[0].trim());
            setMainMarkdown(parts.slice(1).join(separator));
          } else {
            setMermaidCode(null);
            setMainMarkdown(content);
          }
        })
        .catch(err => {
          console.error("Error fetching file:", err);
          setError(err.response?.data?.detail || err.response?.data?.message || err.message || "Failed to load file.");
          setRawContent(null);
          setMermaidCode(null);
          setMainMarkdown(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else if (router.isReady) {
      if (!filePath) {
        setError("File path not specified or invalid.");
      } else if (!Array.isArray(filePath) || filePath.length === 0) {
        setError("Invalid file path structure.");
      }
      setIsLoading(false);
    }
  }, [filePath, router.isReady]);

  const renderLoading = () => (
    <div style={{ textAlign: 'center', padding: '40px' }}>
      <p style={{ fontSize: '1.2rem' }}>Loading content...</p>
      {/* Re-using spinner style from index.tsx for consistency if needed, or a simpler message */}
    </div>
  );

  const renderError = () => (
    <div className="error-message" style={{ margin: '20px' }}>
      <p>Error: {error}</p>
      <Link href="/" legacyBehavior><a>&larr; Back to Home</a></Link>
    </div>
  );

  const renderNoContent = () => (
     <div style={{ textAlign: 'center', padding: '40px', color: '#555' }}>
      <p>No content found for this path, or content is empty.</p>
      <Link href="/" legacyBehavior><a>&larr; Back to Home</a></Link>
    </div>
  );

  if (isLoading) return renderLoading();
  if (error) return <div className="container">{renderError()}</div>; // Wrap error in container for consistent width
  if (!rawContent && !isLoading) return <div className="container">{renderNoContent()}</div>;

  return (
    // Use the global 'container' class
    <div className="container">
      <header style={{ marginBottom: '30px', borderBottom: '1px solid #eee', paddingBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.8em' }}>{pageTitle}</h1>
        <Link href="/" legacyBehavior><a style={{ fontSize: '1em', textDecoration: 'none' }}>&larr; Back to Home</a></Link>
      </header>

      {mermaidCode && (
        <section style={{ marginBottom: '30px' }}>
          <h2 style={{ fontSize: '1.5em', marginBottom: '10px', borderBottom: '1px solid #eee', paddingBottom: '5px' }}>Mind Map</h2>
          {/* MermaidRenderer already uses the 'mermaid-diagram-container' class */}
          <MermaidRenderer mermaidCode={mermaidCode} />
        </section>
      )}

      <section>
        <h2 style={{ fontSize: '1.5em', marginBottom: '10px', borderBottom: '1px solid #eee', paddingBottom: '5px' }}>Content</h2>
        {/* Apply markdown-body class for styling from globals.css */}
        <article className="markdown-body">
          <ReactMarkdown>{mainMarkdown || rawContent}</ReactMarkdown>
        </article>
      </section>
    </div>
  );
};

export default ViewFilePage;
