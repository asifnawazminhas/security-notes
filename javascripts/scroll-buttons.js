document.addEventListener("DOMContentLoaded", function () {
  const container = document.createElement("div");
  container.className = "scroll-controls";

  const topButton = document.createElement("button");
  topButton.className = "scroll-control";
  topButton.setAttribute("aria-label", "Scroll to top");
  topButton.setAttribute("title", "Scroll to top");
  topButton.innerHTML = "↑";

  const bottomButton = document.createElement("button");
  bottomButton.className = "scroll-control";
  bottomButton.setAttribute("aria-label", "Scroll to bottom");
  bottomButton.setAttribute("title", "Scroll to bottom");
  bottomButton.innerHTML = "↓";

  topButton.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });

  bottomButton.addEventListener("click", function () {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: "smooth"
    });
  });

  container.appendChild(topButton);
  container.appendChild(bottomButton);

  document.body.appendChild(container);

  function updateButtons() {
    const scrollTop =
      window.pageYOffset ||
      document.documentElement.scrollTop;

    const scrollHeight =
      document.documentElement.scrollHeight;

    const clientHeight =
      document.documentElement.clientHeight;

    topButton.classList.toggle("scroll-control-hidden", scrollTop < 300);

    bottomButton.classList.toggle(
      "scroll-control-hidden",
      scrollTop + clientHeight >= scrollHeight - 300
    );
  }

  window.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});
