document.addEventListener('DOMContentLoaded', () => {
    const auditForm = document.getElementById('audit-form');
    const urlInput = document.getElementById('url-input');
    const submitBtn = auditForm.querySelector('button');
    const statusMessage = document.getElementById('status-message');
    const auditsList = document.getElementById('audits-list');
    const resultsSection = document.getElementById('results-section');

    let pollingInterval = null;

    // Load initial audits
    fetchAudits();

    auditForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        await createAudit(url);
    });

    async function fetchAudits() {
        try {
            const response = await fetch('/api/v1/audits?limit=20');
            if (!response.ok) throw new Error('Failed to fetch audits');
            const audits = await response.json();
            renderAuditsList(audits);
        } catch (error) {
            console.error(error);
        }
    }

    async function createAudit(url) {
        try {
            setLoadingState(true);
            statusMessage.textContent = 'Starting audit...';
            statusMessage.className = 'status-message loading';
            resultsSection.classList.add('hidden');

            const response = await fetch('/api/v1/audits', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to start audit');
            }

            const data = await response.json();
            urlInput.value = ''; // clear input
            fetchAudits(); // refresh sidebar

            // Start polling
            startPolling(data.id);

        } catch (error) {
            setLoadingState(false);
            statusMessage.textContent = error.message;
            statusMessage.className = 'status-message error';
        }
    }

    function startPolling(auditId) {
        if (pollingInterval) clearInterval(pollingInterval);

        statusMessage.textContent = 'Audit in progress. This may take a minute...';

        pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/v1/audits/${auditId}`);
                if (!response.ok) throw new Error('Failed to fetch audit status');

                const audit = await response.json();

                if (audit.status === 'completed' || audit.status === 'failed') {
                    clearInterval(pollingInterval);
                    setLoadingState(false);
                    statusMessage.textContent = '';
                    fetchAudits(); // refresh sidebar to show updated status
                    renderResults(audit);
                }
            } catch (error) {
                console.error(error);
                clearInterval(pollingInterval);
                setLoadingState(false);
                statusMessage.textContent = 'Error checking audit status.';
                statusMessage.className = 'status-message error';
            }
        }, 2000);
    }

    async function fetchSingleAudit(auditId) {
        try {
            if (pollingInterval) clearInterval(pollingInterval);
            setLoadingState(false);
            statusMessage.textContent = 'Loading audit details...';
            statusMessage.className = 'status-message loading';

            const response = await fetch(`/api/v1/audits/${auditId}`);
            if (!response.ok) throw new Error('Failed to fetch audit details');

            const audit = await response.json();
            statusMessage.textContent = '';

            if (audit.status === 'pending') {
                startPolling(audit.id);
            } else {
                renderResults(audit);
            }

        } catch (error) {
            statusMessage.textContent = error.message;
            statusMessage.className = 'status-message error';
        }
    }

    function renderAuditsList(audits) {
        auditsList.innerHTML = '';
        // Sort descending by ID
        audits.sort((a, b) => b.id - a.id).forEach(audit => {
            const li = document.createElement('li');
            li.className = 'audit-item';
            li.onclick = () => fetchSingleAudit(audit.id);

            const date = new Date(audit.created_at).toLocaleString();

            li.innerHTML = `
                <div class="audit-item-url" title="${audit.url}">${audit.url}</div>
                <div class="audit-item-meta">
                    <span>${date}</span>
                    <span style="color: ${getStatusColor(audit.status)}">${audit.status}</span>
                </div>
            `;
            auditsList.appendChild(li);
        });
    }

    function renderResults(audit) {
        resultsSection.classList.remove('hidden');

        // Header
        document.getElementById('result-url').textContent = audit.url;
        const statusBadge = document.getElementById('result-status');
        statusBadge.textContent = audit.status;
        statusBadge.className = `status-badge ${audit.status}`;

        if (audit.status === 'failed') {
            statusMessage.textContent = `Audit failed: ${audit.error_message || 'Unknown error'}`;
            statusMessage.className = 'status-message error';
            return; // Don't try to render missing metrics
        }

        // Scores
        updateScoreCard('score-performance', audit.performance);
        updateScoreCard('score-accessibility', audit.accessibility);
        updateScoreCard('score-best-practices', audit.best_practices);
        updateScoreCard('score-seo', audit.seo);

        // Detailed Metrics
        document.getElementById('metric-fcp').textContent = audit.first_contentful_paint ? audit.first_contentful_paint.toFixed(1) : '--';
        document.getElementById('metric-lcp').textContent = audit.largest_contentful_paint ? audit.largest_contentful_paint.toFixed(1) : '--';
        document.getElementById('metric-cls').textContent = audit.cumulative_layout_shift ? audit.cumulative_layout_shift.toFixed(3) : '--';

        // Security Headers
        if (audit.security_checks) {
            updateSecurityRow('security-hsts', audit.security_checks.hsts_active);
            updateSecurityRow('security-csp', audit.security_checks.csp_active);
            updateSecurityRow('security-xframe', audit.security_checks.x_frame_options_active);
            updateSecurityRow('security-xcontent', audit.security_checks.x_content_type_options_active);
        }
    }

    function updateScoreCard(id, value) {
        const el = document.getElementById(id);
        if (value === null || value === undefined) {
            el.textContent = '--';
            el.className = 'score';
            return;
        }

        const score = Math.round(value);
        el.textContent = score;

        if (score >= 90) el.className = 'score good';
        else if (score >= 50) el.className = 'score average';
        else el.className = 'score poor';
    }

    function updateSecurityRow(id, isActive) {
        const el = document.getElementById(id);
        if (isActive === null || isActive === undefined) {
            el.textContent = '--';
            el.className = '';
        } else if (isActive) {
            el.textContent = 'Active';
            el.className = 'pass';
        } else {
            el.textContent = 'Missing';
            el.className = 'fail';
        }
    }

    function getStatusColor(status) {
        switch(status) {
            case 'completed': return 'var(--success-color)';
            case 'failed': return 'var(--error-color)';
            default: return 'var(--warning-color)';
        }
    }

    function setLoadingState(isLoading) {
        submitBtn.disabled = isLoading;
        urlInput.disabled = isLoading;
    }
});