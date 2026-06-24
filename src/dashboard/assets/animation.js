// =====================================
// MarketLens KPI Counter Animation
// =====================================

function animateCounter(element, target, duration = 800, suffix = '') {
    const startTime = performance.now();
    const isFloat = target % 1 !== 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);

        const value = eased * target;

        element.textContent = isFloat
            ? value.toFixed(1) + suffix
            : Math.floor(value).toLocaleString() + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function runCounters() {
    const counters = document.querySelectorAll('[data-counter]');

    counters.forEach(counter => {

        // Prevent running twice
        if (counter.dataset.animated === 'true') return;

        counter.dataset.animated = 'true';

        const target = parseFloat(counter.dataset.counter);
        const duration = parseInt(counter.dataset.duration || '800');
        const suffix = counter.dataset.suffix || '';

        animateCounter(counter, target, duration, suffix);
    });
}

// Run once when page loads
window.addEventListener('load', () => {
    runCounters();
});