import React, { useEffect, useRef, useId } from 'react';
import mermaid from 'mermaid';

interface MermaidRendererProps {
  mermaidCode: string;
  // id prop is removed as useId hook will generate a unique ID for the SVG.
}

const MermaidRenderer: React.FC<MermaidRendererProps> = ({ mermaidCode }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const uniqueDiagramIdPart = useId().replace(/:/g, '-'); // Make ID more CSS friendly

  useEffect(() => {
    // Initialize Mermaid.
    // It's generally safe to call this multiple times if it checks its own initialized state.
    // `startOnLoad: false` is crucial because we are manually rendering.
    try {
      mermaid.initialize({ startOnLoad: false, theme: 'default' });
    } catch (e: any) {
      // Catch error if mermaid.initialize throws (e.g. if called with invalid config)
      console.error("Mermaid initialization error:", e.message || e);
      if (containerRef.current) {
        containerRef.current.innerHTML = `<pre>Error initializing Mermaid renderer:\n${e.message || e}</pre>`;
      }
      return; // Stop if initialization fails
    }


    if (mermaidCode && containerRef.current) {
      containerRef.current.innerHTML = ''; // Clear previous diagram before rendering

      try {
        const svgId = `mermaid-svg-${uniqueDiagramIdPart}`;

        // Asynchronously render the Mermaid diagram
        // mermaid.render returns a promise if a callback is not provided,
        // or calls the callback with the svg.
        // Using the callback method here.
        mermaid.render(svgId, mermaidCode, (svgCode, bindFunctions) => {
          if (containerRef.current) {
            containerRef.current.innerHTML = svgCode;
            if (bindFunctions) {
              bindFunctions(containerRef.current); // Bind events if any
            }
          }
        });

      } catch (e: any) {
        console.error("Mermaid rendering error:", e.message || e);
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre>Error rendering diagram:\n${e.message || e}</pre>`;
        }
      }
    } else if (containerRef.current) {
      containerRef.current.innerHTML = mermaidCode ? '' : '<p>No diagram code provided.</p>';
    }
  }, [mermaidCode, uniqueDiagramIdPart]);

  // Apply the className from globals.css for consistent styling
  return <div ref={containerRef} className="mermaid-diagram-container"></div>;
};

export default MermaidRenderer;
