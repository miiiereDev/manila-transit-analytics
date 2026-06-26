document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs & Visualization Explorer Logic ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    const displayPlot = document.getElementById('display-plot');
    const plotDesc = document.getElementById('plot-description');
    const plotContainer = document.querySelector('.plot-container');

    const plotDetails = {
        overall: {
            src: '../../output/figures/average_wait_time_by_line.png',
            desc: 'Scheduled vs. Actual Wait Time by Transit Line. Highlights the average absolute delays, demonstrating that the EDSA Carousel has the largest service gap.'
        },
        peak: {
            src: '../../output/figures/peak_vs_offpeak_comparison.png',
            desc: 'Average Commuter Wait Time: Peak vs. Off-Peak Periods. Shows that while rail systems are faster overall, they experience a significantly higher percentage increase in delays during rush hours compared to the busway.'
        },
        weather: {
            src: '../../output/figures/weather_impact_by_line.png',
            desc: 'Average Wait Time by Weather Condition. Highlights the weather-resiliency of train transit systems compared to the 88% delay surge experienced by the EDSA Carousel busway under heavy rainfall.'
        },
        stations: {
            src: '../../output/figures/top_5_worst_stations.png',
            desc: 'Top 5 Stations with the Highest Average Delay. Identifies the primary spatial bottlenecks across the network (standardized to uppercase to resolve casing duplications).'
        }
    };

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');

            const target = btn.getAttribute('data-target');
            const details = plotDetails[target];

            if (details) {
                // Add fade animation
                plotContainer.classList.add('changing');
                
                setTimeout(() => {
                    displayPlot.src = details.src;
                    plotDesc.textContent = details.desc;
                    plotContainer.classList.remove('changing');
                }, 200);
            }
        });
    });

    // --- CSV Ingestion & Stats Calculation ---
    // Fetch the cleaned dataset to display dynamic trip count
    const csvPath = '../../data/2_cleaned/manila_transit_cleaned.csv';
    const tripsStatElement = document.getElementById('stat-trips');

    function parseCSV(text) {
        // Splits by newline and filters empty lines
        const lines = text.split('\n').filter(line => line.trim() !== '');
        if (lines.length < 2) return [];
        return lines.slice(1); // Return data rows
    }

    fetch(csvPath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load cleaned transit data');
            }
            return response.text();
        })
        .then(data => {
            const rows = parseCSV(data);
            if (rows.length > 0) {
                // Animate counting up for premium feel
                animateValue(tripsStatElement, 0, rows.length, 1200);
            } else {
                tripsStatElement.textContent = '980';
            }
        })
        .catch(error => {
            console.error('Error fetching/parsing CSV:', error);
            // Fallback default value if file isn't fetched directly (e.g. cross-origin issues)
            tripsStatElement.textContent = '980';
        });

    // Premium count-up animation
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
