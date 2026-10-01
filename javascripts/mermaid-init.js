document$.subscribe(() => {
  mermaid.initialize({
    startOnLoad: false
  });

  mermaid.run({
    nodes: document.querySelectorAll(".mermaid")
  });
});
