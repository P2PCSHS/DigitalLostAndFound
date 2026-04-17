
let allItems = [];


async function loadItems() {
    try {
        const res = await fetch("/items");
        allItems = await res.json();

        console.log("Loaded items:", allItems);

        renderItems(allItems);
    } catch (error) {
        console.error("Error loading items:", error);
    }
}



function renderItems(items) {
    const container = document.getElementById("items");

    container.innerHTML = items.map(item => `
        <div class="item">
            <h3>${item.type}</h3>
            <p>${item.description}</p>
            <button onclick="claimItem(${item.id})">Claim</button>
        </div>
    `).join("");
}

async function claimItem(id) {
    const confirmed = confirm("Are you sure you want to claim this item?");

    if (!confirmed) {
        return;
    }

    await fetch(`/items/${id}`, {
        method: "DELETE"
    });

    loadItems();
}

async function addItem() {
    const typeElement = document.getElementById("title");
    const descElement = document.getElementById("description");

    const type = typeElement.value;
    const description = descElement.value;

    if (!type || !description) {
        alert("Please fill out all fields!");
        return;
    } else if (description.length > 200) {
        alert("Description must be 200 characters or less!");
        return;
    }

    try {
        await fetch("/items", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ type, description })
        });

        // clear inputs
        typeElement.value = "";
        descElement.value = "";

        loadItems();

    } catch (error) {
        console.error("Error adding item:", error);
    }
}



function setupSearch() {
    const searchInput = document.getElementById("search");

    searchInput.addEventListener("change", (e) => {
        const query = e.target.value.toLowerCase();

        const filtered = allItems.filter(item =>
            item.type.toLowerCase().includes(query) ||
            item.description.toLowerCase().includes(query)
        );

        renderItems(filtered);
    });
}

loadItems();
setupSearch();