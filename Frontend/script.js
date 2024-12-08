// Product Data
const products = [
  { id: 1, name: "Laptop", price: 899.99, image: "https://via.placeholder.com/150" },
  { id: 2, name: "Smartphone", price: 599.99, image: "https://via.placeholder.com/150" },
  { id: 3, name: "Headphones", price: 99.99, image: "https://via.placeholder.com/150" },
];

// Initialize Cart
let cart = [];

// Render Products
function renderProducts() {
  const productList = document.querySelector('.product-list');
  productList.innerHTML = "";
  products.forEach(product => {
    const productCard = document.createElement('div');
    productCard.classList.add('product');
    productCard.innerHTML = `
      <img src="${product.image}" alt="${product.name}">
      <h3>${product.name}</h3>
      <p>$${product.price.toFixed(2)}</p>
      <button onclick="addToCart(${product.id})">Add to Cart</button>
    `;
    productList.appendChild(productCard);
  });
}

// Add to Cart
function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  const cartItem = cart.find(item => item.id === productId);

  if (cartItem) {
    cartItem.quantity++;
  } else {
    cart.push({ ...product, quantity: 1 });
  }
  renderCart();
}

// Render Cart
function renderCart() {
  const cartItemsContainer = document.getElementById('cart-items');
  const cartTotal = document.getElementById('cart-total');
  cartItemsContainer.innerHTML = "";

  let total = 0;
  cart.forEach(item => {
    total += item.price * item.quantity;

    const cartItem = document.createElement('div');
    cartItem.classList.add('cart-item');
    cartItem.innerHTML = `
      <p>${item.name} - $${item.price.toFixed(2)} x ${item.quantity}</p>
      <button onclick="removeFromCart(${item.id})">Remove</button>
    `;
    cartItemsContainer.appendChild(cartItem);
  });

  cartTotal.textContent = total.toFixed(2);
}

// Remove from Cart
function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  renderCart();
}

// Initialize Page
renderProducts();
renderCart();
