let items = JSON.parse(localStorage.getItem("items")) || [];

function saveItems() {
    localStorage.setItem("items", JSON.stringify(items)); //All items are saved in local storage
}

function addItem() {
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const location = document.getElementById("location").value;
    const photo = document.getElementById("photo").files[0];

    if (!title || !description) {
        alert("Please fill everything");
        return;
    }

    const reader = new FileReader();
    reader.onload = function () {
        items.push({
            id: Date.now(),
            title: title,
            description: description,
            location: location,
            image: reader.result,
            claimed: false
        });

        saveItems();
        renderItems(items);

        // clear form
        document.getElementById("title").value = "";
        document.getElementById("description").value = "";
        document.getElementById("location").value = "";
        document.getElementById("photo").value = "";
    };
    reader.readAsDataURL(photo);
}

function claimItem(id) {
    items = items.filter(item => item.id !== id);
    saveItems();
    renderItems(items);
}


function renderItems(list) {
    const container = document.getElementById("items");
    container.innerHTML = "";

    list.forEach(item => {
        const card = document.createElement("div");
        card.className = "card" + (item.claimed ? " claimed" : "");

        card.innerHTML = `
            <img src="${item.image}">
            <h3>${item.title}</h3>
            <p>${item.description}</p>
            <p><strong>Location:</strong> ${item.location}</p>
        `;

        if (item.claimed) {
            const claimedText = document.createElement("p");
            claimedText.className = "claimed-text";
            claimedText.textContent = "✅ Claimed";
            card.appendChild(claimedText);
        } else {
            const btn = document.createElement("button");
            btn.textContent = "Claim";
            btn.onclick = () => claimItem(item.id);
            card.appendChild(btn);
        }

        container.appendChild(card);
    });
}

document.getElementById("search").addEventListener("input", e => {
    const text = e.target.value.toLowerCase();
    const filtered = items.filter(item =>
        item.title.toLowerCase().includes(text) ||
        item.description.toLowerCase().includes(text)
    );
    renderItems(filtered);
});


renderItems(items);