/**
 * MaLDReTH Radial Visualization
 * Interactive circular visualization showing relationships between
 * lifecycle stages (center) and tools/services (outer arcs)
 * Version 2.0 - With dynamic arc coverage based on correlations
 */

class MaLDReTHRadialVisualization {
    constructor(containerId, data) {
        this.containerId = containerId;
        this.data = data;
        this.width = 1000;
        this.height = 800;
        this.centerRadius = 80;
        this.stageRadius = 180;
        this.categoryBaseRadius = 230; // Start closer to stages
        this.categoryRingSpacing = 15; // Reduced spacing to fit all arcs inside tools
        this.toolRadius = 380; // Keep tools at same radius
        this.categoryRings = 3; // Number of concentric rings for categories
        this.colors = {
            stages: d3.scaleOrdinal()
                .domain(data.stages)
                .range(d3.schemeCategory10),
            categoryStrength: d3.scaleOrdinal()
                .domain(['strong', 'standard', 'weak', 'none'])
                .range(['#ff4444', '#44ff44', '#ffff44', '#f0f0f0']),
            gorcCategories: d3.scaleOrdinal()
                .range([
                    '#2E8B57', '#3CB371', '#66CDAA', '#8FBC8F', '#98FB98',
                    '#90EE90', '#ADFF2F', '#7CFC00', '#32CD32', '#228B22',
                    '#006400', '#008000', '#00FF00', '#7FFF00', '#9AFF9A'
                ]), // Extended green variations for revised structure (up to 15 categories)
            tools: d3.scaleOrdinal()
                .range(d3.schemeSet3)
        };
        
        this.init();
    }
    
