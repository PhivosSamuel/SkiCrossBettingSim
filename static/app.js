$(document).ready(function() {
    var currentRound = 1;
    var totalRounds = 3;

    // Add this global variable at the top of your script
    let stallTimeouts = {};
    let animationInProgress = false;
    // Add this variable at the top of your script
    var pendingRoundUpdate = false;
    var pendingNewBalance;
    var pendingRaceResults;
    var finalRoundCompleted = false;

    const infoButton = document.getElementById("infoButton");
    const modal = document.getElementById("detailedInstructions");
    const closeBtn = document.getElementsByClassName("close")[0];


 

    function showModal() {
        modal.style.display = "block";
    }

    function hideModal() {
        modal.style.display = "none";
    }

    infoButton.addEventListener("mouseenter", showModal);
    infoButton.addEventListener("mouseleave", hideModal);
    infoButton.onclick = showModal;

    closeBtn.onclick = hideModal;

    window.onclick = function(event) {
        if (event.target == modal) {
            hideModal();
        }
    }


    const betInfoButton = document.getElementById("betInfoButton");
    const betModal = document.getElementById("betInstructions");
    const betCloseBtn = betModal.getElementsByClassName("close")[0];

    function showBetModal() {
        betModal.style.display = "block";
    }

    function hideBetModal() {
        betModal.style.display = "none";
    }

    betInfoButton.addEventListener("mouseenter", showBetModal);
    betInfoButton.addEventListener("mouseleave", hideBetModal);
    betInfoButton.onclick = showBetModal;

    betCloseBtn.onclick = hideBetModal;

    window.onclick = function(event) {
        if (event.target == modal) {
            hideModal();
        }
        if (event.target == betModal) {
            hideBetModal();
        }
    }


    $('#startButton').click(function() {
        
        // Hide the start button
        $(this).hide();
        $.post('/start_game', function(data) {
            // Update the odds table with data returned from the server
            for (var skier = 1; skier <= 8; skier++) {
                for (var place = 1; place <= 3; place++) {
                    
                    $('#odds' + skier + '_' + place).text(data[skier][place].toFixed(2));
                }
            }
            // New code to update skier stats
            var skierStats = "Skiers with their stats and odds:<br>";
            for (var skier = 1; skier <= 8; skier++) {
                skierStats += "Skier " + skier + " - Experience: " + data[skier].experience + ", Talent: " + data[skier].talent + ", Speed: " + data[skier].speed + "<br>";
            }
            $('#skierStats').html(skierStats);
            updateOddsForNewRound(1);
            updateStats();
        });
        
        
    });

    function updateOddsForNewRound(round_number) {
        $.get('/get_new_odds', {round_number: round_number}, function(data) {
            for (var skier = 1; skier <= 8; skier++) {
                for (var place = 1; place <= 3; place++) {
                    
                    $('#odds' + skier + '_' + place).text(data[skier][place].toFixed(2));
                }
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.error("Failed to fetch new odds: " + textStatus + ", " + errorThrown);
        });

        // New AJAX call to get skier stats
        $.get('/get_skier_stats', {round_number: round_number}, function(data) {
            var skierStats = "Skiers with their stats and odds:<br>";
            for (var skier = 1; skier <= 8; skier++) {
                skierStats += "Skier " + skier + " - Experience: " + data[skier].experience + ", Talent: " + data[skier].talent + ", Speed: " + data[skier].speed + "<br>";
            }
            $('#skierStats').html(skierStats);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.error("Failed to fetch skier stats: " + textStatus + ", " + errorThrown);
        });
    }

    $('#betButton').off('click').on('click', function() {
        console.log(`Attempting to place bet for round ${currentRound}`);
        if (currentRound > totalRounds) {
            const finalBalance = parseFloat($('#balance').text());
            updateMedals(finalBalance);
            return;
        }

        const bets = [];
        let totalBet = 0;
        const balance = parseFloat($('#balance').text());

        // Validate bets
        for (let i = 1; i <= 8; i++) {
            const bet = parseFloat($('#bet' + i).val());
            if (isNaN(bet) || bet < 0) {
                alert("Please enter a valid positive number for all bets.");
                return;
            }
            bets.push({skier_id: i, bet_amount: bet});
            totalBet += bet;
        }

        if (totalBet > balance) {
            alert("Your total bet exceeds your available balance.");
            return;
        }

        // Send AJAX request
        $(this).prop('disabled', true);
        $.ajax({
            url: '/update_balance',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({bets: bets, balance: balance}),
            success: handleRaceResults,
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Request failed:", textStatus, errorThrown);
                $('#betButton').prop('disabled', false);
            }
        });
    });

    // Modify the handleRaceResults function
    function handleRaceResults(data) {
        const isFinalRound = currentRound === totalRounds;
        
        animateSkiers(data.events, data.race_results, () => {
            // This callback will be called when all animations are complete
            updateRaceResults();
            resetSkiersToStart(isFinalRound);
        });
        
        pendingRaceResults = {
            results: generateRaceResults(data, currentRound),
            round: currentRound
        };
        pendingNewBalance = parseFloat(data.new_balance).toFixed(2);
        
        if (currentRound < totalRounds) {
            currentRound++;
            pendingRoundUpdate = true;
            console.log(`Round incremented to ${currentRound}, waiting for visual update`);
        } else {
            finalRoundCompleted = true; // Set the flag when the final round is completed
            console.log("Game over");
        }
        
        console.log(`Race results handled for round ${currentRound - 1}`);
    }

    // Modify the generateRaceResults function
    function generateRaceResults(data, roundNumber) {
        let results = `<div class='roundResult'><h2>Round ${roundNumber} Results</h2>Race Rankings:<br>`;
        
        if (data.finish_order && Array.isArray(data.finish_order)) {
            data.finish_order.forEach((skier_number, index) => {
                const result = data.race_results[skier_number];
                const suffix = ['st', 'nd', 'rd'][index] || 'th';
                results += `${index + 1}${suffix} place: Skier ${skier_number} - Time: ${result === 'DNF' ? result : result.toFixed(2) + " seconds"}<br>`;
            });
        } else {
            console.error('Invalid finish_order data:', data.finish_order);
            results += 'Error: Unable to display race rankings.<br>';
        }
        
        results += "<br>Skier Payouts:<br>";
        for (let i = 1; i <= 8; i++) {
            results += `Skier ${i}: $${data.payouts[i].toFixed(2)}<br>`;
        }
        
        results += "<br>Skiers with their stats and odds:<br>";
        for (const [skier_number, skier] of Object.entries(data.skier_stats)) {
            results += `Skier ${skier_number} - Experience: ${skier.experience}, Talent: ${skier.talent}, Speed: ${skier.speed}<br>`;
        }
        
        results += `Total Winnings for Round ${roundNumber}: $${data.round_winnings.toFixed(2)}</div>`;
        return results;
    }

    function updateRoundResults(raceResults, roundNumber) {
        const targetDiv = $(`#round${roundNumber}Results`);
        targetDiv.html(raceResults);
    }

    function resetBets() {
        for (let i = 1; i <= 8; i++) {
            $(`#bet${i}`).val(0);
        }
    }

    function calculateYPosition(bump_number) {
        const positions = [64, 190, 311.5, 433.5, 554, 676.5, 797.5, 922.5]; // Adjusted positions based on scaled image
        return positions[bump_number]; // Adjust index to match bump_number correctly
    }

    function animateSkiers(events, raceResults, callback) {
        $('#betButton').prop('disabled', true);
        console.log("Received events:", events);
        let skierAnimations = {};
        let animationsCompleted = 0;
        const totalSkiers = Object.keys(raceResults).length;
    
        $('.skier').stop(true, false);
        animationInProgress = true;
        
        events.forEach(event => {
            const skierDiv = document.getElementById('skier' + event.skier_number);
            let newY = calculateYPosition(event.bump_number);
            
            if (!skierAnimations[event.skier_number]) {
                skierAnimations[event.skier_number] = [];
            }
            skierAnimations[event.skier_number].push({
                div: skierDiv,
                y: newY,
                time: event.time * 1000,
                stall_time: event.stall_time * 1000,
                event: event
            });
        });
    
        Object.entries(skierAnimations).forEach(([skierNumber, animations]) => {
            const totalTime = raceResults[skierNumber] === 'DNF' ? 
                animations.reduce((sum, anim) => sum + anim.time + anim.stall_time, 0) : 
                raceResults[skierNumber] * 1000;
            animateSkierSequence(animations, 0, totalTime, () => {
                animationsCompleted++;
                if (animationsCompleted === totalSkiers) {
                    $('#betButton').prop('disabled', false);
                    callback();
                }
            });
        });
    }

    function animateSkierSequence(animations, index, totalTime, callback) {
        if (index >= animations.length || !animationInProgress) {
            callback();
            return;
        }
    
        const animation = animations[index];
        const { div, y, time, stall_time, event } = animation;
    
        if ($(div).hasClass('fallen')) {
            console.log(`Skier ${event.skier_number} has fallen and cannot move further`);
            callback();
            return;
        }
    
        console.log(`Animating Skier ${event.skier_number} to bump ${event.bump_number}, time: ${time}ms, stall time: ${stall_time}ms, status: ${event.status}`);
    
        $(div).animate({ top: y + 'px' }, {
            duration: time,
            easing: 'linear',
            queue: false,
            complete: function() {
                if (!animationInProgress) {
                    callback();
                    return;
                }
                console.log(`Animation completed for Skier ${event.skier_number} at Bump ${event.bump_number}`);
                handleSkierStatus(event, this, stall_time, () => {
                    if (animationInProgress) {
                        animateSkierSequence(animations, index + 1, totalTime, callback);
                    } else {
                        callback();
                    }
                });
            }
        });
    }

    function handleSkierStatus(event, skierDiv, stall_time, callback) {
        if (!animationInProgress) {
            callback();
            return;
        }
        if (event.bump_number === 7) {
            console.log(`Skier ${event.skier_number} reached the finish line`);
            checkRaceEnd();
            callback();
        } else if (event.status === 'Fell') {
            $(skierDiv).addClass('fallen').stop(true, true);
            console.log(`Skier ${event.skier_number} has fallen at bump ${event.bump_number}`);
            checkRaceEnd();
        } else if (event.status === 'Stalled') {
            $(skierDiv).addClass('confused');
            var rotationDirection = Math.random() < 0.5 ? -20 : 20;
            $(skierDiv).css({
                'transform-origin': '50% 100%',
                'transform': `rotate(${rotationDirection}deg)`
            });
            
            stallTimeouts[event.skier_number] = setTimeout(() => {
                if (animationInProgress) {
                    $(skierDiv).removeClass('confused');
                    $(skierDiv).css('transform', '');
                    console.log(`Stalled Skier ${event.skier_number} resumed movement at Bump ${event.bump_number}`);
                    callback();
                }
            }, stall_time);
        } else {
            checkRaceEnd();
            callback();
        }
    }

    function checkRaceEnd() {
        const totalSkiers = 8;
    
        let finishedSkiers = $('.skier').filter(function() {
            return $(this).css('top') === calculateYPosition(7) + 'px';
        }).length;
    
        let fallenSkiers = $('.fallen').length;
    
        if (finishedSkiers >= 3 || finishedSkiers + fallenSkiers === totalSkiers) {
            console.log("Race ended");
            
            // Instead of immediately stopping animations and resetting,
            // set a flag and use a timeout to allow all animations to complete
            animationInProgress = false;
            
            setTimeout(() => {
                $('.skier').stop(true, true);
                
                Object.values(stallTimeouts).forEach(clearTimeout);
                stallTimeouts = {};
        
                updateRaceResults();
                resetSkiersToStart(currentRound === totalRounds);
            }, 1000); // Adjust this delay as needed
        }
    }

    function updateRaceResults() {
        if (pendingRaceResults) {
            updateRoundResults(pendingRaceResults.results, pendingRaceResults.round);
            pendingRaceResults = null;
        }
        if (pendingNewBalance) {
            $('#balance').text(pendingNewBalance);
            pendingNewBalance = null;
        }
    }

    // Modify the resetSkiersToStart function
    function resetSkiersToStart(isFinalRound) {
        // Stop all ongoing animations immediately
        $('.skier').stop(true, true);
    
        // Clear all stall timeouts
        Object.values(stallTimeouts).forEach(clearTimeout);
        stallTimeouts = {};
    
        // Reset skier positions and remove classes
        var skiers = document.getElementsByClassName('skier');
        var slopeWidth = document.getElementById('skiSlope').offsetWidth;
        var skierWidth = skiers[0].offsetWidth;
    
        for (var i = 0; i < skiers.length; i++) {
            $(skiers[i]).css({
                'left': ((i / (skiers.length - 1)) * (slopeWidth - skierWidth)) + 'px',
                'top': '0px',
                'transform': ''
            }).removeClass('fallen confused');
        }
    
        console.log("Skiers reset to start positions.");
    
        // Update round and odds if necessary
        if (pendingRoundUpdate) {
            console.log(`Updating visual round to ${currentRound}`);
            $('#currentRound').text(currentRound);
            pendingRoundUpdate = false;
            updateOddsForNewRound(currentRound);
        }
    
        // Handle betting button state
        if (isFinalRound && finalRoundCompleted) {
            updateMedals(parseFloat($('#balance').text()));
            $('#betButton').prop('disabled', true);
            console.log("Final round completed. Betting disabled.");
        } else if (currentRound <= totalRounds) {
            $('#betButton').prop('disabled', false);
            console.log("Betting enabled for round: " + currentRound);
        } else {
            $('#betButton').prop('disabled', true);
            console.log("Game over. Betting disabled.");
        }
    
        resetBets();
    
        // Force a repaint to ensure all visual changes are applied immediately
        $('#skiSlope')[0].offsetHeight;
    }

    // Add the updateMedals function
    function updateMedals(finalBalance) {
        $('.medalBox').removeClass('active'); // Reset all medals
        
        if (finalBalance >= 200) {
            $('#goldMedal').addClass('active');
        } else if (finalBalance >= 150) {
            $('#silverMedal').addClass('active');
        } else if (finalBalance >= 100) {
            $('#bronzeMedal').addClass('active');
        }
        updateFinalMessage(finalBalance);
        $('#medalBoxesContainer').show(); // Make sure this is visible at the end
        showResetButton(); // Show the reset button
    }

    // Move the window.onload function here
    $(window).on('load', function() {
        const skiers = document.getElementsByClassName('skier');
        const slopeWidth = document.getElementById('skiSlope').offsetWidth;
        const skierWidth = skiers[0].offsetWidth;
        
        for (let i = 0; i < skiers.length; i++) {
            skiers[i].style.left = `${(i / (skiers.length - 1)) * (slopeWidth - skierWidth)}px`;
        }
    });

    // Add the updateStats function and related calculations
    function updateStats() {
        const exp = parseInt($('#expSlider').val());
        const talent = parseInt($('#talentSlider').val());
        const speed = parseInt($('#speedSlider').val());

        $('#expOutput').text(exp);
        $('#talentOutput').text(talent);
        $('#speedOutput').text(speed);

        const fallChance = calculateFallChance(exp);
        const stallChance = calculateStallChance(talent);
        const raceTime = calculateRaceTime(speed);

        $('#fallChanceOutput').text(`${fallChance}%`);
        $('#stallChanceOutput').text(`${stallChance}%`);
        $('#raceTimeOutput').text(`${raceTime} seconds ± ${calculateVariabilitySpeed(speed)}`);
    }

    function calculateFallChance(experience) {
        const singleBumpProbability = Math.max(0, 12 - experience) / 100;
        return ((1 - Math.pow(1 - singleBumpProbability, 6)) * 100).toFixed(2);
    }

    function calculateStallChance(talent) {
        const singleBumpProbability = Math.max(0, 25 - (talent * 2)) / 100;
        return (singleBumpProbability * 100).toFixed(2);
    }

    function calculateRaceTime(speed) {
        const singleBumpTime = Math.max(2.6 - speed * 0.2, 0);
        return (6 * singleBumpTime).toFixed(2);
    }

    function calculateVariabilitySpeed(speed) {
        return (6 * 0.5).toFixed(2);
    }

    // Attach the updateStats function to the sliders
    $('#expSlider, #talentSlider, #speedSlider').on('input', updateStats);

    // Initial call to set up the stats
    updateStats();

    function calculatePercentile(balance) {
        const strategies = [51.01, 142.52, 9.61, 50.72, 89.24, 186.86, 2.71, 51.38, 70.03, 33.80, 51.61, 75.10, 52.81, 96.59, 97.78, 49.34, 49.58, 52.91, 72.77, 120.16, 49.47, 86.47, 118.08];
        const totalStrategies = strategies.length;
        const strategiesBelow = strategies.filter(s => s < balance).length;
        return Math.round((strategiesBelow / totalStrategies) * 100);
    }
    
    function updateFinalMessage(balance) {
        const percentile = calculatePercentile(balance);
        const message = `With an end balance of $${balance}, you performed better than ${percentile}% of players.`;
        $('#finalMessage').text(message);
    }


    function showResetButton() {
        $('#startButton').hide();
        $('#resetButton').show();
    }

    function resetGame() {
        location.reload(); // This will refresh the page, effectively resetting the game
    }

    $('#resetButton').click(resetGame);


});


