// Base URL for the Flask backend
const API_BASE_URL = "http://localhost:8000";

let allItems = [];

// Function to load items from the backend
async function loadItems() {
    try {
        const res = await fetch(`${API_BASE_URL}/items`);
        if (!res.ok) {
            throw new Error(`Failed to fetch items: ${res.status}`);
        }

        allItems = await res.json();
        console.log("Loaded items:", allItems);

        renderItems(allItems);
    } catch (error) {
        console.error("Error loading items:", error);
        alert("Failed to load items. Please try again later.");
    }
}

// Function to render items on the page
function renderItems(items) {
    const container = document.getElementById("items");

    if (items.length === 0) {
        container.innerHTML = "<p>No items found.</p>";
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="item">
            <h3>${item.type}</h3>
            <p>${item.description}</p>
            <button onclick="claimItem(${item.id})">Claim</button>
        </div>
    `).join("");
}

// Function to claim (delete) an item
async function claimItem(id) {
    const confirmed = confirm("Are you sure you want to claim this item?");

    if (!confirmed) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/items/${id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.error || "Failed to add item");
        }

        alert("Item claimed successfully!");
        loadItems();
    } catch (error) {
        console.error("Error adding item:", error);
        alert(error.message);
    }
}

// Function to add a new item
async function addItem() {
    const typeElement = document.getElementById("title");
    const descElement = document.getElementById("description");

    const type = typeElement.value.trim();
    const description = descElement.value.trim();

    if (!type || !description) {
        alert("Please fill out all fields!");
        return;
    } else if (description.length > 200) {
        alert("Description must be 200 characters or less!");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/items`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type, description })
        });

        if (!res.ok) {
            throw new Error(errorData.error || "Failed to add item");
        }

        // Clear input fields
        typeElement.value = "";
        descElement.value = "";

        alert("Item added successfully!");
        loadItems();
    } catch (error) {
        console.error("Error adding item:", error);
        alert("Failed to add item. Please try again.");
    }
}

// Initialize the app
loadItems();