    init() {
        // Clear existing visualization
        d3.select(this.containerId).selectAll("*").remove();
        
        // Create SVG
        this.svg = d3.select(this.containerId)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        
        // Create defs element for patterns and gradients
        this.defs = this.svg.append('defs');

        // Create main group centered
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.width/2}, ${this.height/2})`);
        
        // Add zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                this.g.attr('transform',
                    `translate(${this.width/2}, ${this.height/2}) scale(${event.transform.k})`
                );
            });

        this.svg.call(this.zoom);
        
        // Create layers
        this.createCenterHub();
        this.createStageRing();
        this.createToolArcs();
        // this.createLegend(); // Commented out per user request
        this.addInteractivity();
    }
    
    calculateCategoryCoverage() {
        /**
         * Calculate which stages each GORC category covers
         * This determines the arc span for each category
         */
        this.categoryCoverage = {};
        
        this.data.gorcCategories.forEach(category => {
            const coverage = {
                stages: [],
                startAngle: null,
                endAngle: null,
                strength: 'none',
                correlationCount: 0,
                strongCount: 0
            };

            // Find all stages this category correlates with
            this.data.stages.forEach((stage, index) => {
                const correlation = this.data.correlations[category.name]?.[stage];
                if (correlation && correlation.marker && correlation.marker.trim() !== '') {
                    coverage.stages.push({
                        stage: stage,
                        index: index,
                        marker: correlation.marker,
                        description: correlation.description
                    });
                    
                    if (correlation.marker === 'XX') {
                        coverage.strongCount++;
                    }
                    coverage.correlationCount++;
                }
            });
            
            // Calculate angular coverage with support for broken arcs
            if (coverage.stages.length > 0) {
                const angleStep = (2 * Math.PI) / this.data.stages.length;


                // Sort stages by index to ensure proper grouping
                coverage.stages.sort((a, b) => a.index - b.index);

                // Group consecutive stages into runs for broken arc segments
                let spanIndices = [];
                let currentRun = [coverage.stages[0].index];

                for (let i = 1; i < coverage.stages.length; i++) {
                    const currentIndex = coverage.stages[i].index;
                    const previousIndex = coverage.stages[i-1].index;

                    // Check for adjacency, including circular adjacency (last stage to first)
                    const isAdjacent = (currentIndex - previousIndex === 1) ||
                                     (previousIndex === this.data.stages.length - 1 && currentIndex === 0);

                    if (isAdjacent) {
                        currentRun.push(currentIndex);
                    } else {
                        // Non-adjacent, so end current run and start new one
                        spanIndices.push(currentRun);
                        currentRun = [currentIndex];
                    }
                }
                spanIndices.push(currentRun);

                // Handle circular cases where first and last runs might be adjacent
                if (spanIndices.length > 1) {
                    const firstRun = spanIndices[0];
                    const lastRun = spanIndices[spanIndices.length - 1];

                    // Check if last stage of last run is adjacent to first stage of first run
                    const lastStageIndex = Math.max(...lastRun);
                    const firstStageIndex = Math.min(...firstRun);

                    if (lastStageIndex === this.data.stages.length - 1 && firstStageIndex === 0) {
                        // Merge first and last runs
                        const mergedRun = [...lastRun, ...firstRun];
                        spanIndices = [mergedRun, ...spanIndices.slice(1, -1)];
                    }
                }

                // Create arc segments for each continuous run (broken arcs)
                coverage.arcSegments = spanIndices.map(run => {
                    const startStageIndex = Math.min(...run);
                    const endStageIndex = Math.max(...run);

                    // Calculate angles to span the entire sector range
                    // Each stage is centered at (index * angleStep - PI/2)
                    // The sector for stage i spans from (i - 0.5)*angleStep to (i + 0.5)*angleStep
                    // Arc should span from start of first stage's sector to end of last stage's sector

                    // Start at the beginning of the first stage's sector (half step before its center)
                    let startAngle = ((startStageIndex - 0.5) * angleStep) - Math.PI / 2;
                    // End at the end of the last stage's sector (half step after its center)
                    let endAngle = ((endStageIndex + 0.5) * angleStep) - Math.PI / 2;

                    // For single stages, span the full stage sector
                    if (startStageIndex === endStageIndex) {
                        startAngle = ((startStageIndex - 0.5) * angleStep) - Math.PI / 2;
                        endAngle = ((startStageIndex + 0.5) * angleStep) - Math.PI / 2;
                    }

                    // Handle circular wrap-around cases
                    if (run.includes(0) && run.includes(this.data.stages.length - 1)) {
                        // This segment wraps around the circle
                        const nonWrapIndices = run.filter(idx => idx !== 0 && idx !== this.data.stages.length - 1);

                        if (nonWrapIndices.length > 0) {
                            // Find the gap and determine which side to use
                            const gap = Math.max(...nonWrapIndices) - Math.min(...nonWrapIndices);
                            if (gap < this.data.stages.length / 2) {
                                // Use the continuous section
                                startAngle = ((Math.min(...nonWrapIndices) - 0.5) * angleStep) - Math.PI / 2;
                                endAngle = ((Math.max(...nonWrapIndices) + 0.5) * angleStep) - Math.PI / 2;
                            }
                        }
                    }

                    return {
                        startAngle: startAngle,
                        endAngle: endAngle,
                        stages: run.map(idx => coverage.stages.find(s => s.index === idx))
                    };
                });

                // For backward compatibility, set primary arc to the first/longest segment
                const primarySegment = spanIndices.reduce((a, b) => a.length > b.length ? a : b);
                const startStageIndex = Math.min(...primarySegment);
                const endStageIndex = Math.max(...primarySegment);

                // Span the full sector range from start to end
                coverage.startAngle = ((startStageIndex - 0.5) * angleStep) - Math.PI / 2;
                coverage.endAngle = ((endStageIndex + 0.5) * angleStep) - Math.PI / 2;

                // Determine overall strength
                if (coverage.strongCount >= 3) {
                    coverage.strength = 'strong';
                } else if (coverage.correlationCount >= 5) {
                    coverage.strength = 'standard';
                } else if (coverage.correlationCount >= 2) {
                    coverage.strength = 'weak';
                }
            }
            
            this.categoryCoverage[category.name] = coverage;
        });
    }
    
    createCenterHub() {
        // Central MaLDReTH label
        const center = this.g.append('g')
            .attr('class', 'center-hub');
        
        // Gradient definition
        const gradient = this.defs.append('radialGradient')
            .attr('id', 'center-gradient')
            .attr('cx', '50%')
            .attr('cy', '50%')
            .attr('r', '50%');
        
        gradient.append('stop')
            .attr('offset', '0%')
            .style('stop-color', '#4a90e2')
            .style('stop-opacity', 1);
        
        gradient.append('stop')
            .attr('offset', '100%')
            .style('stop-color', '#366092')
            .style('stop-opacity', 1);
        
        center.append('circle')
            .attr('r', this.centerRadius)
            .attr('fill', 'url(#center-gradient)')
            .attr('stroke', '#fff')
            .attr('stroke-width', 3);
        
        center.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '-0.5em')
            .style('fill', 'white')
            .style('font-size', '18px')
            .style('font-weight', 'bold')
            .text('MaLDReTH');
        
        center.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '1em')
            .style('fill', 'white')
            .style('font-size', '12px')
            .text('Research Data Lifecycle');
    }
    
    createStageRing() {
        const angleStep = (2 * Math.PI) / this.data.stages.length;
        const stageGroup = this.g.append('g')
            .attr('class', 'stage-ring');
        
        // Store stage positions for later use
        this.stagePositions = {};
        
        // Create stage nodes
        const stages = stageGroup.selectAll('.stage-node')
            .data(this.data.stages)
            .enter()
            .append('g')
            .attr('class', 'stage-node')
            .attr('transform', (d, i) => {
                const angle = i * angleStep - Math.PI / 2;
                const x = Math.cos(angle) * this.stageRadius;
                const y = Math.sin(angle) * this.stageRadius;
                
                // Store position
                this.stagePositions[d] = { x, y, angle, index: i };
                
                return `translate(${x}, ${y})`;
            });
        
        // Stage circles with gradient
        stages.each(function(d, i) {
            const group = d3.select(this);
            
            // Create radial gradient for each stage
            const gradientId = `stage-gradient-${i}`;
            const gradient = group.append('defs')
                .append('radialGradient')
                .attr('id', gradientId);
            
            gradient.append('stop')
                .attr('offset', '0%')
                .style('stop-color', d3.schemeCategory10[i % 10])
                .style('stop-opacity', 0.8);
            
            gradient.append('stop')
                .attr('offset', '100%')
                .style('stop-color', d3.schemeCategory10[i % 10])
                .style('stop-opacity', 1);
            
            group.append('circle')
                .attr('r', 35)
                .attr('fill', `url(#${gradientId})`)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
                .attr('class', 'stage-circle')
                .style('cursor', 'pointer');
        });
        
        // Stage labels
        stages.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.3em')
            .style('fill', 'white')
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .style('pointer-events', 'none')
            .text(d => d.substring(0, 4).toUpperCase());
        
        // Add stage number
        stages.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '-1.5em')
            .style('fill', '#666')
            .style('font-size', '9px')
            .style('font-weight', 'bold')
            .style('pointer-events', 'none')
            .text((d, i) => i + 1);
        
        // Stage connections
        this.createStageConnections(stageGroup);
    }
    
    createStageConnections(stageGroup) {
        const angleStep = (2 * Math.PI) / this.data.stages.length;
        
        // Create curved connections between stages
        const connectionData = [];
        for (let i = 0; i < this.data.stages.length; i++) {
            const nextIndex = (i + 1) % this.data.stages.length;
            const angle1 = i * angleStep - Math.PI / 2;
            const angle2 = nextIndex * angleStep - Math.PI / 2;
            
            connectionData.push({
                source: {
                    x: Math.cos(angle1) * this.stageRadius,
                    y: Math.sin(angle1) * this.stageRadius,
                    angle: angle1
                },
                target: {
                    x: Math.cos(angle2) * this.stageRadius,
                    y: Math.sin(angle2) * this.stageRadius,
                    angle: angle2
                }
            });
        }
        
        stageGroup.selectAll('.stage-connection')
            .data(connectionData)
            .enter()
            .append('path')
            .attr('class', 'stage-connection')
            .attr('d', d => {
                const midAngle = (d.source.angle + d.target.angle) / 2;
                const midRadius = this.stageRadius * 0.85;
                const midX = Math.cos(midAngle) * midRadius;
                const midY = Math.sin(midAngle) * midRadius;
                return `M ${d.source.x},${d.source.y} Q ${midX},${midY} ${d.target.x},${d.target.y}`;
            })
            .attr('fill', 'none')
            .attr('stroke', '#ddd')
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '3,3');
    }
    
    createDynamicCategoryArcs() {
        const categoryGroup = this.g.append('g')
            .attr('class', 'category-arcs');

        // Calculate angle step for stage positioning
        const angleStep = (2 * Math.PI) / this.data.stages.length;

        // Sort categories by strength for ring assignment
        const categoriesWithCoverage = this.data.gorcCategories
            .map(category => ({
                ...category,
                coverage: this.categoryCoverage[category.name]
            }))
            .filter(cat => cat.coverage && cat.coverage.stages.length > 0)
            .sort((a, b) => {
                const strengthOrder = { 'strong': 3, 'standard': 2, 'weak': 1, 'none': 0 };
                return strengthOrder[b.coverage.strength] - strengthOrder[a.coverage.strength];
            });

        categoriesWithCoverage.forEach((category, index) => {
            const coverage = category.coverage;

            // Assign each category to its own unique ring with controlled spacing
            const categoryRadius = this.categoryBaseRadius + (index * this.categoryRingSpacing);

            // Create properly sized arcs with reduced spacing
            const innerRadius = categoryRadius - 6; // Slightly thicker for visibility
            const outerRadius = categoryRadius + 6; // Slightly thicker for visibility

            // Create arc group for this category
            const arcGroup = categoryGroup.append('g')
                .attr('class', 'category-arc-group')
                .attr('data-category', category.name);

            // Add pattern for strong correlations
            let patternId = null;
            if (coverage.strongCount >= 2) {
                patternId = `pattern-${category.name.replace(/\s/g, '-')}`;
                const pattern = this.defs.append('pattern')
                    .attr('id', patternId)
                    .attr('patternUnits', 'userSpaceOnUse')
                    .attr('width', 4)
                    .attr('height', 4);

                pattern.append('rect')
                    .attr('width', 4)
                    .attr('height', 4)
                    .attr('fill', this.colors.gorcCategories(index));

                pattern.append('path')
                    .attr('d', 'M 0,4 l 4,-4 M -1,1 l 2,-2 M 3,5 l 2,-2')
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 0.5)
                    .attr('opacity', 0.5);
            }

            // Render all arc segments (broken arcs support)
            if (coverage.arcSegments && coverage.arcSegments.length > 0) {
                coverage.arcSegments.forEach((segment, segmentIndex) => {
                    const arcGenerator = d3.arc()
                        .innerRadius(innerRadius)
                        .outerRadius(outerRadius)
                        .startAngle(segment.startAngle)
                        .endAngle(segment.endAngle)
                        .cornerRadius(2);

                    const arc = arcGroup.append('path')
                        .attr('d', arcGenerator())
                        .attr('fill', patternId ? `url(#${patternId})` : this.colors.gorcCategories(index))
                        .attr('stroke', '#fff')
                        .attr('stroke-width', 1)
                        .attr('class', 'category-arc')
                        .attr('data-category', category.name)
                        .attr('data-segment', segmentIndex)
                        .style('cursor', 'pointer')
                        .style('opacity', 0.8);
                });
            }

            // Position label at the center of the primary (longest) arc segment
            const primarySegment = coverage.arcSegments && coverage.arcSegments.length > 0
                ? coverage.arcSegments.reduce((a, b) =>
                    (b.endAngle - b.startAngle) > (a.endAngle - a.startAngle) ? b : a)
                : { startAngle: coverage.startAngle, endAngle: coverage.endAngle };

            const labelAngle = (primarySegment.startAngle + primarySegment.endAngle) / 2;
            const labelRadius = outerRadius + 18;
            const labelX = Math.cos(labelAngle) * labelRadius;
            const labelY = Math.sin(labelAngle) * labelRadius;

            // Calculate text rotation
            let textRotation = (labelAngle * 180 / Math.PI) + 90;
            if (textRotation > 90 && textRotation < 270) {
                textRotation += 180;
            }

            arcGroup.append('text')
                .attr('transform', `translate(${labelX}, ${labelY}) rotate(${textRotation})`)
                .attr('text-anchor', 'middle')
                .style('font-size', '9px')
                .style('font-weight', 'bold')
                .style('fill', '#333')
                .style('pointer-events', 'none')
                .text(category.shortName || category.name.substring(0, 10))
                .attr('class', 'category-label');

            // Add coverage indicator
            const coverageText = `${coverage.stages.length}/${this.data.stages.length}`;
            arcGroup.append('text')
                .attr('transform', `translate(${labelX}, ${labelY}) rotate(${textRotation})`)
                .attr('text-anchor', 'middle')
                .attr('dy', '1.1em')
                .style('font-size', '7px')
                .style('fill', '#666')
                .style('pointer-events', 'none')
                .text(coverageText)
                .attr('class', 'coverage-indicator');
        });
    }
    
    createToolArcs() {
        const toolGroup = this.g.append('g')
            .attr('class', 'tool-arcs');

        // First, create a continuous outer ring background
        const outerRing = d3.arc()
            .innerRadius(this.toolRadius - 35)
            .outerRadius(this.toolRadius)
            .startAngle(0)
            .endAngle(2 * Math.PI);

        toolGroup.append('path')
            .attr('d', outerRing())
            .attr('fill', '#f0f0f0')
            .attr('stroke', '#ddd')
            .attr('stroke-width', 1)
            .attr('opacity', 0.3);

        // Now place tool segments within their stage sectors
        const angleStep = (2 * Math.PI) / this.data.stages.length;

        this.data.stages.forEach((stage, stageIndex) => {
            const tools = this.data.stageTools[stage] || [];
            // Use same color scheme as stage circles
            const stageColor = d3.schemeCategory10[stageIndex % 10];

            // Calculate the stage's full sector boundaries
            // Stage circles are at: i * angleStep - Math.PI / 2
            // Adding 90 degrees (Math.PI / 2) to align tool sectors with stage circles
            const stageCenterAngle = (stageIndex * angleStep) - Math.PI / 2 + Math.PI / 2;
            const sectorStartAngle = stageCenterAngle - (angleStep / 2);
            const sectorEndAngle = stageCenterAngle + (angleStep / 2);
            const sectorWidth = sectorEndAngle - sectorStartAngle;

            // Debug logging
            console.log(`Stage ${stageIndex}: ${stage}, angle=${(stageCenterAngle * 180 / Math.PI).toFixed(1)}°, tools=${tools.length}, color index=${stageIndex % 10}`);

            // Create a colored arc for this stage's sector in the outer ring
            const stageArc = d3.arc()
                .innerRadius(this.toolRadius - 35)
                .outerRadius(this.toolRadius)
                .startAngle(sectorStartAngle)
                .endAngle(sectorEndAngle);

            toolGroup.append('path')
                .attr('d', stageArc())
                .attr('fill', stageColor)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
                .attr('opacity', tools.length > 0 ? 0.6 : 0.2)
                .attr('class', 'stage-tool-arc')
                .attr('data-stage', stage);

            // Only draw individual tool markers if there are tools
            if (tools.length > 0) {

                // Divide the sector among tools with small gaps for visual indicators
                const toolArcWidth = sectorWidth / tools.length;
                const gapWidth = toolArcWidth * 0.1;

                tools.forEach((tool, toolIndex) => {
                    const startAngle = sectorStartAngle + (toolIndex * toolArcWidth) + gapWidth;
                    const endAngle = sectorStartAngle + ((toolIndex + 1) * toolArcWidth) - gapWidth;

                    // Create small indicator markers for individual tools
                    const toolMarker = d3.arc()
                        .innerRadius(this.toolRadius - 8)
                        .outerRadius(this.toolRadius)
                        .startAngle(startAngle)
                        .endAngle(endAngle);

                    const midAngle = (startAngle + endAngle) / 2;

                    toolGroup.append('path')
                        .attr('d', toolMarker())
                        .attr('fill', stageColor)
                        .attr('stroke', '#fff')
                        .attr('stroke-width', 0.5)
                        .attr('class', 'tool-arc')
                        .attr('data-tool', tool.name)
                        .attr('data-stage', stage)
                        .attr('data-category', tool.category)
                        .style('cursor', 'pointer')
                        .style('opacity', 0.9)
                        .append('title')
                        .text(`${tool.name} (${stage})`);
                });
            }
        });
    }
    
    createConnections() {
        const connectionGroup = this.g.append('g')
            .attr('class', 'connections')
            .style('pointer-events', 'none');

        // Sort categories the same way as in createDynamicCategoryArcs for ring assignment
        const sortedCategories = this.data.gorcCategories
            .map(category => ({
                ...category,
                coverage: this.categoryCoverage[category.name]
            }))
            .filter(cat => cat.coverage && cat.coverage.stages.length > 0)
            .sort((a, b) => {
                const strengthOrder = { 'strong': 3, 'standard': 2, 'weak': 1, 'none': 0 };
                const strengthDiff = strengthOrder[b.coverage.strength] - strengthOrder[a.coverage.strength];
                if (strengthDiff !== 0) return strengthDiff;
                return b.coverage.stages.length - a.coverage.stages.length;
            });

        // Create connections from stages to their correlated GORC categories
        sortedCategories.forEach((category, index) => {
            const coverage = category.coverage;
            // Use the same radius calculation as arcs to ensure alignment
            const categoryRadius = this.categoryBaseRadius + (index * this.categoryRingSpacing);

            coverage.stages.forEach(stageInfo => {
                const stagePos = this.stagePositions[stageInfo.stage];
                if (!stagePos) return;

                // Calculate arc midpoint for this category at its specific ring
                const categoryMidAngle = (coverage.startAngle + coverage.endAngle) / 2;
                const categoryX = Math.cos(categoryMidAngle) * categoryRadius;
                const categoryY = Math.sin(categoryMidAngle) * categoryRadius;
                
                // Create ribbon connection
                const ribbon = d3.ribbon()
                    .source(() => ({
                        startAngle: stagePos.angle - 0.05,
                        endAngle: stagePos.angle + 0.05,
                        radius: this.stageRadius + 35
                    }))
                    .target(() => ({
                        startAngle: categoryMidAngle - 0.05,
                        endAngle: categoryMidAngle + 0.05,
                        radius: categoryRadius
                    }));
                
                // Create curved path with better control point based on ring position
                const controlRadius = (this.stageRadius + categoryRadius) / 2;
                const controlAngle = (stagePos.angle + categoryMidAngle) / 2;
                const controlX = Math.cos(controlAngle) * controlRadius;
                const controlY = Math.sin(controlAngle) * controlRadius;

                const path = connectionGroup.append('path')
                    .attr('d', `M ${stagePos.x},${stagePos.y} Q ${controlX},${controlY} ${categoryX},${categoryY}`)
                    .attr('fill', 'none')
                    .attr('stroke', stageInfo.marker === 'XX' ? '#ff4444' : '#44ff44')
                    .attr('stroke-width', stageInfo.marker === 'XX' ? 2 : 1)
                    .attr('stroke-opacity', 0.15)
                    .attr('class', 'connection-path')
                    .attr('data-stage', stageInfo.stage)
                    .attr('data-category', category.name)
                    .attr('data-strength', stageInfo.marker);
            });
        });
    }
    
    createLegend() {
        const legendGroup = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(-10, ${this.height - 460})`);
        
        // Background with shadow
        const legendBg = legendGroup.append('rect')
            .attr('width', 230)
            .attr('height', 270)
            .attr('fill', 'rgba(255, 255, 255, 0.95)')
            .attr('stroke', '#ddd')
            .attr('rx', 5)
            .style('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))');
        
        // Title
        legendGroup.append('text')
            .attr('x', 10)
            .attr('y', 25)
            .style('font-weight', 'bold')
            .style('font-size', '14px')
            .text('GORC Categories Legend');
        
        // Legend items - show actual GORC categories with their colors
        const items = [
            { color: '#366092', label: 'MaLDReTH Core', type: 'circle' },
            { color: '#4CAF50', label: 'Lifecycle Stages', type: 'circle' },
            ...this.data.gorcCategories.map((category, i) => ({
                color: this.colors.gorcCategories(category.name),
                label: category.shortName || category.name,
                type: 'arc'
            }))
        ];
        
        items.forEach((item, i) => {
            const y = 50 + (i * 25);
            
            if (item.type === 'circle') {
                legendGroup.append('circle')
                    .attr('cx', 20)
                    .attr('cy', y)
                    .attr('r', 8)
                    .attr('fill', item.color);
            } else {
                const arcGen = d3.arc()
                    .innerRadius(5)
                    .outerRadius(10)
                    .startAngle(0)
                    .endAngle(Math.PI);
                
                legendGroup.append('path')
                    .attr('d', arcGen())
                    .attr('transform', `translate(20, ${y})`)
                    .attr('fill', item.color);
            }
            
            legendGroup.append('text')
                .attr('x', 35)
                .attr('y', y + 4)
                .style('font-size', '12px')
                .text(item.label);
        });
        
        // Add notes about visualization structure (with adjusted spacing for more legend items)
        const structureStartY = 50 + (items.length * 25) + 20;

        legendGroup.append('text')
            .attr('x', 10)
            .attr('y', structureStartY)
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .text('Visualization Structure:');

        legendGroup.append('text')
            .attr('x', 10)
            .attr('y', structureStartY + 15)
            .style('font-size', '9px')
            .style('font-style', 'italic')
            .text('Inner: Lifecycle stages');

        legendGroup.append('text')
            .attr('x', 10)
            .attr('y', structureStartY + 28)
            .style('font-size', '9px')
            .style('font-style', 'italic')
            .text('Middle: GORC categories');

        legendGroup.append('text')
            .attr('x', 10)
            .attr('y', structureStartY + 41)
            .style('font-size', '9px')
            .style('font-style', 'italic')
            .text('Outer: Research tools');
    }
    
    addInteractivity() {
        // Enhanced tooltip
        const tooltip = d3.select('body').append('div')
            .attr('class', 'radial-tooltip')
            .style('position', 'absolute')
            .style('visibility', 'hidden')
            .style('background-color', 'rgba(0, 0, 0, 0.95)')
            .style('color', 'white')
            .style('padding', '12px')
            .style('border-radius', '8px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', '1000')
            .style('max-width', '300px')
            .style('box-shadow', '0 4px 8px rgba(0,0,0,0.3)');
        
        // Stage interaction
        this.g.selectAll('.stage-circle')
            .on('mouseenter', function(event, d) {
                const element = d3.select(this);

                // Only animate if not already scaled
                if (!element.classed('stage-hovered')) {
                    element.classed('stage-hovered', true)
                        .transition()
                        .duration(150)
                        .attr('r', 40);
                }

                tooltip.style('visibility', 'visible')
                    .html(`
                        <div style="font-weight: bold; margin-bottom: 5px;">${d}</div>
                        <div>Click to filter connections</div>
                        <div style="color: #aaa; font-size: 10px; margin-top: 5px;">
                            Stage ${d3.select(this.parentNode).datum()} in the lifecycle
                        </div>
                    `);

                // Highlight connections
                d3.selectAll('.connection-path')
                    .style('stroke-opacity', function(pathData) {
                        return d3.select(this).attr('data-stage') === d ? 0.6 : 0.05;
                    });
            })
            .on('mousemove', function(event) {
                tooltip.style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px');
            })
            .on('mouseleave', function() {
                const element = d3.select(this);
                element.classed('stage-hovered', false)
                    .transition()
                    .duration(150)
                    .attr('r', 35);

                tooltip.style('visibility', 'hidden');

                // Reset connections
                d3.selectAll('.connection-path')
                    .style('stroke-opacity', 0.2);
            })
            .on('click', function(event, d) {
                // Toggle stage focus
                const isActive = d3.select(this).classed('active');
                
                d3.selectAll('.stage-circle').classed('active', false);
                d3.select(this).classed('active', !isActive);
                
                if (!isActive) {
                    // Show only connections for this stage
                    d3.selectAll('.connection-path')
                        .style('display', function() {
                            return d3.select(this).attr('data-stage') === d ? 'block' : 'none';
                        });
                    
                    // Dim non-connected categories
                    d3.selectAll('.category-arc')
                        .style('opacity', function() {
                            const categoryName = d3.select(this).attr('data-category');
                            const hasConnection = d3.selectAll('.connection-path')
                                .filter(function() {
                                    return d3.select(this).attr('data-stage') === d && 
                                           d3.select(this).attr('data-category') === categoryName;
                                })
                                .size() > 0;
                            return hasConnection ? 0.8 : 0.2;
                        });
                } else {
                    // Show all connections
                    d3.selectAll('.connection-path')
                        .style('display', 'block');
                    
                    d3.selectAll('.category-arc')
                        .style('opacity', 0.7);
                }
            });
        
        // Category arc interaction
        this.g.selectAll('.category-arc')
            .on('mouseenter', function(event, d) {
                const categoryName = d3.select(this).attr('data-category');
                const coverage = this.categoryCoverage[categoryName];
                
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style('opacity', 1);
                
                // Build coverage details
                let coverageHtml = `<div style="font-weight: bold; margin-bottom: 8px;">${categoryName}</div>`;
                coverageHtml += `<div style="margin-bottom: 5px;">Coverage: ${coverage.stages.length} stages</div>`;
                
                if (coverage.stages.length > 0) {
                    coverageHtml += '<div style="font-size: 10px; color: #aaa; margin-top: 5px;">Connected stages:</div>';
                    coverageHtml += '<div style="font-size: 11px;">';
                    coverage.stages.forEach(s => {
                        const color = s.marker === 'XX' ? '#ff6666' : '#66ff66';
                        coverageHtml += `<span style="color: ${color}; margin-right: 5px;">${s.stage.substring(0, 4)}</span>`;
                    });
                    coverageHtml += '</div>';
                }
                
                tooltip.style('visibility', 'visible')
                    .html(coverageHtml);
                
                // Highlight related connections
                d3.selectAll('.connection-path')
                    .style('stroke-opacity', function() {
                        return d3.select(this).attr('data-category') === categoryName ? 0.6 : 0.05;
                    });
                
                // Highlight connected stages
                d3.selectAll('.stage-circle')
                    .style('stroke-width', function(d) {
                        const hasConnection = coverage.stages.some(s => s.stage === d);
                        return hasConnection ? 4 : 2;
                    })
                    .style('stroke', function(d) {
                        const connection = coverage.stages.find(s => s.stage === d);
                        if (connection) {
                            return connection.marker === 'XX' ? '#ff4444' : '#44ff44';
                        }
                        return '#fff';
                    });
            })
            .on('mousemove', function(event) {
                tooltip.style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px');
            })
            .on('mouseleave', function() {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style('opacity', 0.7);
                
                tooltip.style('visibility', 'hidden');
                
                // Reset connections
                d3.selectAll('.connection-path')
                    .style('stroke-opacity', 0.2);
                
                // Reset stage highlighting
                d3.selectAll('.stage-circle')
                    .style('stroke-width', 2)
                    .style('stroke', '#fff');
            });
        
        // Tool arc interaction
        this.g.selectAll('.tool-arc')
            .on('mouseenter', function(event) {
                const element = d3.select(this);
                const toolName = element.attr('data-tool');
                const stageName = element.attr('data-stage');
                const categoryName = element.attr('data-category');

                // Only animate if not already scaled
                if (!element.classed('hovered')) {
                    element.classed('hovered', true)
                        .transition()
                        .duration(150)
                        .style('opacity', 1)
                        .style('transform', 'scale(1.05)');
                }

                tooltip.style('visibility', 'visible')
                    .html(`
                        <div style="font-weight: bold; margin-bottom: 5px;">${toolName}</div>
                        <div style="color: #66ff66;">Stage: ${stageName}</div>
                        <div style="color: #ffff66;">Category: ${categoryName}</div>
                    `);
            })
            .on('mousemove', function(event) {
                tooltip.style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px');
            })
            .on('mouseleave', function() {
                const element = d3.select(this);
                element.classed('hovered', false)
                    .transition()
                    .duration(150)
                    .style('opacity', 0.8)
                    .style('transform', 'scale(1)');

                tooltip.style('visibility', 'hidden');
            });
        
        // Make categoryCoverage accessible to interaction functions
        const categoryCoverage = this.categoryCoverage;
        this.g.selectAll('.category-arc').each(function() {
            this.categoryCoverage = categoryCoverage;
        });
    }
    
    // Public method to highlight specific categories
    highlightCategory(categoryName) {
        // Dim all categories except the selected one
        d3.selectAll('.category-arc')
            .style('opacity', function() {
                return d3.select(this).attr('data-category') === categoryName ? 0.9 : 0.2;
            });
        
        // Show only connections for this category
        d3.selectAll('.connection-path')
            .style('stroke-opacity', function() {
                return d3.select(this).attr('data-category') === categoryName ? 0.6 : 0;
            });
    }
    
    // Public method to reset view
    resetView() {
        d3.selectAll('.category-arc').style('opacity', 0.7);
        d3.selectAll('.connection-path').style('stroke-opacity', 0.2).style('display', 'block');
        d3.selectAll('.stage-circle').classed('active', false).style('stroke-width', 2).style('stroke', '#fff');

        // Reset zoom to initial state
        if (this.zoom && this.svg) {
            this.svg.transition()
                .duration(750)
                .call(this.zoom.transform, d3.zoomIdentity);
        }
    }
}

// Initialize visualization when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Fetch data from API
    fetch('/api/radial-visualization-data')
        .then(response => response.json())
        .then(data => {
            window.radialViz = new MaLDReTHRadialVisualization('#radial-viz', data);
            
            // Add control buttons with proper functionality
            document.getElementById('reset-viz').addEventListener('click', () => {
                console.log('Reset View clicked');
                // Reset all visual states to default
                d3.selectAll('.category-arc-group').style('opacity', 0.8);
                d3.selectAll('.category-arc').style('opacity', 0.8);
                d3.selectAll('.connection-path')
                    .style('display', 'block')
                    .style('stroke-opacity', 0.15);
                d3.selectAll('.stage-circle')
                    .classed('active', false)  // Remove active class
                    .style('stroke-width', 2)
                    .style('stroke', '#fff');   // Reset to white border

                // Reset zoom to initial state
                if (window.radialViz && window.radialViz.zoom && window.radialViz.svg) {
                    window.radialViz.svg.transition()
                        .duration(750)
                        .call(window.radialViz.zoom.transform, d3.zoomIdentity);
                }

                // Reset all filter buttons
                const filterContainer = document.getElementById('category-filters');
                if (filterContainer) {
                    filterContainer.querySelectorAll('button').forEach(b => {
                        if (b.getAttribute('data-category')) {
                            b.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
                        } else if (b.textContent === 'Show All') {
                            b.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
                        }
                    });
                }
            });

            document.getElementById('show-all-connections').addEventListener('click', () => {
                console.log('Show All clicked');
                // Reset stage selections
                d3.selectAll('.stage-circle').classed('active', false);

                // Show all connections and arcs
                d3.selectAll('.connection-path')
                    .style('display', 'block')
                    .style('stroke-opacity', 0.2); // Standard visibility
                d3.selectAll('.category-arc-group')
                    .style('opacity', 0.8);
                d3.selectAll('.category-arc')
                    .style('opacity', 0.8);
            });

            document.getElementById('hide-connections').addEventListener('click', () => {
                console.log('Hide Lines clicked');
                d3.selectAll('.connection-path')
                    .style('display', 'none');
            });
            
            // Add category filter buttons - completely fresh approach with event delegation
            const filterContainer = document.getElementById('category-filters');
            if (filterContainer) {
                console.log('Filter container found:', filterContainer);

                // Clear any existing buttons and events
                filterContainer.innerHTML = '';

                // Use all GORC categories that have correlations
                const validCategories = data.gorcCategories.filter(category =>
                    data.correlations[category.name]
                );

                console.log('Creating filter buttons for:', validCategories.map(c => c.shortName));

                // Use event delegation with better debugging
                filterContainer.addEventListener('click', function(event) {
                    console.log('Click event on container:', event.target);

                    if (event.target.tagName === 'BUTTON') {
                        event.preventDefault();
                        event.stopPropagation();

                        const categoryName = event.target.getAttribute('data-category');
                        console.log('Button clicked. Category:', categoryName, 'Text:', event.target.textContent);

                        if (categoryName) {
                            console.log('Processing category filter for:', categoryName);

                            // Reset all category buttons
                            filterContainer.querySelectorAll('button[data-category]').forEach(b => {
                                b.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
                            });

                            // Set this button to active
                            event.target.className = 'btn btn-sm btn-primary me-1 mb-1';

                            // Call filter function
                            console.log('Calling filterCategoryArcs with:', categoryName);
                            filterCategoryArcs(categoryName);

                        } else if (event.target.textContent.trim() === 'Show All') {
                            console.log('Processing Show All');

                            // Reset all category buttons
                            filterContainer.querySelectorAll('button[data-category]').forEach(b => {
                                b.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
                            });
                            event.target.className = 'btn btn-sm btn-secondary me-1 mb-1';

                            console.log('Calling resetCategoryView');
                            resetCategoryView();
                        }
                    }
                }, true); // Use capture phase

                // Create buttons with simpler approach
                validCategories.forEach((category, index) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
                    btn.textContent = category.shortName;
                    btn.setAttribute('data-category', category.name);
                    btn.setAttribute('title', category.name); // Tooltip
                    filterContainer.appendChild(btn);
                });

                // Add reset button
                const resetBtn = document.createElement('button');
                resetBtn.type = 'button';
                resetBtn.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
                resetBtn.textContent = 'Show All';
                resetBtn.setAttribute('title', 'Reset all filters');
                filterContainer.appendChild(resetBtn);

                console.log('Buttons created. Total buttons:', filterContainer.children.length);
            } else {
                console.error('Filter container not found!');
            }

            // Simple filter function for categories
            function filterCategoryArcs(categoryName) {
                console.log('Filtering for category:', categoryName);

                // Debug: Check what arcs exist
                const allArcs = d3.selectAll('.category-arc');
                console.log('Total arcs found:', allArcs.size());
                allArcs.each(function() {
                    console.log('Arc data-category:', d3.select(this).attr('data-category'));
                });

                // Dim all category arc groups
                d3.selectAll('.category-arc-group').style('opacity', 0.1);

                // Highlight selected category arc group
                const matchingGroups = d3.selectAll('.category-arc-group')
                    .filter(function() {
                        const dataCategory = d3.select(this).attr('data-category');
                        console.log('Checking group data-category:', dataCategory, 'vs', categoryName);
                        return dataCategory === categoryName;
                    })
                    .style('opacity', 0.9);

                console.log('Matching groups found:', matchingGroups.size());

                // Hide all connections except for this category
                d3.selectAll('.connection-path').style('display', 'none');
                d3.selectAll('.connection-path')
                    .filter(function() {
                        return d3.select(this).attr('data-category') === categoryName;
                    })
                    .style('display', 'block')
                    .style('stroke-opacity', 0.6);
            }

            // Simple reset function
            function resetCategoryView() {
                console.log('Resetting category view');
                d3.selectAll('.category-arc-group').style('opacity', 0.7);
                d3.selectAll('.connection-path')
                    .style('display', 'block')
                    .style('stroke-opacity', 0.15);
            }
        })
        .catch(error => {
            console.error('Error loading visualization data:', error);
        });
});
