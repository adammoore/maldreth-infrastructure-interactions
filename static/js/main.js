/**
 * main.js
 * Main JavaScript file for MaLDReTH Infrastructure Interactions
 */

// API Base URL
const API_BASE_URL = window.location.origin + '/api';

// Utility Functions
const utils = {
    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} Response data
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    /**
     * Show a notification message
     * @param {string} message - Message to display
     * @param {string} type - Message type (success, error, info)
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        
        const container = document.querySelector('.container');
        container.insertBefore(notification, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    },
    
    /**
     * Debounce function for search inputs
     * @param {function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Format date to readable string
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date
     */
    formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }
};

// Tool Management
const toolManager = {
    /**
     * Load tools for a specific stage
     * @param {string} stage - Stage name
     */
    async loadTools(stage) {
        try {
            const tools = await utils.apiRequest(`/tools/${stage}`);
            this.displayTools(tools);
        } catch (error) {
            utils.showNotification('Failed to load tools', 'error');
        }
    },
    
    /**
     * Display tools in the UI
     * @param {array} tools - Array of tool objects
     */
    displayTools(tools) {
        const container = document.getElementById('tools-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (tools.length === 0) {
            container.innerHTML = '<p class="text-muted">No tools found for this stage.</p>';
            return;
        }
        
        tools.forEach(tool => {
            const toolCard = document.createElement('div');
            toolCard.className = 'tool-card';
            toolCard.innerHTML = `
                <h4>${tool.name}</h4>
                <p>${tool.description || 'No description available'}</p>
                <div class="tool-meta">
                    ${tool.provider ? `<span class="tool-provider">Provider: ${tool.provider}</span>` : ''}
                    ${tool.link ? `<a href="${tool.link}" target="_blank" class="btn btn-sm btn-primary">Visit Tool</a>` : ''}
                </div>
            `;
            container.appendChild(toolCard);
        });
    },
    
    /**
     * Search tools
     * @param {string} query - Search query
     */
    async searchTools(query) {
        if (query.length < 2) return;
        
        try {
            const results = await utils.apiRequest(`/search?q=${encodeURIComponent(query)}`);
            this.displayTools(results);
        } catch (error) {
            utils.showNotification('Search failed', 'error');
        }
    }
};

// Lifecycle Visualization
const lifecycleViz = {
    /**
     * Initialize the lifecycle visualization
     */
    async init() {
        const container = document.getElementById('lifecycle-viz');
        if (!container) return;
        
        try {
            // Show loading spinner
            container.innerHTML = '<div class="text-center p-3"><div class="spinner"></div></div>';
            
            // Load lifecycle data
            const data = await utils.apiRequest('/lifecycle');
            
            // Render visualization
            this.render(data, container);
        } catch (error) {
            container.innerHTML = '<p class="text-danger">Failed to load lifecycle data</p>';
            console.error('Visualization error:', error);
        }
    },
    
    /**
     * Render the lifecycle visualization
     * @param {object} data - Lifecycle data
     * @param {HTMLElement} container - Container element
     */
    render(data, container) {
        // Clear container
        container.innerHTML = '';
        
        // Create SVG element
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', '0 0 800 600');
        
        // Add stages as circles
        const centerX = 400;
        const centerY = 300;
        const radius = 200;
        
        data.nodes.forEach((node, index) => {
            const angle = (index / data.nodes.length) * 2 * Math.PI - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            // Create group for stage
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'stage-node');
            g.setAttribute('transform', `translate(${x}, ${y})`);
            g.style.cursor = 'pointer';
            
            // Add circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', '40');
            circle.setAttribute('fill', '#2E86C1');
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '2');
            
            // Add text
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('fill', '#fff');
            text.setAttribute('font-size', '12');
            text.textContent = node.name;
            
            // Add click event
            g.addEventListener('click', () => {
                toolManager.loadTools(node.name);
                this.highlightStage(g);
            });
            
            g.appendChild(circle);
            g.appendChild(text);
            svg.appendChild(g);
        });
        
        container.appendChild(svg);
    },
    
    /**
     * Highlight selected stage
     * @param {SVGElement} element - Stage element to highlight
     */
    highlightStage(element) {
        // Remove previous highlights
        document.querySelectorAll('.stage-node circle').forEach(circle => {
            circle.setAttribute('fill', '#2E86C1');
        });
        
        // Highlight selected
        const circle = element.querySelector('circle');
        circle.setAttribute('fill', '#28B463');
    }
};

// Form Handlers
const formHandlers = {
    /**
     * Initialize form handlers
     */
    init() {
        // Tool creation form
        const toolForm = document.getElementById('tool-form');
        if (toolForm) {
            toolForm.addEventListener('submit', this.handleToolSubmit.bind(this));
        }
        
        // Search form
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            const debouncedSearch = utils.debounce((e) => {
                toolManager.searchTools(e.target.value);
            }, 300);
            
            searchInput.addEventListener('input', debouncedSearch);
        }
    },
    
    /**
     * Handle tool form submission
     * @param {Event} e - Form submit event
     */
    async handleToolSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            await utils.apiRequest('/tools', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            utils.showNotification('Tool created successfully', 'success');
            e.target.reset();
            
            // Reload tools if on the same stage
            if (data.stage_id) {
                toolManager.loadTools(data.stage_id);
            }
        } catch (error) {
            utils.showNotification('Failed to create tool', 'error');
        }
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    lifecycleViz.init();
    formHandlers.init();
    
    // Load initial data if needed
    const currentStage = document.querySelector('[data-current-stage]');
    if (currentStage) {
        toolManager.loadTools(currentStage.dataset.currentStage);
    }
    
    // Set up navigation active state
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Export for use in other scripts
window.MaLDReTH = {
    utils,
    toolManager,
    lifecycleViz,
    formHandlers
};
