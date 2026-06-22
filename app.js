document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const productInput = document.getElementById('productInput');
    const loadingDiv = document.getElementById('loading');
    const resultsDashboard = document.getElementById('results-dashboard');

    // Quick Analyzer Elements
    const analyzeReviewBtn = document.getElementById('analyzeReviewBtn');
    const reviewInput = document.getElementById('reviewInput');
    const reviewResult = document.getElementById('reviewResult');

    analyzeBtn.addEventListener('click', analyzeProduct);
    analyzeReviewBtn.addEventListener('click', analyzeSingleReview);

    // New Feature Elements
    const bookingForm = document.getElementById('bookingForm');
    const diaryForm = document.getElementById('diaryForm');

    if (bookingForm) bookingForm.addEventListener('submit', handleBooking);
    if (diaryForm) diaryForm.addEventListener('submit', handleDiaryGeneration);

    productInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeProduct();
    });

    async function analyzeSingleReview() {
        const reviewText = reviewInput.value.trim();
        if (!reviewText) {
            alert('Please enter a review to analyze.');
            return;
        }

        analyzeReviewBtn.disabled = true;
        reviewResult.classList.add('d-none');

        try {
            const response = await fetch('/api/analyze_single_review', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ review_text: reviewText })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Analysis failed');
            }

            const data = await response.json();

            // Display Result
            reviewResult.classList.remove('d-none', 'bg-success-subtle', 'text-success', 'bg-danger-subtle', 'text-danger', 'bg-secondary-subtle', 'text-secondary');

            let resultText = `Predicted Sentiment: ${data.sentiment.toUpperCase()}`;
            if (data.sentiment === 'Positive') {
                reviewResult.classList.add('bg-success-subtle', 'text-success');
            } else if (data.sentiment === 'Negative') {
                reviewResult.classList.add('bg-danger-subtle', 'text-danger');
            } else {
                reviewResult.classList.add('bg-secondary-subtle', 'text-secondary');
            }

            reviewResult.textContent = resultText;

        } catch (error) {
            console.error('Error:', error);
            if (error.message === 'Invalid character used') {
                reviewResult.classList.remove('d-none', 'bg-success-subtle', 'text-success', 'bg-secondary-subtle', 'text-secondary');
                reviewResult.classList.add('bg-danger-subtle', 'text-danger');
                reviewResult.textContent = 'Invalid character used';
            } else {
                alert('An error occurred.');
            }
        } finally {
            analyzeReviewBtn.disabled = false;
        }
    }

    async function analyzeProduct() {
        const productName = productInput.value.trim();
        if (!productName) {
            alert('Please enter a product name.');
            return;
        }

        // UI State: Loading
        loadingDiv.classList.remove('d-none');
        resultsDashboard.classList.add('d-none');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze_product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_name: productName })
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            updateDashboard(data);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the product. Please try again.');
        } finally {
            // UI State: Ready
            loadingDiv.classList.add('d-none');
            analyzeBtn.disabled = false;
        }
    }

    function updateDashboard(data) {
        // 1. Overall Sentiment (Pie Chart)
        const sentiment = data.overall_sentiment;
        renderCharts(sentiment, data.key_aspects_sentiment);

        // 2. AI Summary
        document.getElementById('ai-summary-text').textContent = data.ai_summary;

        // 3. Key Aspects (List)
        const aspectsList = document.getElementById('aspects-list');
        aspectsList.innerHTML = '';
        data.key_aspects_sentiment.forEach(item => {
            const li = document.createElement('li');
            li.className = 'aspect-item';

            // Determine color based on sentiment text
            let badgeClass = 'bg-secondary';
            if (item.sentiment.includes('Positive')) badgeClass = 'bg-success';
            else if (item.sentiment.includes('Negative')) badgeClass = 'bg-danger';

            li.innerHTML = `
                <span class="fw-semibold">${item.aspect}</span>
                <span class="badge ${badgeClass} rounded-pill">${item.sentiment}</span>
            `;
            aspectsList.appendChild(li);
        });

        // 4. Reviews
        const reviewsContainer = document.getElementById('reviews-container');
        reviewsContainer.innerHTML = '';
        data.sample_reviews.forEach(review => {
            const div = document.createElement('div');
            div.className = `review-card ${review.sentiment.toLowerCase()}`;
            div.innerHTML = `
                <p class="mb-1 fst-italic">"${review.text}"</p>
                <small class="fw-bold text-uppercase" style="font-size: 0.7rem;">${review.sentiment}</small>
            `;
            reviewsContainer.appendChild(div);
        });

        // 5. Recommendations
        const recContainer = document.getElementById('recommendations-container');
        recContainer.innerHTML = '';
        data.recommendations.forEach(rec => {
            const col = document.createElement('div');
            col.className = 'col-md-4 mb-3';
            col.innerHTML = `
                <div class="recommendation-card shadow-sm text-center">
                    <img src="${rec.image_url}" alt="${rec.name}" class="img-fluid rounded mb-3" style="width: 150px; height: 150px; object-fit: cover;">
                    <h6 class="fw-bold text-primary-custom mb-2">${rec.name}</h6>
                    <p class="small text-muted mb-0">${rec.reason}</p>
                    <a href="${rec.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">View Product</a>
                </div>
            `;
            recContainer.appendChild(col);
        });
        resultsDashboard.classList.remove('d-none');

        // Scroll to results
        resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    let sentimentPieChart = null;
    let aspectsBarChart = null;

    function renderCharts(sentiment, aspects) {
        // Destroy existing charts if they exist
        if (sentimentPieChart) sentimentPieChart.destroy();
        if (aspectsBarChart) aspectsBarChart.destroy();

        // 1. Pie Chart: Overall Sentiment
        const ctxPie = document.getElementById('sentimentPieChart').getContext('2d');
        sentimentPieChart = new Chart(ctxPie, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral', 'Mixed'],
                datasets: [{
                    data: [sentiment.Positive, sentiment.Negative, sentiment.Neutral, sentiment.Mixed],
                    backgroundColor: [
                        '#a8e6cf', // Pastel Green
                        '#ffaaa5', // Pastel Red
                        '#dcedc1', // Pastel Yellow/Green
                        '#ffd3b6'  // Pastel Orange
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // 2. Bar Chart: Key Aspects
        // Parse aspect sentiment strings "Positive (85%)" -> 85
        const aspectLabels = aspects.map(a => a.aspect);
        const aspectScores = aspects.map(a => {
            const match = a.sentiment.match(/\((\d+)%\)/);
            return match ? parseInt(match[1]) : 0;
        });
        const aspectColors = aspects.map(a => {
            if (a.sentiment.includes('Positive')) return '#a8e6cf';
            if (a.sentiment.includes('Negative')) return '#ffaaa5';
            return '#dcedc1';
        });

        const ctxBar = document.getElementById('aspectsBarChart').getContext('2d');
        aspectsBarChart = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: aspectLabels,
                datasets: [{
                    label: 'Sentiment Score (%)',
                    data: aspectScores,
                    backgroundColor: aspectColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    async function handleBooking(e) {
        e.preventDefault();
        const name = document.getElementById('bookingName').value;
        const date = document.getElementById('bookingDate').value;
        const time = document.getElementById('bookingTime').value;
        const reason = document.getElementById('bookingReason').value;

        try {
            const response = await fetch('/api/book_appointment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, date, time, reason })
            });
            const data = await response.json();
            if (data.success) {
                alert(data.message);
                const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
                modal.hide();
                bookingForm.reset();
            }
        } catch (error) {
            console.error('Booking Error:', error);
            alert('Failed to book appointment.');
        }
    }

    async function handleDiaryGeneration(e) {
        e.preventDefault();
        const skinType = document.getElementById('skinType').value;
        const concerns = document.getElementById('skinConcerns').value;

        try {
            const response = await fetch('/api/generate_diary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skin_type: skinType, concerns })
            });
            const data = await response.json();

            // Render Routine
            const morningList = document.getElementById('morningRoutineList');
            const eveningList = document.getElementById('eveningRoutineList');
            morningList.innerHTML = '';
            eveningList.innerHTML = '';

            data.routine.Morning.forEach(step => {
                const li = document.createElement('li');
                li.className = 'mb-1';
                li.innerHTML = `<i class="bi bi-check2-circle text-success me-2"></i>${step}`;
                morningList.appendChild(li);
            });

            data.routine.Evening.forEach(step => {
                const li = document.createElement('li');
                li.className = 'mb-1';
                li.innerHTML = `<i class="bi bi-check2-circle text-primary me-2"></i>${step}`;
                eveningList.appendChild(li);
            });

            document.getElementById('diaryResult').classList.remove('d-none');

        } catch (error) {
            console.error('Diary Error:', error);
            alert('Failed to generate diary.');
        }
    }

});
