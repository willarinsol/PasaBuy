document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".filterbtn");
  const entries = document.querySelectorAll(".order-entry");
  const emptyMessage = document.querySelector(".filtered-empty");
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  function filterOrders(filter) {
    let visibleCount = 0;
    entries.forEach(function (entry) {
      const isVisible =
        filter === "active"
          ? entry.dataset.status === "posted" ||
            entry.dataset.status === "claimed"
          : entry.dataset.status === filter;
      entry.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });
    emptyMessage.hidden = visibleCount !== 0;
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      buttons.forEach(function (item) {
        item.classList.toggle("active", item === button);
      });
      filterOrders(button.dataset.filter);
    });
  });

  document.querySelectorAll(".order-action").forEach(function (button) {
    button.addEventListener("click", function () {
      const action = button.dataset.action;
      const message =
        action === "cancel"
          ? "Cancel this order? This cannot be undone."
          : "Mark this order as completed?";
      if (!window.confirm(message)) return;

      fetch(`/order/${button.dataset.orderId}/${action}/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
      })
        .then(function (response) {
          if (!response.ok) throw new Error("Unable to update this order.");
          window.location.reload();
        })
        .catch(function (error) {
          window.alert(error.message);
        });
    });
  });

  filterOrders("active");
});
