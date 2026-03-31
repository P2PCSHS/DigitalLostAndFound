
async function loadItems() {
    const res = await fetch("/items");
    const data = await res.json();

    console.log("Items from backend:", data);

    const container = document.getElementById("items");

    container.innerHTML = data.map(item => `
        <div class="item">
            <h3>${item.type}</h3>
            <p>${item.description}</p>
        </div>
    `).join("");
}


async function addItem() {
    const typeElement = document.getElementById("title");
    const descElement = document.getElementById("description");

    const type = typeElement.value;
    const description = descElement.value;

    if (!type || !description) {
        alert("Please fill out both fields!");
        return;
    }

    await fetch("/items", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            type,
            description
        })
    });

    // clear input after submit
    descElement.value = "";
    typeElement.value = "";

    loadItems();
}


// run on page load
loadItems();