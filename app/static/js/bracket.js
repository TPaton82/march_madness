
function getFinalFourRound(round) {
    const region = round.parentElement;
    const area = region.className.split('-')[1]
    const finalFourRound = document.querySelector(`#final-four-${area}`)
    return finalFourRound;
}

function getNextRound(currentRound) {
    // Find the region
    const region = currentRound.parentElement;
    
    // If we're at the winner round, no next round
    if (currentRound.id === 'winner') {
        return null;
    }

    // If we're at the championship, next round is the winner
    if (currentRound.id === 'championship-game') {
        return currentRound.querySelector('#winner');
    }

    // If we're in the final four, next round is the championship
    if (region.className.includes('final-four')) {
        return document.querySelector('#championship-game');
    }

    // Otherwise we're in the areas, determine the next round
    const rounds = Array.from(region.querySelectorAll('.round'));
    nextRoundIndex = rounds.indexOf(currentRound);
    
    // For right side, rounds are in reverse order
    if (region.className.includes('right')) {
        nextRoundIndex -= 1;
    }
    else {
        nextRoundIndex += 1;
    }

    const nextRound = rounds[nextRoundIndex]

    // No next round we're at the final reound in the area so move to final four
    if (!nextRound) {
        return getFinalFourRound(currentRound);
    }

    return nextRound;
}

function getNextTeam(round, nextRound, currentGameIndex) {
    
    // Ensure we move to final four correctly
    if (round.id.includes('west') && nextRound.id.includes('final-four')) {
        currentGameIndex += 1
    }

    // Ensure we move to championship
    if (round.id.includes('final-four-right') && nextRound.id.includes('championship')) {
        currentGameIndex += 1
    }

    // If next round is the winner then return that now
    if (nextRound.id == 'winner') {
        return nextRound.querySelector('.team-row')
    }

    // Given the next round and current game index, find the correct game in the next round
    const nextGames = nextRound.querySelectorAll('.game-card, .championship-card');

    // Calculate which slot this team goes into in next round
    // Example: 2 games in current round → 1 game in next round
    const nextGameIndex = Math.floor(currentGameIndex / 2);

    const nextGame = nextGames[nextGameIndex];

    if (nextGame) {
        const nextTeam = nextGame.querySelectorAll('.team-row')[currentGameIndex % 2];
        return nextTeam;
    }

}

function replaceTeam(nextTeam, team) {
    const team_clone = team.cloneNode(true);
    team_clone.querySelector('.circle').classList.remove('active');
    nextTeam.replaceWith(team_clone);
}

function clearFutureSelections(round, team) {
    const teamName = team.querySelector('.team-name').textContent.trim()
    
    // Iterate through all subsequent rounds 
    let nextRound = getNextRound(round);

    while (nextRound) {
        // For each game-card in the round
        nextRound.querySelectorAll('.team-row').forEach(team => {
            if (team.querySelector('.team-name').textContent.trim() === teamName) {
                clearTeamRow(team);
            }
        });

        // Move to the next round
        nextRound = getNextRound(nextRound);
    }
}

function clearTeamRow(teamRow) {
    // Clear team name
    const nameDiv = teamRow.querySelector('.team-name');
    if (nameDiv) nameDiv.textContent = "";

    const seedDiv = teamRow.querySelector('.team-seed');
    if (seedDiv) seedDiv.textContent = "";

    // Deactivate circle
    teamRow.querySelectorAll('.circle').forEach(circle => circle.classList.remove('active'));

    // Remove team logo image
    const img = teamRow.querySelector('img.team-logo');
    if (img) img.remove();
}

function advanceTeam(game, team) {
    const round = game.parentElement
    const nextRound = getNextRound(round);

    if (nextRound) {
        gameIndex = Array.from(round.querySelectorAll('.game-card')).indexOf(game);
        const nextTeam = getNextTeam(round, nextRound, gameIndex);
        clearFutureSelections(nextRound, nextTeam);
        replaceTeam(nextTeam, team);
    }
};

function amendGameWinner(game, team) {
    const circles = game.querySelectorAll('.circle');

    // Remove 'active' class from all circles in this card
    circles.forEach(c => c.classList.remove('active'));

    // Add 'active' to the clicked circle
    if (team.textContent.trim() != "") {
        const circle = team.querySelector('.circle');
        circle.classList.add('active');
    }
};

function addGameCardListeners() {
    const games = document.querySelectorAll('.game-card, .championship-card');
    games.forEach(game => {
        game.addEventListener('click', (e) => {
            selected_team = e.target.closest(".team-row");
            amendGameWinner(game, selected_team)
            advanceTeam(game, selected_team)
        });
    })
}

function AddSubmitPicksButtonListner() {
    const submit_picks_button = document.getElementById("submitPicksBtn");
    
    submit_picks_button.addEventListener("click", () => {
        const gameStates = document.querySelectorAll(".game-card, .championship-card, .winner-card");

        let userPicks = [];
        let winnerPick = null;
        
        gameStates.forEach(game => {
            teams = game.querySelectorAll(".team-row");
            teams.forEach(team => {
                
                // We also need to get the state of the winner which doesn't have a circle.
                // Do this first to avoid searching for circle which doesn't exist
                if (game.id == "winner") {
                    const winnerName = team.querySelector(".team-name").textContent
                    if (winnerName != "") {
                        winnerPick = winnerName
                    }
                }
                else {
                    const circle = team.querySelector(".circle");
                    if (circle.classList.contains("active")) {
                        userPicks.push({
                            game_id: game.dataset.gameId,
                            team_id: team.dataset.teamId,
                        });
                    }
                }
            });
        });

        const finalScore = document.querySelector("#final-score").textContent

        fetch("/submit-picks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ user_picks: userPicks, winner_pick: winnerPick, final_score: finalScore })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage("save-message", data.message);
            } else {
                showMessage("save-message", data.get(message, "Error saving picks"), 5000);
            }
        });
    });
}


function showMessage(elementId, text, duration = 2000) {
    const msg = document.getElementById(elementId);

    msg.textContent = text;
    msg.classList.remove("hidden");

    // Clear any pending timers so messages behave consistently
    if (msg.hideTimer) {
        clearTimeout(msg.hideTimer);
    }

    msg.hideTimer = setTimeout(() => {
        msg.classList.add("hidden");
    }, duration);
}

addGameCardListeners();
AddSubmitPicksButtonListner();