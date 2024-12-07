// Example cart functionality
const cartItems = JSON.parse(localStorage.getItem("cart")) || [];
const cartTotal = cartItems.reduce((total, item) => total + item.price, 0);

const cartContainer = document.getElementById("cart-items");
const totalElement = document.getElementById("cart-total");

// Render cart items
cartItems.forEach(item => {
  const cartItem = document.createElement("div");
  cartItem.className = "cart-item";
  cartItem.innerHTML = `<p>${item.name}</p><p>$${item.price.toFixed(2)}</p>`;
  cartContainer.appendChild(cartItem);
});

// Update total
totalElement.textContent = cartTotal.toFixed(2);

// Clear cart on checkout
document.getElementById("checkout-btn").addEventListener("click", () => {
  localStorage.removeItem("cart");
  alert("Checkout complete!");
  window.location.reload();
});
