// Chart generation and management functionality

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.maxCharts = 4;
        this.currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'dark';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Listen for theme changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-bs-theme') {
                    this.currentTheme = document.documentElement.getAttribute('data-bs-theme');
                    this.updateAllChartsTheme();
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-bs-theme']
        });
    }

    getPlotlyConfig() {
        return {
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
            displaylogo: false,
            responsive: true,
            toImageButtonOptions: {
                format: 'png',
                filename: 'chart',
                height: 500,
                width: 700,
                scale: 1
            }
        };
    }

    getPlotlyLayout(title = '') {
        const isDark = this.currentTheme === 'dark';
        
        return {
            title: {
                text: title,
                font: {
                    color: isDark ? '#ffffff' : '#333333',
                    size: 16
                }
            },
            template: isDark ? 'plotly_dark' : 'plotly_white',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: isDark ? '#ffffff' : '#333333',
                family: '"Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif'
            },
            xaxis: {
                gridcolor: isDark ? '#444444' : '#e6e6e6',
                tickfont: { color: isDark ? '#ffffff' : '#333333' },
                titlefont: { color: isDark ? '#ffffff' : '#333333' }
            },
            yaxis: {
                gridcolor: isDark ? '#444444' : '#e6e6e6',
                tickfont: { color: isDark ? '#ffffff' : '#333333' },
                titlefont: { color: isDark ? '#ffffff' : '#333333' }
            },
            legend: {
                font: { color: isDark ? '#ffffff' : '#333333' }
            },
            margin: { t: 50, l: 50, r: 50, b: 50 },
            height: 400,
            autosize: true
        };
    }

    createChart(containerId, data, chartType, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with id ${containerId} not found`);
            return null;
        }

        let plotData = [];
        let layout = this.getPlotlyLayout(options.title || '');

        try {
            switch (chartType) {
                case 'bar':
                    plotData = this.createBarChart(data, options);
                    break;
                case 'line':
                    plotData = this.createLineChart(data, options);
                    break;
                case 'pie':
                    plotData = this.createPieChart(data, options);
                    break;
                case 'scatter':
                    plotData = this.createScatterChart(data, options);
                    break;
                case 'box':
                    plotData = this.createBoxChart(data, options);
                    break;
                case 'histogram':
                    plotData = this.createHistogram(data, options);
                    break;
                case 'heatmap':
                    plotData = this.createHeatmap(data, options);
                    break;
                default:
                    throw new Error(`Unsupported chart type: ${chartType}`);
            }

            // Create the plot
            Plotly.newPlot(containerId, plotData, layout, this.getPlotlyConfig());
            
            // Store chart reference
            this.charts.set(containerId, {
                type: chartType,
                data: plotData,
                layout: layout,
                options: options
            });

            return containerId;

        } catch (error) {
            console.error('Error creating chart:', error);
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error creating chart: ${error.message}
                </div>
            `;
            return null;
        }
    }

    createBarChart(data, options) {
        const { x, y, color } = options;
        
        return [{
            x: data.map(row => row[x]),
            y: data.map(row => row[y]),
            type: 'bar',
            marker: {
                color: color || (this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3'),
                opacity: 0.8
            },
            name: `${y} by ${x}`
        }];
    }

    createLineChart(data, options) {
        const { x, y, color } = options;
        
        return [{
            x: data.map(row => row[x]),
            y: data.map(row => row[y]),
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: color || (this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3'),
                width: 3
            },
            marker: {
                size: 6,
                color: color || (this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3')
            },
            name: `${y} over ${x}`
        }];
    }

    createPieChart(data, options) {
        const { x, values } = options;
        
        // Count occurrences or use provided values
        const counts = {};
        if (values) {
            data.forEach(row => {
                counts[row[x]] = row[values];
            });
        } else {
            data.forEach(row => {
                counts[row[x]] = (counts[row[x]] || 0) + 1;
            });
        }

        const labels = Object.keys(counts);
        const vals = Object.values(counts);

        return [{
            labels: labels,
            values: vals,
            type: 'pie',
            hole: 0.3,
            marker: {
                colors: this.generateColors(labels.length)
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        }];
    }

    createScatterChart(data, options) {
        const { x, y, color, size } = options;
        
        return [{
            x: data.map(row => row[x]),
            y: data.map(row => row[y]),
            type: 'scatter',
            mode: 'markers',
            marker: {
                size: size ? data.map(row => Math.max(5, Math.min(20, row[size] / 10))) : 8,
                color: color ? data.map(row => row[color]) : (this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3'),
                colorscale: 'Viridis',
                showscale: !!color,
                opacity: 0.7,
                line: {
                    width: 1,
                    color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                }
            },
            name: `${y} vs ${x}`
        }];
    }

    createBoxChart(data, options) {
        const { x, y } = options;
        
        if (x && y) {
            // Grouped box plot
            const groups = {};
            data.forEach(row => {
                if (!groups[row[x]]) groups[row[x]] = [];
                groups[row[x]].push(row[y]);
            });

            return Object.keys(groups).map(group => ({
                y: groups[group],
                type: 'box',
                name: group,
                boxpoints: 'outliers'
            }));
        } else {
            // Single box plot
            const column = y || x;
            return [{
                y: data.map(row => row[column]),
                type: 'box',
                name: column,
                boxpoints: 'outliers',
                marker: {
                    color: this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3'
                }
            }];
        }
    }

    createHistogram(data, options) {
        const { x } = options;
        
        return [{
            x: data.map(row => row[x]),
            type: 'histogram',
            marker: {
                color: this.currentTheme === 'dark' ? '#4FC3F7' : '#2196F3',
                opacity: 0.7,
                line: {
                    color: this.currentTheme === 'dark' ? '#ffffff' : '#000000',
                    width: 1
                }
            },
            name: `Distribution of ${x}`
        }];
    }

    createHeatmap(data, options) {
        const { matrix, xLabels, yLabels } = options;
        
        return [{
            z: matrix,
            x: xLabels,
            y: yLabels,
            type: 'heatmap',
            colorscale: 'RdYlBu',
            reversescale: true,
            showscale: true
        }];
    }

    generateColors(count) {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    updateAllChartsTheme() {
        this.charts.forEach((chartInfo, containerId) => {
            this.updateChartTheme(containerId);
        });
    }

    updateChartTheme(containerId) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) return;

        const newLayout = this.getPlotlyLayout(chartInfo.layout.title?.text || '');
        
        Plotly.relayout(containerId, newLayout);
    }

    removeChart(containerId) {
        if (this.charts.has(containerId)) {
            Plotly.purge(containerId);
            this.charts.delete(containerId);
        }
    }

    exportChart(containerId, format = 'png') {
        if (!this.charts.has(containerId)) {
            console.error(`Chart ${containerId} not found`);
            return;
        }

        const options = {
            format: format,
            width: 800,
            height: 600,
            filename: `chart_${Date.now()}`
        };

        Plotly.downloadImage(containerId, options);
    }

    resizeChart(containerId) {
        if (this.charts.has(containerId)) {
            Plotly.Plots.resize(containerId);
        }
    }

    resizeAllCharts() {
        this.charts.forEach((chartInfo, containerId) => {
            this.resizeChart(containerId);
        });
    }

    getChartCount() {
        return this.charts.size;
    }

    clearAllCharts() {
        this.charts.forEach((chartInfo, containerId) => {
            this.removeChart(containerId);
        });
    }
}

// Initialize chart manager
let chartManager;

document.addEventListener('DOMContentLoaded', function() {
    chartManager = new ChartManager();

    // Handle window resize
    window.addEventListener('resize', function() {
        if (chartManager) {
            chartManager.resizeAllCharts();
        }
    });
});

// Export for global use
window.ChartManager = ChartManager;
window.chartManager = chartManager;

// Utility functions for chart generation
function createQuickChart(containerId, type, data, options = {}) {
    if (!window.chartManager) {
        console.error('Chart manager not initialized');
        return null;
    }
    
    return window.chartManager.createChart(containerId, data, type, options);
}

function removeChart(containerId) {
    if (window.chartManager) {
        window.chartManager.removeChart(containerId);
    }
}

function exportChart(containerId, format = 'png') {
    if (window.chartManager) {
        window.chartManager.exportChart(containerId, format);
    }
}

// Analytics chart helpers
function createCorrelationHeatmap(containerId, correlationMatrix) {
    const matrix = [];
    const labels = Object.keys(correlationMatrix);
    
    labels.forEach(row => {
        const rowData = [];
        labels.forEach(col => {
            rowData.push(correlationMatrix[row][col] || 0);
        });
        matrix.push(rowData);
    });

    return createQuickChart(containerId, 'heatmap', [], {
        matrix: matrix,
        xLabels: labels,
        yLabels: labels,
        title: 'Correlation Matrix'
    });
}

function createDistributionChart(containerId, data, column) {
    return createQuickChart(containerId, 'histogram', data, {
        x: column,
        title: `Distribution of ${column}`
    });
}

function createTrendChart(containerId, data, xColumn, yColumn) {
    return createQuickChart(containerId, 'line', data, {
        x: xColumn,
        y: yColumn,
        title: `${yColumn} Trend over ${xColumn}`
    });
}

function createCategoryChart(containerId, data, column) {
    return createQuickChart(containerId, 'pie', data, {
        x: column,
        title: `Distribution of ${column}`
    });
}

// Export functions for use in other scripts
window.createQuickChart = createQuickChart;
window.removeChart = removeChart;
window.exportChart = exportChart;
window.createCorrelationHeatmap = createCorrelationHeatmap;
window.createDistributionChart = createDistributionChart;
window.createTrendChart = createTrendChart;
window.createCategoryChart = createCategoryChart;
