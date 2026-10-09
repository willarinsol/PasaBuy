document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  document.querySelectorAll(".accept-btn").forEach(function (button) {
    button.addEventListener("click", function () {
      button.disabled = true;
      button.textContent = "Accepting...";

      fetch(`/order/${button.dataset.orderId}/accept/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
      })
        .then(function (response) {
          if (!response.ok)
            throw new Error("This order is no longer available.");
          button.textContent = "Accepted";
          window.setTimeout(function () {
            window.location.href = "/my-orders/";
          }, 400);
        })
        .catch(function (error) {
          button.disabled = false;
          button.textContent = "Claim Food Run";
          window.alert(error.message);
        });
    });
  });
});
