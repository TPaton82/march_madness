function addSearchGamesListener() {
    const searchInput = document.getElementById("game-search");
    searchInput.addEventListener("input", function() {
        const filter = this.value.toLowerCase();
        const gameCards = document.querySelectorAll(".game-card-upcoming");

        gameCards.forEach(card => {
            const team1 = card.querySelector(".team:nth-child(1)").innerText.toLowerCase();
            const team2 = card.querySelector(".team:nth-child(3)").innerText.toLowerCase();

            if (team1.includes(filter) || team2.includes(filter)) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }
        });
    });
}

addSearchGamesListener();